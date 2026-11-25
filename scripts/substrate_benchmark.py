#!/usr/bin/env python3
"""AECO v0.5 published table arithmetic; not a new field experiment."""
import json
from pathlib import Path

def analyze(d):
    t1,t4,t5=d["table1"],d["table4"],d["table5"]
    male=sum(x["male_weight"] for x in t1)
    female=sum(x["female_weight"] for x in t1)
    n=male+female
    total_salt=sum(x["n"] for x in t4)
    low_salt=sum(x["n"] for x in t4 if x["mM"]<=10)
    non_feed=sum(x["feeding"] for x in t5)
    non_total=sum(x["feeding"]+x["sampling_only"] for x in t5)
    salt=d["text_salt_feeding"]
    assert (male,female,n,total_salt,low_salt,non_feed,non_total)==(67,7,74,66,41,4,36)
    assert salt["feeding"]==total_salt
    return {"status":"descriptive_published_aggregate_reanalysis",
            "source":d["source"],"natural_substrate_total_weight":n,
            "female_total_weight":female,"female_fraction":female/n,
            "natural_substrates":[dict(x,total_weight=x["male_weight"]+x["female_weight"],
              female_fraction=(x["female_weight"]/(x["male_weight"]+x["female_weight"]) if x["male_weight"]+x["female_weight"] else None)) for x in t1],
            "low_salt_1_10mM_fraction":low_salt/total_salt,
            "salt_feeding_given_observation":salt["feeding"]/salt["total_observed"],
            "non_salt_feeding_given_observation":non_feed/non_total,
            "descriptive_feeding_fraction_ratio":(salt["feeding"]/salt["total_observed"])/(non_feed/non_total),
            "caveats":d["caveats"]}
if __name__=="__main__":
    d=json.loads(Path("data/literature/boggs_dau_2004_tables.json").read_text())
    out=Path("results/substrate_benchmark_v0.5.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(analyze(d),indent=2)+"\n")
    print(out)
