"""Open a headed browser on a persistent profile so the USER logs in themselves (password/OTP); exits when they close the window.

Usage: login.py <url> --profile <dir> [--fill "css=value" ...] [--press-enter]
--fill only pre-fills non-secret fields such as the email; never pass passwords or OTPs.
"""
import argparse
from playwright.sync_api import sync_playwright
from common import resolve_url, open_context

ap = argparse.ArgumentParser()
ap.add_argument("url")
ap.add_argument("--profile", required=True)
ap.add_argument("--fill", action="append", default=[], help='"css=value", non-secret fields only')
ap.add_argument("--press-enter", action="store_true", help="press Enter in the last filled field (e.g. request an OTP)")
args = ap.parse_args()

with sync_playwright() as p:
    _, ctx = open_context(p, args.profile, headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(resolve_url(args.url), wait_until="domcontentloaded")
    field = None
    for spec in args.fill:
        css, value = spec.split("=", 1)
        field = page.locator(css).first
        field.fill(value)
    if field is not None and args.press_enter:
        field.press("Enter")
    print("WAITING: log in inside the browser window, then close the window.", flush=True)
    ctx.wait_for_event("close", timeout=0)
    print("PROFILE_SAVED", args.profile, flush=True)
