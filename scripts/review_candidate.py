#!/usr/bin/env python3
"""Stage a human-selected ConcertRadar discovery as a reviewed PR change.

Only the repository owner can initiate the GitHub workflow. This script never
publishes an uncertain candidate to main. It validates against recent extracted
official schema metadata and writes the catalog on the workflow's PR branch.
"""
import argparse
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path

from promote_verified_concerts import eligible, run, simple_url

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data/new-discoveries.json"
REVIEW = ROOT / "data/event-review.json"
CATALOG = ROOT / "data/concerts.json"
ID = re.compile(r"^suggestion-\d{4}-\d{2}-\d{2}-[a-z0-9-]{2,80}$")
ISSUE = re.compile(r"(?m)^ConcertRadar-ID:\s*(suggestion-\d{4}-\d{2}-\d{2}-[a-z0-9-]{2,80})\s*$")
CITY_SOURCE = "venue_location"


def candidate_id(explicit="", issue_text=""):
    value = explicit.strip() if explicit else ""
    if not value:
        match = ISSUE.search(issue_text or "")
        value = match.group(1) if match else ""
    if not ID.fullmatch(value):
        raise ValueError("No valid ConcertRadar-ID in the approved workflow input or issue body")
    return value


def stage(candidates, review, catalog, selected_id, now):
    matches = [row for row in candidates.get("events", []) if row.get("id") == selected_id]
    if len(matches) != 1:
        raise ValueError("Candidate not found uniquely in current published discovery feed")
    candidate = matches[0]
    if candidate.get("date", "") < now.date().isoformat():
        raise ValueError("Concert date is in the past")
    if candidate.get("verification") not in (None, "candidate_unverified"):
        raise ValueError("Cannot review a non-candidate record")
    try:
        timestamp = datetime.fromisoformat(review["generated_at"].replace("Z", "+00:00"))
        age = (now - timestamp).total_seconds()
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise ValueError("No valid extraction timestamp") from error
    if not 0 <= age < 48 * 3600:
        raise ValueError("Extracted metadata is older than 48 hours; run a fresh venue scan")
    matching_rows = [r for r in review.get("results", [])
                     if simple_url(r.get("source_url")) == simple_url(candidate.get("url"))
                     and r.get("name") == candidate.get("name")
                     and str(r.get("date") or "")[:10] == candidate.get("date")]
    all_rows = [r for r in review.get("results", [])
                if simple_url(r.get("source_url")) == simple_url(candidate.get("url"))]
    if len(matching_rows) != 1 or len(all_rows) != 1:
        raise ValueError("Event metadata is ambiguous or no longer matches the discovery")
    verified = dict(matching_rows[0])
    if not verified.get("city") and candidate.get("city_source") == CITY_SOURCE:
        verified["city"] = candidate.get("city", "")
    event, reason = eligible(verified, now.date())
    if reason:
        raise ValueError("Not eligible for strict schema-verified admission: " + reason)
    updated, stats = run(catalog, {"results": [verified]}, now.date())
    if stats["approved"] != 1:
        raise ValueError("Duplicate or invalid event: " + repr(stats["skipped"]))
    added = stats["added"][0]
    if added["id"] != selected_id:
        raise ValueError("Candidate ID differs from strict admission ID")
    # Staged records cannot silently acquire a fabricated genre, taste score or
    # live ticket quote. Standard provenance remains explicit.
    return updated, added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-id", default=os.environ.get("REVIEW_INPUT", ""))
    args = parser.parse_args()
    selected = candidate_id(args.candidate_id, os.environ.get("REVIEW_BODY", ""))
    discoveries = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    updated, added = stage(discoveries, review, catalog, selected, datetime.now(timezone.utc))
    CATALOG.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PR review staged (not merged): " + json.dumps(added, ensure_ascii=False))


if __name__ == "__main__":
    main()
