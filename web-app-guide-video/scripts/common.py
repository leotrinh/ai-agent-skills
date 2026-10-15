"""Shared browser helpers: resolve URL-or-file targets and open a (persistent-profile) Playwright context."""
from pathlib import Path


def resolve_url(target):
    """Accept http(s) URLs or a local HTML prototype path."""
    if target.startswith(("http://", "https://", "file://")):
        return target
    return Path(target).resolve().as_uri()


def open_context(p, profile=None, headless=True, viewport=(1600, 900), **kwargs):
    """Persistent profile keeps the user's login between runs; no profile means a clean context (prototypes)."""
    vp = {"width": viewport[0], "height": viewport[1]}
    if profile:
        return None, p.chromium.launch_persistent_context(str(profile), headless=headless, viewport=vp, **kwargs)
    browser = p.chromium.launch(headless=headless)
    return browser, browser.new_context(viewport=vp, **kwargs)
