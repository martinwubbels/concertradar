#!/usr/bin/env python3
"""Offline tests: a discovery remains dated on later scans, and festivals are explicit."""
import json
import tempfile
import unittest
from pathlib import Path
import build_discoveries as feed

class DiscoveryFeedTests(unittest.TestCase):
    def test_keep_first_seen_and_festival_kind(self):
        original=(feed.REVIEW,feed.CATALOG,feed.OUTPUT)
        try:
            with tempfile.TemporaryDirectory() as dirname:
                root=Path(dirname)
                feed.REVIEW=root/"event-review.json"
                feed.CATALOG=root/"concerts.json"
                feed.OUTPUT=root/"new-discoveries.json"
                def raw(name,url,types=None):
                    return {"confidence":"review_schema","name":name,"date":"2030-07-14",
                        "venue":"A stage","city":"Zwolle","source_url":url,
                        "source_venue":"Test podium","event_type":types or ["MusicEvent"],
                        "price":24,"currency":"EUR"}
                feed.REVIEW.write_text(json.dumps({"results":[
                    raw("Roots Festival","https://example.org/roots-festival",["Festival"]),
                    raw("Theater Oostpool","https://example.org/theater"),
                    raw("Normal Band","https://example.org/normal")
                ]}),encoding="utf-8")
                feed.CATALOG.write_text(json.dumps({"events":[]}),encoding="utf-8")
                old_time="2026-11-25T10:00:00+00:00"
                feed.OUTPUT.write_text(json.dumps({"updated_at":old_time,"events":[{
                    "id":"suggestion-2030-07-14-rootsfestival",
                    "name":"Roots Festival","date":"2030-07-14"
                }]}),encoding="utf-8")
                feed.build()
                one=json.loads(feed.OUTPUT.read_text(encoding="utf-8"))
                self.assertEqual(len(one["events"]),2)
                festival=next(e for e in one["events"] if e["name"]=="Roots Festival")
                self.assertEqual(festival["event_kind"],"festival")
                self.assertEqual(festival["first_seen_at"],old_time)
                self.assertTrue(festival["last_seen_at"])
                concert=next(e for e in one["events"] if e["name"]=="Normal Band")
                self.assertEqual(concert["event_kind"],"concert")
                first=concert["first_seen_at"]
                feed.build()
                two=json.loads(feed.OUTPUT.read_text(encoding="utf-8"))
                self.assertEqual(next(e for e in two["events"] if e["name"]=="Normal Band")["first_seen_at"],first)
        finally:
            feed.REVIEW,feed.CATALOG,feed.OUTPUT=original

if __name__=="__main__":
    unittest.main()