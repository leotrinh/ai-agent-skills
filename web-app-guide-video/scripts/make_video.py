"""Render a narrated, subtitled guide video from a guide script JSON: edge-tts voice -> Playwright recording -> ffmpeg MP4.

Usage: make_video.py <guide.json> [--profile <dir>] [--out <dir>]
Schema: references/guide-script-schema.md. Also writes <out>/contact-sheet.png for visual review.
"""
import argparse, asyncio, json, re, shutil, subprocess, time
from pathlib import Path
from urllib.parse import urljoin
import edge_tts
from playwright.sync_api import sync_playwright
from common import resolve_url, open_context

ASSETS = Path(__file__).resolve().parent.parent / "assets"
OVERLAY_CSS = (ASSETS / "overlay.css").read_text(encoding="utf-8")
OVERLAY_JS = (ASSETS / "overlay.js").read_text(encoding="utf-8").split("\n", 1)[1]
SETTLE_MS = 1300
TAIL_MS = 700
SUB_STYLE = "FontName=Arial,FontSize=13,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,BorderStyle=4,Outline=0,MarginV=18"


async def synth(text, voice, rate, mp3):
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="SentenceBoundary")
    cues = []
    with open(mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                cues.append({"start": chunk["offset"] / 1e7, "end": (chunk["offset"] + chunk["duration"]) / 1e7, "text": chunk["text"]})
    return cues


def media_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def make_audio(guide, build):
    for i, s in enumerate(guide["steps"]):
        s["mp3"] = build / f"{i:02}.mp3"
        s["cues"] = asyncio.run(synth(s["say"], guide["voice"], guide.get("rate", "+0%"), s["mp3"]))
        s["dur"] = media_duration(s["mp3"])


def locate(page, spec):
    if isinstance(spec, str):
        return page.get_by_text(spec, exact=True).locator("visible=true").first
    if "css" in spec:
        return page.locator(spec["css"]).locator("visible=true").first
    scope = page.locator(spec["within"]) if "within" in spec else page
    return scope.get_by_text(spec["text"], exact=True).locator("visible=true").first


def ripple(page, el):
    box = el.bounding_box()
    if box:
        page.evaluate("([x, y]) => { const d = document.createElement('div'); d.className = 'gv-ripple'; d.style.left = x + 'px';"
                      " d.style.top = y + 'px'; document.body.appendChild(d); setTimeout(() => d.remove(), 800); }",
                      [box["x"] + min(40, box["width"] / 2), box["y"] + box["height"] / 2])


def run_action(page, action, base_url):
    kind, arg = next(iter(action.items()))
    if kind == "click":
        el = locate(page, arg)
        ripple(page, el)
        el.click()
    elif kind == "hover":
        locate(page, arg).hover()
    elif kind == "type":
        locate(page, arg).fill(arg["value"])
    elif kind == "goto":
        page.goto(urljoin(base_url, arg) if arg.startswith("/") else resolve_url(arg))
    elif kind == "scroll":
        page.mouse.wheel(0, arg)
    elif kind == "wait":
        page.wait_for_timeout(arg)
    else:
        raise ValueError(f"unknown action {kind}")
    page.wait_for_load_state("networkidle")


def apply_blur(page, blur):
    selectors = ["table tbody"] if blur is True else (blur or [])
    page.evaluate("""sels => { document.querySelectorAll('.gv-blur').forEach(e => e.classList.remove('gv-blur'));
      sels.forEach(s => document.querySelectorAll(s).forEach(e => e.classList.add('gv-blur')));
      document.documentElement.classList.toggle('gv-blur-on', sels.length > 0); }""", selectors)


def record(guide, build, profile):
    vid_dir = build / "raw"
    shutil.rmtree(vid_dir, ignore_errors=True)
    w, h = guide.get("viewport", [1600, 900])
    url = resolve_url(guide["url"])
    with sync_playwright() as p:
        browser, ctx = open_context(p, profile, viewport=(w, h), record_video_dir=str(vid_dir), record_video_size={"width": w, "height": h})
        page = ctx.new_page()
        t0 = time.monotonic()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(800)
        for s in guide["steps"]:
            page.evaluate("() => document.querySelectorAll('#gv-frame,#gv-pill').forEach(e => e.remove())")
            for action in s.get("actions", []):
                run_action(page, action, url)
            page.wait_for_timeout(SETTLE_MS)
            page.evaluate("css => document.getElementById('gv-style') || Object.assign(document.head.appendChild("
                          "document.createElement('style')), {id: 'gv-style', textContent: css})", OVERLAY_CSS)
            apply_blur(page, s.get("blur"))
            if not page.evaluate(OVERLAY_JS, [s.get("target"), s.get("badge", ""), s.get("label", ""), s.get("title", "")]):
                print("WARN target not found:", s.get("title"), s.get("target"))
            s["t"] = time.monotonic() - t0
            page.wait_for_timeout(int(s["dur"] * 1000) + TAIL_MS)
        page.close()
        video = page.video.path()
        ctx.close()
        if browser:
            browser.close()
    return Path(video)


def srt_time(sec):
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def render(guide, build, raw, out_file):
    steps = guide["steps"]
    lead_in = max(steps[0]["t"] - 0.5, 0)
    lines, n = [], 0
    for s in steps:
        s["t"] -= lead_in
        for c in s["cues"]:
            n += 1
            lines += [str(n), f"{srt_time(s['t'] + c['start'])} --> {srt_time(s['t'] + c['end'])}", c["text"], ""]
    (build / "subs.srt").write_text("\n".join(lines), encoding="utf-8")

    inputs, delays = ["-ss", f"{lead_in:.3f}", "-i", str(raw)], []
    for i, s in enumerate(steps, start=1):
        inputs += ["-i", str(s["mp3"])]
        ms = int(s["t"] * 1000)
        delays.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(1, len(steps) + 1))
    graph = ";".join(delays) + f";{mix}amix=inputs={len(steps)}:normalize=0[aout];[0:v]subtitles=subs.srt:force_style='{SUB_STYLE}'[vout]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(out_file.resolve())],
                   cwd=build, check=True)


def contact_sheet(video, sheet):
    every = max(media_duration(video) / 12, 1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vf", f"fps=1/{every:.2f},scale=800:-1,tile=3x4",
                    "-frames:v", "1", str(sheet)], check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("guide")
    ap.add_argument("--profile")
    ap.add_argument("--out")
    args = ap.parse_args()
    guide_path = Path(args.guide).resolve()
    guide = json.loads(guide_path.read_text(encoding="utf-8"))
    out = Path(args.out) if args.out else guide_path.parent
    build = out / "build"
    build.mkdir(parents=True, exist_ok=True)
    make_audio(guide, build)
    print("audio ok, speech", round(sum(s["dur"] for s in guide["steps"]), 1), "s", flush=True)
    raw = record(guide, build, args.profile)
    out_file = out / guide.get("output", re.sub(r"[^a-z0-9]+", "-", guide_path.stem.lower()) + ".mp4")
    render(guide, build, raw, out_file)
    contact_sheet(out_file, out / "contact-sheet.png")
    print("DONE", out_file, round(media_duration(out_file), 1), "s")
