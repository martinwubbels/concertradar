#!/usr/bin/env python3
"""Propose exact official event URLs for catalog records lacking a direct page.

Uses existing discovered official links and structured event metadata. Strictly
requires source-domain and event-date evidence. Never publishes proposals to
the live concert list without separate verification.
"""
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data/concerts.json"
DISCOVERY=ROOT/"data/discovery-candidates.json"
REVIEW=ROOT/"data/event-review.json"
OUTPUT=ROOT/"data/link-review.json"
MONTHS={"jan":1,"feb":2,"mrt":3,"mar":3,"apr":4,"mei":5,"jun":6,"jul":7,"aug":8,"sep":9,"okt":10,"oct":10,"nov":11,"dec":12}
DATE_RE=re.compile(r"\b(\d{1,2})\s+(jan|feb|mrt|mar|apr|mei|jun|jul|aug|sep|okt|oct|nov|dec)\.?\b",re.I)

def host(url):
    return urlparse(url).hostname.removeprefix("www.") if urlparse(url).hostname else ""

def norm(s):
    value=unicodedata.normalize("NFKD",str(s or "")).lower()
    return re.sub(r"[^a-z0-9]+"," ",value).strip()

def words(s):
    return [v for v in norm(s).split() if len(v)>2 and v not in {"and","the","met","feat","friends","solo","festival","support","presenteert"}]

def title_match(name,title):
    term=words(name)
    haystack=norm(title)
    # Exact performer name is required for short names and two-act shows.
    if not term:return False
    return len([w for w in term if w in haystack.split()])/len(term)>=0.8

def correct_date(title,event_date):
    match=DATE_RE.search(str(title or ""))
    if not match:return False
    return int(match.group(1))==int(event_date[-2:]) and MONTHS[match.group(2).lower()]==int(event_date[5:7])

def specific(url):
    path=urlparse(url).path.strip("/")
    return bool(path and "/" in path and not path.endswith(("agenda","programma","events")))

def main():
    events=json.loads(CATALOG.read_text(encoding="utf-8")).get("events",[])
    discovery=json.loads(DISCOVERY.read_text(encoding="utf-8")).get("candidates",[])
    structured=json.loads(REVIEW.read_text(encoding="utf-8")).get("results",[])
    suggestions=[]
    for event in events:
        if event.get("link_status")!="venue_or_generic":continue
        original_host=host(event.get("url",""))
        if not original_host:continue
        possibilities=[]
        for candidate in discovery:
            url=candidate.get("url","")
            if host(url)!=original_host or not specific(url):continue
            if title_match(event["name"],candidate.get("title")) and correct_date(candidate.get("title"),event["date"]):
                possibilities.append({"url":url,"evidence":"title_and_date_on_official_site","title":candidate.get("title")})
        for candidate in structured:
            url=candidate.get("source_url","")
            if host(url)!=original_host or not specific(url):continue
            if candidate.get("date")==event["date"] and title_match(event["name"],candidate.get("name","")):
                possibilities.append({"url":url,"evidence":"structured_event_name_and_date","title":candidate.get("name")})
        by_url={}
        for x in possibilities:by_url[x["url"]]=x
        if len(by_url)==1:
            item=next(iter(by_url.values()))
            suggestions.append({"id":event["id"],"name":event["name"],"date":event["date"],"current_url":event["url"],**item})
    result={"generated_at":datetime.now(timezone.utc).isoformat(),
            "status":"suggestions_only_manual_confirmation_required",
            "count":len(suggestions),"suggestions":suggestions}
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Found {len(suggestions)} one-to-one potential event links. Catalog unchanged.")

if __name__=="__main__":
    main()
