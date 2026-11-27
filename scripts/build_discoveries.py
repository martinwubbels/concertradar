#!/usr/bin/env python3
"""Build an explicitly UNVERIFIED discovery feed, separate from the masterlist."""
import html
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data/event-review.json"
CATALOG = ROOT / "data/concerts.json"
OUTPUT = ROOT / "data/new-discoveries.json"

# Only infer a missing city when the official programme has a single,
# unambiguous venue city. This is not equivalent to event-level confirmation.
VENUE_CITIES = {
    "SPOT Groningen": "Groningen", "VERA Groningen": "Groningen",
    "Simplon Groningen": "Groningen", "Hedon Zwolle": "Zwolle",
    "Theater Meppen": "Meppen", "Alte Weberei Nordhorn": "Nordhorn",
    "De Amer": "Amen", "De Tamboer": "Hoogeveen",
    "ATLAS Theater": "Emmen", "DNK Assen": "Assen",
}

EXCLUDE = re.compile(
    r"\b(cabaret|musical|tribute|tributes|sings coldplay|rolling stones|theatercollege|"
    r"comed(y|ie)|stand.up|talkshow|kinder(show|theater)|juf braaksel|"
    r"lezing|rondleiding|workshop|hotel 3|student liedduo competition|"
    r"bert visscher|claudia de breij|het nationale theater|theater oostpool|nederlands dans theater|jimmy carr|david linszen)\b", re.I
)

def norm(s):
    s = unicodedata.normalize("NFKD", html.unescape(str(s or "")))
    return re.sub(r"[^a-z0-9]+", "", s.casefold())

def cleanurl(s):
    p = urlsplit(str(s or ""))
    return (p.netloc.lower() + p.path.rstrip("/")).lower()

def build():
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    known_urls = {cleanurl(e.get("url")) for e in catalog.get("events", [])}
    known_names = {(norm(e.get("name")), e.get("date")) for e in catalog.get("events", [])}
    seen = set()
    found = []
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    try:
        previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = {}
    previous_by_id = {e["id"]: e for e in previous.get("events", []) if e.get("id")}
    # Existing feed entries were known no later than its last generation.
    previous_cutoff = previous.get("updated_at") or now
    for raw in review.get("results", []):
        if raw.get("confidence") != "review_schema":
            continue
        name = html.unescape(str(raw.get("name") or "")).strip()
        day = str(raw.get("date") or "")[:10]
        venue = html.unescape(str(raw.get("venue") or "")).strip()
        url = str(raw.get("source_url") or "")
        types = raw.get("event_type") or []
        if not (name and venue and re.fullmatch(r"\d{4}-\d{2}-\d{2}", day)):
            continue
        if day < today or EXCLUDE.search(name):
            continue
        if not any(t in types for t in ("MusicEvent", "Event", "TheaterEvent", "Festival")):
            continue
        if urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
            continue
        key = (norm(name), day)
        if key in known_names or cleanurl(url) in known_urls or key in seen:
            continue
        seen.add(key)
        source_venue = str(raw.get("source_venue") or "")
        parsed_city = html.unescape(str(raw.get("city") or "")).strip()
        city = parsed_city or VENUE_CITIES.get(source_venue, "")
        city_source = "official_page_schema" if parsed_city else ("venue_location" if city else "unknown")
        price = raw.get("price") if raw.get("currency") in ("EUR", "€") else None
        if not isinstance(price, (int, float)) or not 0 <= price <= 10000:
            price = None
        event_id = "suggestion-" + day + "-" + re.sub(r"[^a-z0-9]+", "-", norm(name))[:48]
        prior = previous_by_id.get(event_id, {})
        festival = "Festival" in types or bool(re.search(r"\bfestival\b|\bpopronde\b|\bnoorderslag\b|\btakeroot\b|\bbuspop\b", name, re.I))
        found.append({
            "id": event_id,
            "event_kind": "festival" if festival else "concert",
            "first_seen_at": prior.get("first_seen_at") or (previous_cutoff if prior else now),
            "last_seen_at": now,
            "name": name, "date": day, "venue": venue,
            "city": city, "city_source": city_source,
            "source_venue": source_venue,
            "schema_types": types,
            "source_checked_at": review.get("generated_at") or now,
            "verification": "candidate_unverified",
            "url": url, "price": price,
            "availability_hint": raw.get("availability"),
            "review_required": True,
        })
    found.sort(key=lambda e: (e["date"], e["name"]))
    output = {
        "updated_at": now,
        "status": "suggestions_not_confirmed_or_ranked",
        "events": found[:150],
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(output['events'])} unverified possible discoveries. No events added to masterlist.")

if __name__ == "__main__":
    build()
