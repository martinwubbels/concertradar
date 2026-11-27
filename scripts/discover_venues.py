#!/usr/bin/env python3
"""Read-only discovery: find possible new event links on known official venue pages.

This intentionally does NOT add events automatically. Search/agenda links are not
confirmed performances. Inspect the generated candidate JSON and official event
pages before promoting anything to data/concerts.json.
No third-party packages, accounts, secrets or paid APIs required.
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
CATALOG = ROOT / "data/concerts.json"
OUT = ROOT / "data/discovery-candidates.json"
VENUES = [
    ("SPOT Groningen", "https://www.spotgroningen.nl/programma/"),
    ("VERA Groningen", "https://www.vera-groningen.nl/"),
    ("Simplon Groningen", "https://simplon.nl/programma/"),
    ("Hedon Zwolle", "https://www.hedon-zwolle.nl/"),
    ("Metropool", "https://metropool.nl/agenda/"),
    ("De Amer", "https://www.deamer.nl/"),
    ("d'Rentmeester", "https://www.drentmeester.nl/"),
    ("De Vegafabriek", "https://www.devegafabriek.nl/"),
    ("Podium34", "https://www.podium34.nl/"),
    ("Klein Paradiso", "https://delibre.nl/klein-paradiso/"),
    ("Nijend24", "https://www.nijend24.nl/"),
    ("Podium Zuidhaege", "https://podiumzuidhaege.nl/"),
    ("De Tamboer", "https://detamboer.nl/programma"),
    ("ATLAS Theater", "https://www.atlastheater.nl/"),
    ("DNK Assen", "https://www.dnk.nl/"),
    ("Alte Weberei Nordhorn", "https://alteweberei.de/programm/"),
    ("EmslandArena Lingen", "https://www.emslandarena.com/"),
    ("Theater Meppen", "https://www.meppen-theater.de/termine/liste/"),
    ("Het Podium Hoogeveen", "https://detamboer.nl/"),
    ("Poppunt Drenthe", "https://poppuntdrenthe.nl/"),
]
HEADERS = {"User-Agent": "ConcertRadar personal music calendar/1.0", "Accept": "text/html,application/xhtml+xml"}
PATTERNS = ("/programma/", "/agenda/", "/events/", "/event/", "/voorstelling/", "/productie/", "/produktion/", "/veranstaltung/", "/termin/", "/concert/")
NONMUSIC = re.compile(r"cabaret|musical|theaterweekend|dansvoorstelling|stand-up|comed(y|ie)|toneel|lezing|rondleiding|workshop|kindervoorstelling", re.I)
GENERIC = re.compile(r"/(verzameling|collectie|nieuws|categorie|category|page|tag|thema|abonnement|archief)(/|$)", re.I)
EXCLUDE = re.compile(r"/(tickets?|login|contact|privacy|cookies|nieuws|news|over-ons|about|zoeken|search|account|winkelwagen)(/|$)", re.I)

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_url = None
        self.label = []
    def handle_starttag(self, tag, attrs):
        if tag.lower()=="a":
            a=dict(attrs)
            self.current_url=a.get("href")
            self.label=[]
    def handle_data(self, data):
        if self.current_url is not None:
            self.label.append(data)
    def handle_endtag(self, tag):
        if tag.lower()=="a" and self.current_url is not None:
            self.links.append((self.current_url, re.sub(r"\s+", " ", " ".join(self.label)).strip()[:130]))
            self.current_url=None
            self.label=[]

def normalize(url):
    x=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((x.scheme,x.netloc,x.path.rstrip("/")+"/" if x.path.endswith("/") else x.path,"",""))

def collect(name, page):
    req=urllib.request.Request(page,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=9) as response:
        if "html" not in response.headers.get("Content-Type","").lower():
            raise ValueError("Not an HTML page")
        html=response.read(750_000).decode("utf-8","replace")
        base=response.geturl()
    parser=Links()
    parser.feed(html)
    host=urllib.parse.urlsplit(base).hostname or ""
    seen=set()
    out=[]
    for href,title in parser.links:
        if not href or href.startswith(("#","mailto:","javascript:","tel:")):
            continue
        url=urllib.parse.urljoin(base,href)
        parsed=urllib.parse.urlsplit(url)
        target_host=parsed.hostname or ""
        if not (target_host==host or target_host.endswith("."+host)):
            continue
        if parsed.scheme!="https" or EXCLUDE.search(parsed.path):
            continue
        path=parsed.path.lower()
        if GENERIC.search(parsed.path) or not any(p in path for p in PATTERNS):
            continue
        if path.rstrip("/") in ("/agenda","/programma","/events","/event","/concert","/veranstaltungen"):
            continue
        clean=normalize(url)
        if clean in seen or clean==normalize(base):
            continue
        seen.add(clean)
        out.append({"url":clean,"title":title,"venue":name,"discovery_source":page,"review_priority":"low_nonmusic" if NONMUSIC.search(title) else "review"})
    return out[:250]

def main():
    original = json.loads(CATALOG.read_text(encoding="utf-8"))
    urls = {normalize(e.get("url", "")) for e in original.get("events", [])
            if str(e.get("url", "")).startswith("https://")}
    # Retain the last successful check when a venue is temporarily inaccessible.
    try:
        prior = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prior = {}
    older = prior.get("venues", {})
    cursor_by_venue = prior.get("cursor_by_venue") or {}
    next_cursor = {}
    now = datetime.now(timezone.utc).isoformat()
    by_venue = {}
    status = {}
    for name, url in VENUES:
        previous_ok = (older.get(name) or {}).get("last_ok_at")
        try:
            found = collect(name, url)
            new_links = [event for event in found if event["url"] not in urls]
            if new_links:
                offset = int(cursor_by_venue.get(name, 0) or 0) % len(new_links)
                ordered = new_links[offset:] + new_links[:offset]
                by_venue[name] = ordered[:100]
                next_cursor[name] = (offset + len(by_venue[name])) % len(new_links)
            else:
                by_venue[name] = []
                next_cursor[name] = 0
            status[name] = {
                "status": "ok", "url": url, "checked_at": now,
                "last_ok_at": now, "links_seen": len(found),
                "candidate_links": len(new_links),
            }
            print(f"{name}: {len(found)} links; {len(new_links)} candidates")
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            next_cursor[name] = int(cursor_by_venue.get(name, 0) or 0)
            status[name] = {
                "status": "failed", "url": url, "checked_at": now,
                "last_ok_at": previous_ok, "links_seen": 0,
                "candidate_links": 0, "reason": str(error)[:160],
            }
            print(f"{name}: inaccessible ({error})")
    # Round robin. One large agenda must not displace smaller venues from the
    # published candidate feed (previously capped at 600 in venue order).
    candidates = []
    used = set()
    while len(candidates) < 600 and any(by_venue.values()):
        for name, _ in VENUES:
            group = by_venue.get(name, [])
            if not group:
                continue
            item = group.pop(0)
            if item["url"] in used:
                continue
            used.add(item["url"])
            candidates.append(item)
            if len(candidates) >= 600:
                break
    output = {
        "generated_at": now, "type": "unverified_links_not_events",
        "summary": {
            "venues_total": len(VENUES),
            "venues_ok": sum(v["status"] == "ok" for v in status.values()),
            "venues_failed": sum(v["status"] == "failed" for v in status.values()),
            "candidates": len(candidates),
            "policy": "Unverified venue links; not confirmations, tickets or a complete calendar",
        },
        "venues": status, "cursor_by_venue": next_cursor, "candidates": candidates,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(candidates)} unverified links; no masterlist changes")

if __name__=="__main__":
    main()
