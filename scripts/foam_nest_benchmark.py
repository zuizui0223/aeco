#!/usr/bin/env python3
"""AECO v0.6: descriptive frog foam-nest literature benchmark."""
import json
from datetime import date
from pathlib import Path
from statistics import median

def day(s):
    month, d = map(int, s.split("-"))
    return date(2000, month, d)

def describe(values):
    return {"n": len(values), "min": min(values), "median": median(values), "max": max(values)} if values else {"n":0,"min":None,"median":None,"max":None}

def analyze(d):
    natural=[dict(x,total=x["arboreal"]+x["terrestrial"],terrestrial_fraction=x["terrestrial"]/(x["arboreal"]+x["terrestrial"])) for x in d["natural_counts"]]
    t=sum(x["total"] for x in natural)
    n=sum(x["terrestrial"] for x in natural)
    experiment=d["experiment"]
    if len({x["id"] for x in experiment})!=len(experiment):
        raise ValueError("duplicate nest id")
    days=[dict(id=x["id"],placement=x["placement"],uncertain_construction=x["uncertain_construction"],discovery_to_reported_hatching_days=(day(x["hatching"])-day(x["discovery"])).days) for x in experiment if x["hatching"] is not None]
    assert (t,n,len(experiment),len(days))==(132,17,10,9)
    assert all(x["discovery_to_reported_hatching_days"]>=0 for x in days)
    v=lambda subset:[x["discovery_to_reported_hatching_days"] for x in subset]
    return {"status":"descriptive_published_nest_data_only","natural_placement_by_year":natural,
            "natural_total":t,"natural_terrestrial":n,"natural_terrestrial_fraction":n/t,
            "year_difference_percentage_points":100*(natural[0]["terrestrial_fraction"]-natural[1]["terrestrial_fraction"]),
            "experimental_nests":len(experiment),"missing_hatch_endpoint":len(experiment)-len(days),
            "discovery_to_reported_hatching_days":describe(v(days)),
            "excluding_uncertain_construction_dates":describe(v([x for x in days if not x["uncertain_construction"]])),
            "by_experimental_placement":{p:describe(v([x for x in days if x["placement"]==p])) for p in ("arboreal","terrestrial")},
            "nest_intervals":days,"caveats":d["caveats"]}
if __name__=="__main__":
    d=json.loads(Path("data/literature/foam_nest_placement_tables_v0.6.json").read_text())
    result=analyze(d)
    assert result["discovery_to_reported_hatching_days"]=={"n":9,"min":8,"median":13,"max":24}
    assert result["excluding_uncertain_construction_dates"]=={"n":6,"min":10,"median":13,"max":24}
    out=Path("results/foam_nest_benchmark_v0.6.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(out)
