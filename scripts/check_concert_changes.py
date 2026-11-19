#!/usr/bin/env python3
"""Read-only comparison of public official event pages with the catalog.

Changes are suggestions, never automatic edits to ticket prices or bookings.
Uses schema.org event data where available. Generic venue home pages are ignored.
"""
import json
import sys
import re
import unicodedata
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from extract_event_details import read_page

CATALOG = ROOT / "data/concerts.json"
OUT = ROOT / "data/changes.json"
MAX_CHECKS = 65

def is_event_link(url):
    try:
        parsed = urlsplit(url)
        parts = [x for x in parsed.path.split("/") if x]
        if parsed.scheme != "https" or not parsed.hostname or len(parts) < 2:
            return False
        # Exclude marketing home pages that return unrelated "first event" schema.
        return any(s in parsed.path.lower() for s in (
            "/programma/", "/agenda/", "/events/", "/event/",
            "/voorstelling/", "/produktion/", "/productie/"))
    except ValueError:
        return False

def comparable_names(a,b):
    def normalize(s):
        txt=unicodedata.normalize("NFKD",str(s or "")).casefold()
        return re.sub(r"[^a-z0-9]+"," ",txt).strip()
    x,y=normalize(a),normalize(b)
    if not x or not y:return False
    return x==y or (min(len(x),len(y))>=7 and (x in y or y in x))

def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date().isoformat()
    events = [e for e in catalog.get("events", []) if e.get("date", "") >= today and is_event_link(e.get("url", ""))]
    # Stable rotation across days: check a different slice on each run.
    pivot = int(datetime.now(timezone.utc).strftime("%j")) % max(1,len(events))
    selected = (events[pivot:] + events[:pivot])[:MAX_CHECKS]
    alerts, stats = [], {"checked":0,"matched":0,"unreadable":0,"mismatch":0}
    for e in selected:
        stats["checked"] += 1
        try:
            found, error = read_page(e["url"])
            # Prefer title+date. If the source moved the concert, accept a different
            # date only when the title still unmistakably refers to the same act.
            same = [x for x in found if x.get("date")==e["date"] and comparable_names(x.get("name"),e["name"])]
            moved = [x for x in found if comparable_names(x.get("name"),e["name"])]
            if not same and not moved:
                stats["unreadable"] += 1
                continue
            x = (same or moved)[0]
            stats["matched"] += 1
            diffs = []
            if x.get("date") and x["date"] != e["date"]:
                diffs.append(f"Datum eerder {e['date']}, pagina {x['date']}")
            if x.get("city") and e.get("city") and x["city"].casefold().strip() != e["city"].casefold().strip():
                diffs.append(f"Plaats eerder {e['city']}, pagina {x['city']}")
            # A title may contain support acts; do not treat minor changes as cancellations.
            if e.get("price") is not None and x.get("price") is not None:
                if x.get("currency") in (None, "EUR") and abs(float(e["price"])-float(x["price"])) > 0.01:
                    diffs.append(f"Prijs eerder €{e['price']}, pagina €{x['price']}")
            if x.get("availability") == "SoldOut" and e.get("priority") != "UITVERKOCHT":
                diffs.append("Officiële metadata meldt uitverkocht")
            if diffs:
                stats["mismatch"] += 1
                alerts.append({"id":e["id"],"name":e["name"],"date":e["date"],"url":e["url"],
                               "description":"; ".join(diffs),"checked_at":datetime.now(timezone.utc).isoformat()})
        except Exception as exc:
            stats["unreadable"] += 1
            print(f"Skipped {e.get('id')}: {type(exc).__name__}: {exc}")
        time.sleep(0.15)
    out={"generated_at":datetime.now(timezone.utc).isoformat(),"type":"unverified_changes_only",
         "description":"Candidates for manual verification. Absence is not confirmation of unchanged data.",
         "stats":stats,"alerts":alerts}
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(stats)

if __name__ == "__main__":
    main()
