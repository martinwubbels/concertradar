#!/usr/bin/env python3
"""Promote only strong, venue-authored event matches to the public masterlist.

This is NOT a live ticket-availability service and NOT an artist taste review.
Uncertain records stay in event-review/new-discoveries. Never overwrite an event
or change an existing ID. No external dependencies, API keys or personal data.
"""
import hashlib
import html
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"data/event-review.json"
MASTER=ROOT/"data/concerts.json"
LOG=ROOT/"data/promotion-report.json"

# Event metadata must originate from the exact first-party event page.
OFFICIAL_HOSTS={
    "metropool.nl","spotgroningen.nl","hedon-zwolle.nl","vera-groningen.nl",
    "drentmeester.nl","deamer.nl","alteweberei.de","emslandarena.com",
    "podium34.nl","nijend24.nl","atlastheater.nl","detamboer.nl",
    "dnk.nl","denieuwekolk.nl","devegafabriek.nl"
}
# Metropool uses TheaterEvent even for its gigs. Other venues need MusicEvent.
MUSIC_ONLY_THEATER_EVENT_HOSTS={"metropool.nl"}
EXCLUDE=re.compile(
    r"\b(cabaret|musical|tribute|tributes|sings coldplay|rolling stones|"
    r"comed(?:y|ie)|stand.?up|talkshow|lezing|rondleiding|workshop|"
    r"juf braaksel|theatercollege|student liedduo competition|"
    r"bert visscher|claudia de breij|dansvoorstelling|toneel|filmfestival)\b",re.I
)
EVENT_PATHS=("/agenda/","/programma/","/voorstelling/","/events/","/event/","/produktion/","/productie/","/concert/")
STOP={"the","and","with","met","van","en","de","het","een","support","plus","ft","feat","live"}

def normalized(value):
    value=unicodedata.normalize("NFKD",html.unescape(str(value or ""))).casefold()
    return re.sub(r"[^a-z0-9]+"," ",value).strip()

def simple_url(url):
    try:
        u=urlsplit(str(url or ""))
        if u.scheme!="https" or not u.hostname or u.username or u.password:return ""
        return urlunsplit(("https",u.hostname.lower().removeprefix("www."),u.path.rstrip("/"),"",""))
    except ValueError:
        return ""

def official_page(url):
    value=simple_url(url)
    if not value:return False
    u=urlsplit(value)
    host=u.hostname
    path=u.path.lower()
    return host in OFFICIAL_HOSTS and any(x in path for x in EVENT_PATHS) and len(path.strip("/").split("/"))>=2

def slug_matches_title(name,url):
    slug=normalized(urlsplit(url).path.rstrip("/").split("/")[-1])
    words=[x for x in normalized(name).split() if len(x)>=3 and x not in STOP]
    if not slug or not words:return False
    # Last path component must actually resemble the claimed act.
    return any(w in slug.split() for w in words[:3])

def primary_name(name):
    name=normalized(name).split(" support ")[0]
    name=re.split(r"\s+(?:\+|with|feat|ft)\s+",name,1)[0]
    return name

def duplicates(existing,event):
    target_url=simple_url(event["url"])
    name=normalized(event["name"])
    primary=primary_name(event["name"])
    for prior in existing:
        if simple_url(prior.get("url",""))==target_url:return True
        if prior.get("date")!=event["date"]:continue
        if normalized(prior.get("city"))!=normalized(event["city"]):continue
        other=normalized(prior.get("name"))
        # Prevent duplicating already-listed headliners with support acts.
        if name==other or (primary and (primary==primary_name(prior.get("name")))) or (name in other or other in name):
            return True
    return False

def eligible(raw,today):
    if raw.get("confidence")!="review_schema":return None,"unconfirmed_schema"
    name=html.unescape(str(raw.get("name") or "")).strip()
    day=str(raw.get("date") or "")
    venue=html.unescape(str(raw.get("venue") or "")).strip()
    city=html.unescape(str(raw.get("city") or "")).strip()
    url=str(raw.get("source_url") or "")
    schema_url=str(raw.get("schema_url") or "")
    if not name or not venue or not city:return None,"missing_name_venue_or_city"
    try:
        if date.fromisoformat(day)<today:return None,"past_event"
    except (ValueError,TypeError):return None,"invalid_date"
    if EXCLUDE.search(name):return None,"nonmusic_keyword"
    if not official_page(url):return None,"not_approved_specific_event_url"
    if simple_url(schema_url)!=simple_url(url):return None,"schema_url_does_not_match_page"
    if not slug_matches_title(name,url):return None,"event_slug_name_mismatch"
    types=raw.get("event_type") or []
    if isinstance(types,str):types=[types]
    host=urlsplit(url).hostname.lower().removeprefix("www.")
    music=("MusicEvent" in types or (host in MUSIC_ONLY_THEATER_EVENT_HOSTS and "TheaterEvent" in types))
    if not music:return None,"music_type_not_confirmed"
    # Price is metadata, not a current booking quote.
    price=raw.get("price")
    if raw.get("currency")!="EUR" or type(price) not in (int,float) or not (0<=price<=10000):
        price=None
    availability=raw.get("availability")
    if availability and availability not in ("InStock","SoldOut","PreOrder","LimitedAvailability","OnlineOnly"):
        availability=None
    return {
        "name":name,"date":day,"venue":venue,"city":city,
        "genre":"Muziek / nog niet ingedeeld",
        "price":price,"quality":None,"value":None,
        "priority":"UITVERKOCHT" if availability=="SoldOut" else "NIEUW · CONTROLEREN",
        "match":"",
        "reason":"Automatisch overgenomen van de officiële concertpagina. Muziekstijl, beoordeling, prijs en beschikbaarheid zelf controleren.",
        "url":simple_url(url),
        "link_status":"event_page",
        "verification":"auto_verified_schema",
        "availability_hint":availability,
        "source_checked_at":datetime.now(timezone.utc).isoformat(),
        "source_venue":str(raw.get("source_venue") or "")
    },None

def run(catalog,review,today):
    existing=list(catalog.get("events") or [])
    entries=list(review.get("results") or [])
    checked={}
    skipped={}
    approved=[]
    # Never trust multiple disagreeing Event blobs on one page.
    by_url={}
    for row in entries:
        url=simple_url(row.get("source_url"))
        if url:by_url.setdefault(url,[]).append(row)
    for url,rows in by_url.items():
        matches=[]
        for row in rows:
            event,why=eligible(row,today)
            if why:skipped[why]=skipped.get(why,0)+1
            elif event:matches.append(event)
        if len(matches)!=1:
            if matches:skipped["ambiguous_multiple_events"]=skipped.get("ambiguous_multiple_events",0)+len(matches)
            continue
        event=matches[0]
        if duplicates(existing+approved,event):
            skipped["already_in_masterlist"]=skipped.get("already_in_masterlist",0)+1
            continue
        # Deterministic ID, stable on every rerun and across link changes.
        compact=re.sub(r"[^a-z0-9]","",normalized(event["name"]))[:46]
        base=f"suggestion-{event['date']}-{compact}"
        # Existing discovery decisions use this ID. Reject clashes rather than changing identity.
        if any(x.get("id")==base for x in existing+approved):
            skipped["id_collision"]=skipped.get("id_collision",0)+1
            continue
        event["id"]=base
        approved.append(event)
    updated=dict(catalog)
    if approved:
        updated["events"]=sorted(existing+approved,key=lambda e:(e.get("date",""),normalized(e.get("name"))))
        updated["updated_at"]=datetime.now(timezone.utc).date().isoformat()
    stats={"checked_records":len(entries),"approved":len(approved),"skipped":skipped,
           "added":[{"id":e["id"],"name":e["name"],"date":e["date"],"url":e["url"]} for e in approved]}
    return updated,stats

def main():
    catalog=json.loads(MASTER.read_text(encoding="utf-8"))
    review=json.loads(INPUT.read_text(encoding="utf-8"))
    # Refuse to promote stale cached extraction results.
    generated=review.get("generated_at")
    try:
        stamp=datetime.fromisoformat(generated.replace("Z","+00:00"))
    except (AttributeError,ValueError):
        raise SystemExit("No valid extraction timestamp. Masterlist unchanged.")
    if (datetime.now(timezone.utc)-stamp).total_seconds()>3*3600:
        raise SystemExit("Extraction older than 3 hours. Masterlist unchanged.")
    updated,stats=run(catalog,review,datetime.now(timezone.utc).date())
    if stats["approved"]:
        MASTER.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report={"generated_at":datetime.now(timezone.utc).isoformat(),
            "description":"Only strict official music event matches auto-added; all others remain separate.",
            **stats}
    LOG.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Added {stats['approved']} strictly verified shows; {len(stats['skipped'])} exclusion reasons.")
if __name__=="__main__":
    main()
