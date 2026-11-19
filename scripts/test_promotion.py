#!/usr/bin/env python3
"""Offline safety tests for daily concert auto-promotion."""
import copy
import unittest
from datetime import date
from promote_verified_concerts import eligible,run

TODAY=date(2026,11,19)
BASE={
  "confidence":"review_schema",
  "name":"Noah Derksen",
  "date":"2026-11-21",
  "venue":"Vestzak, Enschede",
  "city":"Enschede",
  "source_url":"https://metropool.nl/agenda/noah-derksen",
  "schema_url":"https://metropool.nl/agenda/noah-derksen",
  "event_type":["TheaterEvent"],
  "source_venue":"Metropool",
  "price":20,
  "currency":"EUR",
  "availability":"InStock",
}

class PromotionTests(unittest.TestCase):
    def test_accept_specific_metropool_gig(self):
        e,reason=eligible(copy.deepcopy(BASE),TODAY)
        self.assertIsNone(reason)
        self.assertEqual(e["city"],"Enschede")
        self.assertEqual(e["url"],BASE["source_url"])
        self.assertEqual(e["price"],20)
        self.assertIsNone(e["quality"])
        self.assertEqual(e["verification"],"auto_verified_schema")

    def test_reject_generic_venue_homepage(self):
        row={**BASE,"source_url":"https://metropool.nl","schema_url":"https://metropool.nl"}
        self.assertIsNone(eligible(row,TODAY)[0])

    def test_reject_wrong_source_or_event_schema_url(self):
        self.assertIsNone(eligible({**BASE,"schema_url":"https://metropool.nl/agenda/other"},TODAY)[0])
        self.assertIsNone(eligible({**BASE,"source_url":"https://example.com/agenda/noah-derksen","schema_url":"https://example.com/agenda/noah-derksen"},TODAY)[0])

    def test_reject_missing_city_or_generic_event_at_mixed_venue(self):
        self.assertIsNone(eligible({**BASE,"city":""},TODAY)[0])
        row={**BASE,"event_type":["Event"],"source_url":"https://www.spotgroningen.nl/programma/noah-derksen/","schema_url":"https://www.spotgroningen.nl/programma/noah-derksen/"}
        self.assertIsNone(eligible(row,TODAY)[0])

    def test_music_event_at_approved_venue(self):
        row={**BASE,"event_type":["MusicEvent"],"source_url":"https://www.spotgroningen.nl/programma/noah-derksen/","schema_url":"https://www.spotgroningen.nl/programma/noah-derksen/"}
        self.assertIsNotNone(eligible(row,TODAY)[0])

    def test_reject_nonmusic_even_if_venue_metadata_claims_event(self):
        row={**BASE,"name":"Niels Geusebroek sings Coldplay","source_url":"https://metropool.nl/agenda/niels-geusebroek-sings-coldplay","schema_url":"https://metropool.nl/agenda/niels-geusebroek-sings-coldplay"}
        self.assertIsNone(eligible(row,TODAY)[0])

    def test_reject_stale_event_and_undocumented_price_currency(self):
        self.assertIsNone(eligible({**BASE,"date":"2026-11-18"},TODAY)[0])
        e,_=eligible({**BASE,"currency":"USD"},TODAY)
        self.assertIsNone(e["price"])

    def test_dedupe_by_matching_existing_performer_date_city(self):
        catalog={"schema_version":1,"updated_at":"2026-11-19","events":[
            {"id":"already-here","name":"Noah Derksen + support","date":"2026-11-21","city":"Enschede","url":"https://metropool.nl/"}
        ]}
        updated,stats=run(catalog,{"results":[BASE]},TODAY)
        self.assertEqual(stats["approved"],0)
        self.assertEqual(updated,catalog)

    def test_accept_then_stay_idempotent(self):
        original={"schema_version":1,"updated_at":"2026-11-19","events":[]}
        first,stats=run(original,{"results":[BASE]},TODAY)
        self.assertEqual(stats["approved"],1)
        self.assertEqual(first["events"][0]["id"],"suggestion-2026-11-21-noahderksen")
        second,again=run(first,{"results":[BASE]},TODAY)
        self.assertEqual(again["approved"],0)
        self.assertEqual(second,first)

    def test_ambiguous_multiple_event_blobs(self):
        conflicting={**BASE,"name":"Noah Derksen special edition"}
        _,stats=run({"events":[]},{"results":[BASE,conflicting]},TODAY)
        self.assertEqual(stats["approved"],0)

    def test_protect_catalog_and_preserve_event_ids(self):
        concert={"id":"existing-id","name":"Existing","date":"2027-02-06","city":"Hoogeveen","url":"https://www.detamboer.nl/"}
        original={"schema_version":1,"updated_at":"2026-11-19","events":[concert]}
        updated,stats=run(original,{"results":[BASE]},TODAY)
        self.assertEqual(stats["approved"],1)
        self.assertEqual(next(x for x in updated["events"] if x["id"]=="existing-id"),concert)
        self.assertEqual(len(original["events"]),1)

if __name__=="__main__":
    unittest.main()
