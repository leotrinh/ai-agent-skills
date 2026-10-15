"""Read-only discovery: optionally click a path of visible labels, then save screenshot, visible text and nav labels.

Usage: snapshot.py <url> --out <dir> [--profile <dir>] [--click "Label" ...] [--name slug]
Clicks only what you list; list navigation labels only, never Save/Submit/Delete-type controls on real data.
"""
import argparse, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import resolve_url, open_context

ap = argparse.ArgumentParser()
ap.add_argument("url")
ap.add_argument("--out", required=True)
ap.add_argument("--profile")
ap.add_argument("--click", action="append", default=[])
ap.add_argument("--name")
args = ap.parse_args()

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
slug = args.name or (re.sub(r"[^a-z0-9]+", "-", (args.click[-1] if args.click else "home").lower()).strip("-") or "page")

NAV_JS = """() => [...document.querySelectorAll('nav a, nav button, aside a, aside button, [role=navigation] a, [role=navigation] button, [role=tab]')]
  .filter(e => e.offsetParent).map(e => e.innerText.trim().replace(/\\s+/g, ' ')).filter(Boolean)"""

with sync_playwright() as p:
    browser, ctx = open_context(p, args.profile)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(resolve_url(args.url), wait_until="networkidle")
    for label in args.click:
        page.get_by_text(label, exact=True).locator("visible=true").first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1200)
    page.screenshot(path=out / f"{slug}.png")
    main = page.locator("main")
    text = main.first.inner_text() if main.count() else page.inner_text("body")
    (out / f"{slug}.txt").write_text(text[:4000], encoding="utf-8")
    (out / f"{slug}.nav.json").write_text(json.dumps(page.evaluate(NAV_JS), ensure_ascii=False), encoding="utf-8")
    print("saved", out / slug, "url=", page.url)
    ctx.close()
    if browser:
        browser.close()
