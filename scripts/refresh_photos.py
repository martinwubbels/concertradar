#!/usr/bin/env python3
"""Update public official concert-page image URLs. No third-party dependencies.

Only links images that venues already publish as their sharing preview.
Does not copy copyrighted photo files. Failed checks preserve previous images.
Concert discovery and ticket availability are NOT inferred by this script.
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/concerts.json"
PHOTOS = ROOT / "data/photos.json"
HEADERS = {"User-Agent": "ConcertRadar/1.0 (personal concert calendar; contact via repository)", "Accept": "text/html,application/xhtml+xml"}
MAX_HTML = 400_000
TIMEOUT = 12

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.title = ""
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "meta":
            return
        x = {k.lower(): v for k, v in attrs if k and v}
        key = (x.get("property") or x.get("name") or "").lower()
        if key in ("og:image", "og:image:url", "twitter:image", "twitter:image:src"):
            if x.get("content"):
                self.images.append(x["content"])
        if key in ("og:title", "twitter:title") and x.get("content"):
            self.title = x["content"]

def safe_url(value):
    try:
        u = urllib.parse.urlparse(value)
        return u.scheme == "https" and bool(u.hostname) and not (u.username or u.password)
    except ValueError:
        return False

def event_photo(url, artist):
    if not safe_url(url):
        return None
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        if "html" not in response.headers.get("Content-Type", "").lower():
            return None
        html = response.read(MAX_HTML).decode("utf-8", errors="replace")
        final_url = response.geturl()
    parser = MetaParser()
    parser.feed(html)
    host = urllib.parse.urlparse(final_url).hostname or ""
    for image in parser.images:
        image = urllib.parse.urljoin(final_url, image)
        if safe_url(image) and not any(word in image.lower() for word in ("placeholder", "default-image", "blank.gif")):
            # No claim of identity verification: credit/source is preserved.
            return {"url": image, "source_url": final_url, "source_host": host, "title": parser.title, "checked_at": datetime.now(timezone.utc).isoformat()}
    return None

def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    old = json.loads(PHOTOS.read_text(encoding="utf-8")) if PHOTOS.exists() else {}
    photos = old.get("photos") or {}
    fresh = 0
    checked = 0
    # Preserve previously known images, but never map a generic venue home page to the wrong act.
    for event in catalog.get("events", []):
        event_id = event.get("id")
        url = event.get("url", "")
        if not event_id or not safe_url(url):
            continue
        parsed = urllib.parse.urlparse(url)
        if parsed.path.strip("/") in ("", "programma", "agenda", "tour"):
            continue
        checked += 1
        try:
            record = event_photo(url, event.get("name", ""))
            if record:
                photos[event_id] = record
                fresh += 1
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            print(f"Skipped {event_id}: {exc}")
        time.sleep(0.25)
    out = {"schema_version": 1, "updated_at": datetime.now(timezone.utc).isoformat(), "photos": photos, "checked": checked, "found_this_run": fresh}
    PHOTOS.parent.mkdir(parents=True, exist_ok=True)
    PHOTOS.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Checked {checked} event pages; found {fresh} share images; retained {len(photos)} total records.")

if __name__ == "__main__":
    main()
