#!/usr/bin/env python3
"""Offline smoke tests. No credentials, network or user data required."""
import json
import py_compile
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

for path in (ROOT/"scripts").glob("*.py"):
    py_compile.compile(str(path),doraise=True)

html=(ROOT/"index.html").read_text(encoding="utf-8")
assert "<script>" in html and "</script>" in html
source=html.split("<script>",1)[1].split("</script>",1)[0]
with tempfile.TemporaryDirectory() as directory:
    testfile=Path(directory)/"concertradar.js"
    testfile.write_text(source,encoding="utf-8")
    subprocess.run(["node","--check",str(testfile)],check=True)

for path in (ROOT/"data").glob("*.json"):
    json.loads(path.read_text(encoding="utf-8"))

concerts=json.loads((ROOT/"data/concerts.json").read_text(encoding="utf-8"))["events"]
assert len(concerts)==len({c["id"] for c in concerts})
assert all(c["id"] and c["name"] and c["date"] and c["city"] for c in concerts)
assert len(concerts)>=110
assert all(c.get("link_status") in ("event_page","event_page_unverified","venue_or_generic") for c in concerts)
assert sum(c["link_status"]=="event_page" for c in concerts)>=26
venues=json.loads((ROOT/"data/venue-locations.json").read_text(encoding="utf-8"))
assert all("address" in v for v in venues["venues"].values())
cloud_config=json.loads((ROOT/"data/cloud-config.json").read_text(encoding="utf-8"))
assert {"url","anonKey","enabled"} <= cloud_config.keys()
assert "create policy" in (ROOT/"supabase/schema.sql").read_text(encoding="utf-8").lower()
assert "cloudPull" in source
assert "function inboxMarkup" in source
assert "function historyMarkup" in source
assert "function dashboardMarkup" in source
assert "function tasteResult" in source
assert "function surpriseEvidence" in source
assert "function surpriseIndex" in source
assert "function specificMusicDiscovery" in source
assert "Maximaal acht nog niet beoordeelde ontdekkingen" in source
assert "[\'discovery\',\'Smaakmatches\']" not in source
assert "function tasteMarkup" in source
assert "function tasteCloudMarkup" in source
assert "function preloadKnownTaste" in source
assert "KNOWN_TASTE_V1" in source
assert "preloadKnownTaste();render();" in source
assert "function saveTasteWord" in source
assert "function removeTasteWord" in source
assert "function tasteManualEffect" in source
assert "function bindTasteCloud" in source
assert "tasteWordsUpdatedAt" in source
assert "function hasDirectConcertLink" in source
assert "function eventSearchUrl" in source
assert "function concertLinkLabel" in source
assert "link_status" in source
assert "Geen directe concertlink" in source
assert "KAARTEN GEKOCHT" in source
assert "concert-booked" in html
assert "taste-small" in html
subprocess.run(["python","-m","unittest","discover","-s","scripts","-p","test_promotion.py","-v"],cwd=ROOT,check=True)
assert "musicDNAMarkup" in source
assert "listeningMarkup" in source
assert "bindTasteExtras" in source
assert "surpriseMarkup" in source
assert "urgencyMarkup" in source
assert "tasteHistoryMarkup" in source
assert "REJECT_REASONS" in source
assert "function tasteResult" in source
print("ConcertRadar smoke tests passed:",len(concerts),"catalog records")
