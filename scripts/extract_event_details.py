#!/usr/bin/env python3
"""Extract event metadata from discovered official URLs, WITHOUT updating concerts.

JSON-LD schema.org MusicEvent/Event provides names/dates/venues/offers.
Other pages may omit fields; these stay unverified. Never invent availability.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/discovery-candidates.json"
CATALOG = ROOT / "data/concerts.json"
OUT = ROOT / "data/event-review.json"
MAX_PAGES = 100
HEADERS = {"User-Agent": "ConcertRadar/1.0 personal music calendar", "Accept": "text/html,application/xhtml+xml"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.in_jsonld = False
        self.buf = []
        self.meta = {}
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag.lower() == "script" and d.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.buf = []
        if tag.lower() == "meta":
            key = (d.get("property") or d.get("name") or "").lower()
            if key and d.get("content") and key not in self.meta:
                self.meta[key] = d["content"]
    def handle_data(self, value):
        if self.in_jsonld:
            self.buf.append(value)
    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.in_jsonld:
            self.scripts.append("".join(self.buf))
            self.in_jsonld = False
            self.buf = []

def walk(x):
    if isinstance(x, list):
        for v in x:
            yield from walk(v)
    elif isinstance(x, dict):
        if "@graph" in x:
            yield from walk(x["@graph"])
        yield x

def pick_name(x):
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        return x.get("name") or ""
    if isinstance(x, list):
        return ", ".join(filter(None, (pick_name(v) for v in x)))
    return ""

def parsed_event(obj):
    typ = obj.get("@type", "")
    types = typ if isinstance(typ, list) else [typ]
    if not any(t in ("Event", "MusicEvent", "Festival", "TheaterEvent") for t in types):
        return None
    date = str(obj.get("startDate", ""))[:10]
    if not DATE.match(date):
        return None
    location = obj.get("location") or {}
    loc = location[0] if isinstance(location, list) and location else location
    venue = pick_name(loc)
    address = loc.get("address", {}) if isinstance(loc, dict) else {}
    city = address.get("addressLocality", "") if isinstance(address, dict) else ""
    offers = obj.get("offers") or {}
    if isinstance(offers, list):
        offers = next((x for x in offers if isinstance(x, dict)), {})
    price = offers.get("price") if isinstance(offers, dict) else None
    try:
        price = float(str(price).replace(",", ".")) if price is not None else None
    except (ValueError, TypeError):
        price = None
    if price is not None and not 0 <= price <= 10000:
        price = None
    status_raw = offers.get("availability", "") if isinstance(offers, dict) else ""
    status = str(status_raw).rsplit("/", 1)[-1] if status_raw else None
    return {"name": obj.get("name") or "", "date": date, "venue": venue, "city": city,
            "performer": pick_name(obj.get("performer")),
            "description": str(obj.get("description") or "")[:1200], "price": price,
            "currency": offers.get("priceCurrency") if isinstance(offers, dict) else None,
            "availability": status, "event_type": types, "schema_url": obj.get("url")}

def read_page(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=9) as response:
        if "html" not in response.headers.get("Content-Type", "").lower():
            return [], "not_html"
        html = response.read(750_000).decode("utf-8", "replace")
    m = Metadata()
    m.feed(html)
    found = []
    for raw in m.scripts:
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        for item in walk(data):
            event = parsed_event(item)
            if event:
                found.append(event)
    return found, None

def main():
    discover = json.loads(INPUT.read_text(encoding="utf-8"))
    known = json.loads(CATALOG.read_text(encoding="utf-8")).get("events", [])
    known_urls = {e.get("url", "").rstrip("/") for e in known}
    candidates = [e for e in discover.get("candidates", []) if e.get("review_priority") != "low_nonmusic"]
    # Prevent one large venue crowding out smaller stages completely.
    groups = {}
    for candidate in candidates:
        groups.setdefault(candidate.get("venue", "unknown"), []).append(candidate)
    try:
        previous = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = {}
    previous_cursor = previous.get("cursor_by_venue") or {}
    # Start where each venue's previous extraction left off. This avoids
    # rereading the same first five events forever on large agenda pages.
    totals = {name: len(items) for name, items in groups.items()}
    for name, items in groups.items():
        offset = int(previous_cursor.get(name, 0) or 0) % len(items)
        groups[name] = items[offset:] + items[:offset]
    selected_by_venue = {}
    selected = []
    while len(selected) < MAX_PAGES and any(groups.values()):
        for group in groups.values():
            if group and len(selected) < MAX_PAGES:
                selected.append(group.pop(0))
                name = selected[-1].get("venue", "unknown")
                selected_by_venue[name] = selected_by_venue.get(name, 0) + 1
    next_cursor = {
        name: (int(previous_cursor.get(name, 0) or 0) + selected_by_venue.get(name, 0)) % size
        for name, size in totals.items() if size
    }
    results = []
    stats = {"checked": 0, "structured_events": 0, "needs_review": 0, "failed": 0,
             "candidate_venues": len(totals), "selected_by_venue": selected_by_venue}
    for item in selected:
        url = item["url"]
        if url.rstrip("/") in known_urls:
            continue
        stats["checked"] += 1
        try:
            parsed, error = read_page(url)
            if parsed:
                stats["structured_events"] += len(parsed)
                for event in parsed[:3]:
                    confidence = "review_schema" if event["name"] and event["date"] and event["venue"] else "incomplete"
                    results.append({**event, "source_url": url, "source_venue": item.get("venue"),
                                    "confidence": confidence, "review_required": True})
            else:
                stats["needs_review"] += 1
                results.append({"source_url": url, "source_venue": item.get("venue"),
                                "link_title": item.get("title", ""), "review_required": True,
                                "reason": error or "no_music_event_schema"})
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            stats["failed"] += 1
            results.append({"source_url": url, "source_venue": item.get("venue"),
                            "review_required": True, "reason": str(e)[:150]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
       "description": "Candidates only, not confirmed concerts or ticket status",
       "stats": stats, "cursor_by_venue": next_cursor, "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(stats)

if __name__ == "__main__":
    main()
