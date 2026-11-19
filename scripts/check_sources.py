#!/usr/bin/env python3
"""Read-only daily checks of official event pages.

A missing page is NOT proof of cancellation. Cancellation requires explicit
schema.org eventStatus=EventCancelled on a matching event. A date change
requires an event with the same performer/title on the same event URL.
No catalog or personal settings are modified.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data/concerts.json"
OUTPUT=ROOT/"data/source-checks.json"
MAX_PAGES=50
HEADERS={"User-Agent":"ConcertRadar/1.0 source verification (read-only)","Accept":"text/html"}
EVENT_TYPES={"MusicEvent","Event","TheaterEvent","Festival"}

class JsonLd(HTMLParser):
    def __init__(self):
        super().__init__();self.in_json=False;self.buf=[];self.blocks=[]
    def handle_starttag(self,tag,attrs):
        if tag=="script" and dict(attrs).get("type","").lower()=="application/ld+json":
            self.in_json=True;self.buf=[]
    def handle_data(self,data):
        if self.in_json:self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=="script" and self.in_json:
            self.blocks.append("".join(self.buf));self.in_json=False

def items(node):
    if isinstance(node,list):
        for x in node:yield from items(x)
    elif isinstance(node,dict):
        if "@graph" in node:yield from items(node["@graph"])
        if "@type" in node:yield node

def norm(s):
    s=unicodedata.normalize("NFKD",str(s or "")).casefold()
    return " ".join(re.findall(r"[a-z0-9]+",s))

def is_direct(url):
    p=urllib.parse.urlsplit(url)
    return p.scheme=="https" and bool(p.hostname) and len(p.path.strip("/").split("/"))>=2 and p.path.rstrip("/") not in ("/agenda","/programma","/events")

def title_match(expected,actual):
    a=[x for x in norm(expected).split() if len(x)>=3 and x not in {"the","and","met","van","friends","plus"}]
    b=set(norm(actual).split())
    return bool(a) and sum(x in b for x in a[:4])/len(a[:4])>=0.60

def matching_schema(concert,blocks):
    hits=[]
    for raw in blocks:
        try:data=json.loads(raw)
        except (ValueError,TypeError):continue
        for x in items(data):
            types=x.get("@type",[])
            if isinstance(types,str):types=[types]
            if not any(t in EVENT_TYPES for t in types):continue
            if not title_match(concert["name"],x.get("name","")):continue
            linked=x.get("url")
            if isinstance(linked,str) and linked:
                # A schema URL from another show is not this concert.
                if urllib.parse.urlsplit(linked).path.rstrip("/")!=urllib.parse.urlsplit(concert["url"]).path.rstrip("/"):continue
            hits.append(x)
    return hits

def evaluate(concert,blocks,when):
    hits=matching_schema(concert,blocks)
    if len(hits)!=1:
        return {"state":"unavailable","reason":"no_unique_matching_event_schema","checked_at":when}
    x=hits[0]
    found_date=str(x.get("startDate") or "")[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",found_date):
        return {"state":"unavailable","reason":"no_valid_date","checked_at":when}
    status=str(x.get("eventStatus") or "").rsplit("/",1)[-1]
    result={"state":"confirmed","date":found_date,"checked_at":when,"source_url":concert["url"]}
    if status=="EventCancelled":
        result["state"]="cancelled"
        result["reason"]="event_status_cancelled"
    elif found_date!=concert["date"]:
        result["state"]="changed"
        result["reason"]="date_mismatch"
    if status:result["event_status"]=status
    return result

def read(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=7) as res:
        if res.status!=200 or "html" not in res.headers.get("Content-Type","").lower():raise ValueError("Not an HTML event page")
        source=res.read(650_000).decode("utf-8","replace")
    p=JsonLd();p.feed(source)
    return p.blocks

def build(concerts,previous,fetch,when):
    checks=dict(previous.get("checks") or {})
    alerts=[]
    future=[e for e in concerts if e.get("date","")>=when[:10] and e.get("link_status") in ("event_page","event_page_unverified") and is_direct(e.get("url",""))]
    # Least-recently checked events are monitored first, not the same fixed 35.
    future.sort(key=lambda e:((checks.get(e["id"],{}).get("checked_at") or ""),e.get("date",""),e.get("id","")))
    selected=future[:MAX_PAGES]
    retained={a["id"]:a for a in previous.get("alerts",[]) if any(e.get("id")==a.get("id") for e in future)}
    for e in selected:
        try:result=evaluate(e,fetch(e["url"]),when)
        except (urllib.error.URLError,OSError,TimeoutError,ValueError) as err:
            result={"state":"unavailable","checked_at":when,"reason":type(err).__name__}
        prior=checks.get(e["id"],{})
        if result["state"]=="confirmed":result["last_confirmed_at"]=when
        elif prior.get("last_confirmed_at"):result["last_confirmed_at"]=prior["last_confirmed_at"]
        checks[e["id"]]=result
        retained.pop(e["id"],None)
        if result["state"] in ("changed","cancelled"):
            fingerprint=result.get("date",e["date"])+":"+result["state"]
            alerts.append({"id":e["id"],"name":e["name"],"kind":result["state"],"fingerprint":fingerprint,
             "message":"Datum wijkt af van catalogus" if result["state"]=="changed" else "Expliciete annulering in eventdata",
             "url":e["url"],"checked_at":when})
    alerts.extend(retained.values())
    return {"checked_at":when,"description":"Read-only evidence, rotating checks; failures never imply cancellation",
            "checked_count":len(selected),"eligible_count":len(future),"checks":checks,"alerts":alerts}

def main():
    catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
    previous=json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    result=build(catalog.get("events",[]),previous,read,datetime.now(timezone.utc).isoformat())
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Official event pages checked:",result["checked_count"],"possible changes:",len(result["alerts"]))

if __name__=="__main__":main()
