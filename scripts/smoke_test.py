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
# In compact mode, images must remain visible: do not regress the photo display.
assert ".compact-event .artistpic{display:none}" not in html
assert ".compact-event .artistpic{display:flex" in html
assert "const photoOf=e=>" in source
assert "officialPhotos[e.id]?.url" in source
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
assert "function sourceDetail" in source
assert "function artistProfile" in source
assert "function personalDashboardTop" in source
assert "function noticeCandidates" in source
assert "function travelInfo" in source
assert "function agendaConflicts" in source
assert "function parseCalendarDates" in source
assert "function bindNewDashboard" in source
assert "data/source-checks.json" in source
assert "data/artist-profiles.json" in source
assert "Reisgrenzen" in source
assert "Mijn startscherm" in source
subprocess.run(["python","-m","unittest","discover","-s","scripts","-p","test_source_checks.py","-v"],cwd=ROOT,check=True)
subprocess.run(["node","scripts/test_six_features.cjs"],cwd=ROOT,check=True)
profiles=json.loads((ROOT/"data/artist-profiles.json").read_text(encoding="utf-8"))["artists"]
assert "willow avalon" in profiles and "henry wagons" in profiles
checks=json.loads((ROOT/"data/source-checks.json").read_text(encoding="utf-8"))
assert "checks" in checks and "alerts" in checks
assert "function googleCalendarEventUrl" in source
assert "function outlookCalendarEventUrl" in source
assert "function musicHistoryMarkup" in source
assert "function listeningHistoryBoost" in source
assert "function freshness(e)" in source
assert "mobileTab" in source
assert "compactCards" in source
assert "function scoreDetails" in source
subprocess.run(["node","scripts/test_v2.cjs"],cwd=ROOT,check=True)
assert "function searchNowUrl" in source
assert "function searchNowMarkup" in source
assert "function bindSearchNow" in source
assert "Volledige podiumscan via GitHub" in source
subprocess.run(["node","scripts/test_search_now.cjs"],cwd=ROOT,check=True)
# Concertkaarten v3: compacte inhoud en uitsluitend drie primaire acties.
card_source=source.split("function card(e){",1)[1].split("function updates(){",1)[0]
assert "event-card-v3" in card_source
assert '"card-primary-actions"' in card_source
assert card_source.count('data-action="interested"')==1
assert card_source.count('data-action="booked"')==1
assert card_source.count('data-action="rejected"')==1
assert '"event-more"' in card_source
assert "data-artist-profile" in card_source
assert "data-listen-open" in card_source
assert "googleCalendarEventUrl(e)" in card_source
assert "outlookCalendarEventUrl(e)" in card_source
assert "spotifyUrl(e)" in card_source
assert "scoreDetails(e)" in card_source
assert "photoOf(e)" in card_source
assert ".event-card-v3 .artistpic" in html
assert ".event-card-v3 .card-bottom" in html
assert "grid-template-columns:54px 60px minmax(0,1fr)" in html
assert "display:flex;flex-wrap:wrap" in html
assert "function dashboardSuggestionEntries" in source
assert "function dashboardShortlistMarkup" in source
assert "Nieuwe suggesties om te shortlisten" in source
assert "candidate_unverified" in source
subprocess.run(["node","scripts/test_home_shortlist.cjs"],cwd=ROOT,check=True)
subprocess.run(["node","scripts/test_new_overview.cjs"],cwd=ROOT,check=True)
subprocess.run(["node","scripts/test_navigation_dashboard.cjs"],cwd=ROOT,check=True)
subprocess.run(["python","-m","unittest","discover","-s","scripts","-p","test_discovery_feed.py","-v"],cwd=ROOT,check=True)
print("ConcertRadar smoke tests passed:",len(concerts),"catalog records")
