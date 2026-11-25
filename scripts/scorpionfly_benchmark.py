#!/usr/bin/env python3
"""Descriptive transcription audit; not a treatment contrast."""
import json
from pathlib import Path

def summarize(d):
    rows=d["branches"]
    n=sum(r["n"] for r in rows)
    m=sum(r["mated"] for r in rows)
    a=sum(r["n"] for r in rows if r["resource_associated"])
    b=sum(r["mated"] for r in rows if r["resource_associated"])
    if n!=d["n_pairs"] or any(not 0<=r["mated"]<=r["n"] for r in rows):
        raise ValueError("invalid aggregate")
    assert (n,m,a,b)==(40,31,34,27)
    return dict(status="descriptive_published_aggregate_only",source=d["source"],n_pairs=n,
        n_mated=m,resource_branch_pairs=a,resource_associated_matings=b,
        resource_fraction_of_matings=b/m,resource_matings_per_all_pairs=b/n,
        branches=[dict(r,observed_mated_fraction=r["mated"]/r["n"]) for r in rows],
        caveats=d["caveats"])
if __name__=="__main__":
    d=json.loads(Path("data/literature/scorpionfly_mating_branches_v0.8.json").read_text())
    r=summarize(d)
    p=Path("results/scorpionfly_benchmark_v0.8.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(r,indent=2)+"\n")
