#!/usr/bin/env python3
"""Offline review tests: only owner-proposed, recent, strict official rows can become a PR."""
import copy
import unittest
from datetime import datetime, timezone, timedelta
from review_candidate import candidate_id, stage

NOW = datetime(2026, 11, 27, 21, 0, tzinfo=timezone.utc)
ID = "suggestion-2027-03-20-rootsinger"
URL = "https://simplon.nl/events/root-singer/"
RAW = {
    "confidence": "review_schema", "name": "Root Singer", "date": "2027-03-20",
    "venue": "Simplon", "city": "Groningen", "source_url": URL,
    "schema_url": URL, "event_type": ["MusicEvent"], "source_venue": "Simplon Groningen",
    "price": 23, "currency": "EUR",
}
CAND = {
    "id": ID, "name": "Root Singer", "date": "2027-03-20",
    "venue": "Simplon", "city": "Groningen", "url": URL,
    "city_source": "venue_location", "verification": "candidate_unverified",
}


def recent():
    return {"generated_at": (NOW - timedelta(hours=2)).isoformat(), "results": [copy.deepcopy(RAW)]}


class ProposalTests(unittest.TestCase):
    def test_issue_id_parsing_rejects_untrusted_values(self):
        self.assertEqual(candidate_id("", "ConcertRadar-ID: " + ID + "\n\nReview"), ID)
        self.assertEqual(candidate_id(ID), ID)
        with self.assertRaises(ValueError):
            candidate_id("", "ConcertRadar-ID: ; rm -rf /")
        with self.assertRaises(ValueError):
            candidate_id("", "candidate unknown")

    def test_valid_official_candidate_requires_separate_pr(self):
        catalog = {"schema_version": 1, "updated_at": "2026-11-27", "events": []}
        updated, added = stage({"events": [CAND]}, recent(), catalog, ID, NOW)
        self.assertEqual(added["id"], ID)
        self.assertEqual(added["date"], "2027-03-20")
        self.assertEqual(len(updated["events"]), 1)
        self.assertEqual(len(catalog["events"]), 0, "Stage returns a copy, never silently edits main")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            stage({"events": [CAND]}, recent(), updated, ID, NOW)

    def test_city_derived_from_official_venue_is_explicit(self):
        review = recent()
        review["results"][0]["city"] = ""
        updated, _ = stage({"events": [CAND]}, review, {"events": []}, ID, NOW)
        self.assertEqual(updated["events"][0]["city"], "Groningen")
        bad = {**CAND, "city_source": "unknown"}
        with self.assertRaisesRegex(ValueError, "missing_name_venue_or_city"):
            stage({"events": [bad]}, review, {"events": []}, ID, NOW)

    def test_music_evidence_can_only_make_unverified_pr_proposal(self):
        review = recent()
        review["results"][0]["event_type"] = ["Event"]
        review["results"][0]["performer"] = "Root Singer"
        review["results"][0]["description"] = "Een live concert met country en americana."
        updated, added = stage({"events": [CAND]}, review, {"events": []}, ID, NOW)
        self.assertEqual(added["id"], ID)
        record = updated["events"][0]
        self.assertEqual(record["verification"], "manual_review_required")
        self.assertEqual(record["priority"], "VOORSTEL · CONTROLEREN")
        self.assertIsNone(record["availability_hint"])
        self.assertIn("niet als MusicEvent bevestigd", record["reason"])
        review["results"][0]["description"] = "Een toneelvoorstelling"
        with self.assertRaisesRegex(ValueError, "Generic event lacks"):
            stage({"events": [CAND]}, review, {"events": []}, ID, NOW)

    def test_outdated_or_ambiguous_or_generic_events_rejected(self):
        review = recent()
        review["generated_at"] = (NOW - timedelta(days=4)).isoformat()
        with self.assertRaisesRegex(ValueError, "older"):
            stage({"events": [CAND]}, review, {"events": []}, ID, NOW)
        review = recent()
        review["results"].append(copy.deepcopy(RAW))
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            stage({"events": [CAND]}, review, {"events": []}, ID, NOW)
        review = recent()
        review["results"][0]["event_type"] = ["Event"]
        with self.assertRaisesRegex(ValueError, "lacks performer"):
            stage({"events": [CAND]}, review, {"events": []}, ID, NOW)
        review = recent()
        review["results"][0]["schema_url"] = "https://simplon.nl/events/other/"
        with self.assertRaisesRegex(ValueError, "schema_url_does_not_match_page"):
            stage({"events": [CAND]}, review, {"events": []}, ID, NOW)


if __name__ == "__main__":
    unittest.main()
