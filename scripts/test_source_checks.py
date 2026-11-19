#!/usr/bin/env python3
"""Offline deterministic tests: no false cancellations or invented status."""
import unittest
from check_sources import JsonLd, matching_schema, evaluate, build, is_direct

CONCERT={
 "id":"artist-20261219","name":"The Artist","date":"2026-12-19",
 "venue":"Test Hall","city":"Groningen","url":"https://venue.example/programma/the-artist/",
 "link_status":"event_page"
}
def jsonld(date="2026-12-19",status=None,name="The Artist",url=None):
 import json
 data={"@context":"https://schema.org","@type":"MusicEvent","name":name,"startDate":date,
       "url":url or CONCERT["url"]}
 if status:data["eventStatus"]="https://schema.org/"+status
 parser=JsonLd()
 parser.feed('<script type="application/ld+json">'+json.dumps(data)+'</script>')
 return parser.blocks
NOW="2026-11-19T22:00:00+00:00"

class MonitorTests(unittest.TestCase):
 def test_confirm(self):
  self.assertEqual(evaluate(CONCERT,jsonld(),NOW)["state"],"confirmed")
 def test_explicit_cancellation(self):
  self.assertEqual(evaluate(CONCERT,jsonld(status="EventCancelled"),NOW)["state"],"cancelled")
 def test_date_change(self):
  self.assertEqual(evaluate(CONCERT,jsonld(date="2026-12-20"),NOW)["state"],"changed")
 def test_no_cancel_on_missing_event_data(self):
  self.assertEqual(evaluate(CONCERT,[],NOW)["state"],"unavailable")
 def test_ignore_unrelated_schema(self):
  self.assertEqual(evaluate(CONCERT,jsonld(name="Other Band"),NOW)["state"],"unavailable")
 def test_ignore_wrong_page(self):
  self.assertEqual(evaluate(CONCERT,jsonld(url="https://venue.example/programma/other-band/"),NOW)["state"],"unavailable")
 def test_bad_url(self):
  self.assertFalse(is_direct("https://venue.example/"))
 def test_page_unavailable_stays_neutral(self):
  def error(_):raise TimeoutError("No response")
  output=build([CONCERT],{},error,NOW)
  self.assertEqual(output["checks"][CONCERT["id"]]["state"],"unavailable")
  self.assertEqual(output["alerts"],[])
 def test_change_alert_is_specific(self):
  output=build([CONCERT],{},lambda _:jsonld(date="2026-12-21"),NOW)
  self.assertEqual(len(output["alerts"]),1)
  self.assertIn("2026-12-21",output["alerts"][0]["fingerprint"])
 def test_missing_future_event_ignored(self):
  past={**CONCERT,"date":"2026-01-01"}
  out=build([past],{},lambda _:jsonld(),NOW)
  self.assertEqual(out["checked_count"],0)

if __name__=="__main__":unittest.main()
