#!/usr/bin/env python3
"""Bounded, aggregate-only iNaturalist feasibility audit; not an ecological test."""
import argparse
import collections
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.inaturalist.org/v1/"
DATES = {"d1": "2015-01-01", "d2": "2025-12-31"}
STREAMS = [
    ("mating_project", {"project_id": "mating-behaviour"}, None),
    ("reproductive_project", {"project_id": "reproductive-behavior-of-animals"}, None),
    ("mating_field", {"field:EwA - Behavior Observed": "Mating"}, (12551, "Mating")),
    ("aggregation_field", {"field:Butterflies aggregating/Roosting/mud puddling": "Yes"}, (17428, "Yes")),
    ("mating_text", {"q": "mating", "search_on": "description"}, None),
    ("copulation_text", {"q": "copulating", "search_on": "description"}, None),
    ("puddling_text", {"q": "puddling", "search_on": "description"}, None),
    ("frog_text", {"q": "frog", "search_on": "description"}, None),
    ("toad_text", {"q": "toad", "search_on": "description"}, None),
]

def fetch(endpoint, params):
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "AECO-research-feasibility/0.1 (github.com/zuizui0223/aeco)", "Accept": "application/json"})
    for attempt in range(3):
        try:
            time.sleep(1.2)
            with urllib.request.urlopen(req, timeout=25) as res:
                payload = json.load(res)
            if not isinstance(payload.get("results"), list):
                raise ValueError("Unexpected API payload")
            return payload
        except (OSError, ValueError) as err:
            if attempt == 2:
                raise RuntimeError(str(err)) from err
            time.sleep(2 ** attempt)

def resolve(name, rank):
    payload = fetch("taxa", {"q": name, "rank": rank, "per_page": 30})
    matches = [x for x in payload["results"] if x.get("name") == name and x.get("rank") == rank and x.get("is_active", True)]
    if len(matches) != 1:
        raise ValueError("Could not uniquely resolve taxon " + name)
    return int(matches[0]["id"])

def in_taxon(obs, tid):
    tax = obs.get("taxon") or {}
    return tax.get("id") == tid or tid in (tax.get("ancestor_ids") or [])

def field_matches(obs, target):
    if target is None:
        return None
    fid, val = target
    fields = obs.get("ofvs")
    if fields is None:
        fields = obs.get("observation_field_values")
    if fields is None:
        return None
    for field in fields:
        f = field.get("field_id", field.get("observation_field_id", (field.get("observation_field") or {}).get("id")))
        if str(f) == str(fid) and str(field.get("value", "")).casefold() == val.casefold():
            return True
    return False

def summarize(payload, tid, target):
    rows = payload["results"]
    valid = {int(o["id"]): o for o in rows if o.get("id") is not None and in_taxon(o, tid)}
    states = collections.Counter(str(field_matches(o, target)) for o in valid.values())
    total = payload.get("total_results")
    return {
        "reported_total": total,
        "sample_returned": len(rows),
        "sample_unique_taxon_valid": len(valid),
        "sample_taxon_invalid_or_duplicate": len(rows) - len(valid),
        "sample_field_matches": states.get("True", 0) if target else None,
        "sample_field_mismatches": states.get("False", 0) if target else None,
        "sample_field_metadata_unknown": states.get("None", 0) if target else None,
        "truncated": total > len(rows) if isinstance(total, int) else None,
        "status": "retrieved_candidates_not_reviewed",
    }, set(valid)

def self_test():
    sample = {"total_results": 5, "results": [
        {"id": 1, "taxon": {"id": 9, "ancestor_ids": [7]}, "ofvs": [{"field_id": 12551, "value": "Mating"}]},
        {"id": 1, "taxon": {"id": 9, "ancestor_ids": [7]}, "ofvs": [{"field_id": 12551, "value": "Mating"}]},
        {"id": 2, "taxon": {"id": 9, "ancestor_ids": [7]}, "ofvs": []},
        {"id": 3, "taxon": {"id": 8}, "ofvs": []},
        {"id": 4, "taxon": {"id": 7}},
    ]}
    s, ids = summarize(sample, 7, (12551, "Mating"))
    assert ids == {1, 2, 4}
    assert s["sample_field_matches"] == 1 and s["sample_field_mismatches"] == 1
    assert s["sample_field_metadata_unknown"] == 1 and s["sample_taxon_invalid_or_duplicate"] == 2
    empty, _ = summarize({"total_results": 0, "results": []}, 7, None)
    assert empty["reported_total"] == 0 and empty["truncated"] is False
    print("Synthetic code checks passed; no ecological inference.")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--sample", type=int, default=50, choices=range(1, 201))
    p.add_argument("--output", default="results/inat_audit.json")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    result = {"status": "candidate_availability_only", "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "date_window": DATES, "sample_cap_per_query": args.sample, "queries": [],
              "warning": "Candidate labels are not reviewed mating events; no exposure, causal association or absence inferred."}
    for name, rank in [("Pieridae", "family"), ("Pieris", "genus")]:
        try:
            tid = resolve(name, rank)
        except (RuntimeError, ValueError) as e:
            result["queries"].append({"taxon": name, "status": "taxon_resolution_failed", "error": str(e)})
            continue
        union = set()
        for stream, params, target in STREAMS:
            query = {"taxon_id": tid, "verifiable": "true", "captive": "false", "photos": "true",
                     "per_page": args.sample, "order_by": "id", "order": "asc", **DATES, **params}
            try:
                summary, ids = summarize(fetch("observations", query), tid, target)
                union.update(ids)
            except (RuntimeError, ValueError) as e:
                summary = {"status": "query_failed", "reported_total": None, "error": str(e)}
            result["queries"].append({"taxon": name, "taxon_id": tid, "stream": stream, "params": query, **summary})
        result["queries"].append({"taxon": name, "status": "sample_union_only", "sample_unique_across_streams": len(union)})
    success = sum(x.get("status") == "retrieved_candidates_not_reviewed" for x in result["queries"])
    result["successful_queries"] = success
    result["status"] = "candidate_availability_only" if success == 18 else "incomplete_audit" if success else "api_unavailable"
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(result["status"], "successful queries:", success, "of 18")
    if success == 0:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
