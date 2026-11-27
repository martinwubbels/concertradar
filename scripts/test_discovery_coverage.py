#!/usr/bin/env python3
"""Offline coverage tests. Never call venue websites."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import discover_venues as discover
import extract_event_details as extract


class SourceCoverageTests(unittest.TestCase):
    def test_round_robin_and_failed_venue_history(self):
        old = discover.CATALOG, discover.OUT, discover.VENUES
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                discover.CATALOG = root / "catalog.json"
                discover.OUT = root / "links.json"
                discover.VENUES = [
                    ("Large", "https://large.example/agenda/"),
                    ("Small", "https://small.example/agenda/"),
                    ("Broken", "https://broken.example/agenda/"),
                ]
                discover.CATALOG.write_text('{"events":[]}', encoding="utf-8")
                discover.OUT.write_text(json.dumps({"venues": {
                    "Broken": {"last_ok_at": "2026-11-21T11:00:00+00:00"}
                }}), encoding="utf-8")

                def collect(name, source):
                    if name == "Broken":
                        raise OSError("Temporary connection error")
                    return [{"url": f"https://{name.lower()}.example/event/{i}",
                             "title": f"Artist {i}", "venue": name}
                            for i in range(125 if name == "Large" else 3)]

                with patch.object(discover, "collect", side_effect=collect):
                    discover.main()
                result = json.loads(discover.OUT.read_text(encoding="utf-8"))
                self.assertEqual(result["summary"]["venues_ok"], 2)
                self.assertEqual(result["summary"]["venues_failed"], 1)
                self.assertEqual(result["venues"]["Broken"]["last_ok_at"], "2026-11-21T11:00:00+00:00")
                self.assertEqual(result["venues"]["Large"]["candidate_links"], 125)
                self.assertEqual(result["venues"]["Small"]["candidate_links"], 3)
                # The small venue gets the same initial visibility as the large one.
                self.assertEqual([x["venue"] for x in result["candidates"][:6]],
                                 ["Large", "Small", "Large", "Small", "Large", "Small"])
                self.assertEqual(len(result["candidates"]), 103)
                self.assertEqual(len({x["url"] for x in result["candidates"]}), 103)
        finally:
            discover.CATALOG, discover.OUT, discover.VENUES = old

    def test_extraction_cursor_rotates_venues(self):
        old = extract.INPUT, extract.CATALOG, extract.OUT, extract.MAX_PAGES
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                extract.INPUT, extract.CATALOG, extract.OUT = (
                    root / "candidate.json", root / "catalog.json", root / "review.json"
                )
                extract.MAX_PAGES = 2
                extract.CATALOG.write_text('{"events":[]}', encoding="utf-8")
                items = [
                    {"url": f"https://a.example/event/{i}", "venue": "A", "title": "Singer"}
                    for i in range(3)
                ] + [
                    {"url": f"https://b.example/event/{i}", "venue": "B", "title": "Band"}
                    for i in range(3)
                ]
                extract.INPUT.write_text(json.dumps({"candidates": items}), encoding="utf-8")
                def parse(url):
                    return [], "no_music_event_schema"
                with patch.object(extract, "read_page", side_effect=parse):
                    extract.main()
                    one = json.loads(extract.OUT.read_text(encoding="utf-8"))
                    extract.main()
                    two = json.loads(extract.OUT.read_text(encoding="utf-8"))
                first_urls = [x["source_url"] for x in one["results"]]
                next_urls = [x["source_url"] for x in two["results"]]
                self.assertNotEqual(first_urls, next_urls)
                self.assertTrue(all(x.endswith("/0") for x in first_urls))
                self.assertTrue(all(x.endswith("/1") for x in next_urls))
                self.assertEqual(two["stats"]["selected_by_venue"], {"A": 1, "B": 1})
        finally:
            extract.INPUT, extract.CATALOG, extract.OUT, extract.MAX_PAGES = old

    def test_verified_official_agendas_and_venue_patterns(self):
        sites = dict(discover.VENUES)
        self.assertEqual(sites["Simplon Groningen"], "https://simplon.nl/programma/")
        self.assertEqual(sites["Theater Meppen"], "https://www.meppen-theater.de/termine/liste/")
        self.assertIn("/events/", discover.PATTERNS)
        self.assertIn("/termin/", discover.PATTERNS)


if __name__ == "__main__":
    unittest.main()
