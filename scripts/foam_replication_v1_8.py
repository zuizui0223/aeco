#!/usr/bin/env python3
"""Pre-outcome frozen 25-cell pooled-month replication diagnostic.
Never changes the selected cells based on observed monthly profiles. Not a year-month
model, a climate-adjusted causal estimate, or an observed reproductive outcome."""
import argparse, hashlib, itertools, json
from collections import Counter
from pathlib import Path
import numpy as np
from foam_temporal_v1_6 import KEYS, polygon, safe, eligible, contrasts, overlap, dump
OUT=Path("results/v1.8"); OUT.mkdir(parents=True,exist_ok=True)
FROZEN=Path("data/frozen/foam_pooled_month_v1.8.json")
OLD=Path("results/global_foam_coverage_v1.7_frozen_pooled_month_candidates.json")
BASE={"year":"2010,2021","month":"1,12","hasCoordinate":"true","hasGeospatialIssue":"false","occurrenceStatus":"PRESENT","basisOfRecord":"HUMAN_OBSERVATION"}
GROUPS=("E","S","P","B")
MIN_CELLS=20
MIN_BLOCKS=5

def frame():
    f=json.loads(FROZEN.read_text()); old=json.loads(OLD.read_text())
    rows=f["rows"]; keys=lambda r:(r["ix"],r["iy"])
    assert len(rows)==len(set(map(keys,rows)))==25
    assert Counter(r["block"] for r in rows)==Counter(old["block_counts"])
    assert f["source_zip_sha256"]==old["source_artifact_sha256"]
    for r,o in zip(rows,old["rows"]):
        assert keys(r)==keys(o) and r["block"]==o["block"]
        assert all(r["expected"][k]==o[k] for k in GROUPS)
        assert o["taxE"]==o["taxS"]==1
        e,s=[r["groups"][k]["mapped_keys"] for k in ("E","S")]
        assert e and s and len(e)==len(set(e)) and len(s)==len(set(s)) and not set(e)&set(s)
    return rows

def collect(shard,nshards):
    rows=[r for i,r in enumerate(frame()) if i%nshards==shard]
    path=OUT/f"shard_{shard}.jsonl";path.write_text("")
    for i,r in enumerate(rows):
        b={**BASE,"geometry":polygon(r)}
        keys={"E":r["groups"]["E"]["mapped_keys"],"S":r["groups"]["S"]["mapped_keys"],
              "P":[KEYS["Pieridae"]],"B":[v for k,v in KEYS.items() if k!="Pieridae"],"B_all":list(KEYS.values())}
        z={**r}
        for k,ids in keys.items():
            z[k]=safe(b,ids,k in ("E","S"))
        z["all_retrieved"]=all(z[k]["status"]=="retrieved" for k in keys)
        z["dated_partition_ok"]=False
        z["matches_coverage_counts"]=False
        z["butterfly_partition_ok"]=False
        if z["all_retrieved"]:
            z["dated_partition_ok"]=all(sum(z[k]["months"])==z[k]["hits"] for k in keys)
            z["matches_coverage_counts"]=all(z[k]["hits"]==r["expected"][k] for k in GROUPS)
            z["butterfly_partition_ok"]=(z["P"]["hits"]+z["B"]["hits"]==z["B_all"]["hits"] and np.array_equal(np.asarray(z["P"]["months"])+np.asarray(z["B"]["months"]),z["B_all"]["months"]))
        with path.open("a") as fh:fh.write(json.dumps(z,ensure_ascii=False,allow_nan=False)+"\n")
        print("REPLICATION_PROGRESS",shard,i+1,len(rows),flush=True)

def block_summary(rows,field):
    if not rows:return {"n":0,"blocks":0,"status":"no_eligible_pairs"}
    blocks=sorted({r["block"] for r in rows})
    b=np.array([np.mean([r[field] for r in rows if r["block"]==k]) for k in blocks])
    k=len(b);n=len(rows);mu=float(b.mean())
    out={"n":n,"blocks":k,"status":"exploratory_support_gate_pass" if n>=MIN_CELLS and k>=MIN_BLOCKS else "insufficient_support_descriptive_only",
         "block_balanced_mean":mu,"cell_mean":float(np.mean([r[field] for r in rows])),
         "positive_blocks":int(sum(b>0)),"negative_blocks":int(sum(b<0)),
         "block_means":{x:float(v) for x,v in zip(blocks,b)},
         "block_sizes":{x:sum(r["block"]==x for r in rows) for x in blocks}}
    if k>=2:
        out["leave_one_block_out"]={x:float(np.delete(b,i).mean()) for i,x in enumerate(blocks)}
        rng=np.random.default_rng(20261125)
        v=b[rng.integers(0,k,(10000,k))].mean(axis=1)
        out["descriptive_block_bootstrap_interval_95"]=np.quantile(v,[.025,.975]).tolist()
        # Diagnostic conditional on exchangeable independent symmetric block effects;
        # not a valid general causal null under shared climate or species ranges.
        null=np.array([np.mean(b*np.asarray(s)) for s in itertools.product((-1,1),repeat=k)])
        out["sign_flip_diagnostic_two_sided_p"]=float(np.mean(np.abs(null)>=abs(mu)-1e-12))
        out["sign_flip_diagnostic_one_sided_positive_p"]=float(np.mean(null>=mu-1e-12))
        out["sign_flip_patterns"]=len(null)
    return out

def analyze():
    rows=[]
    for p in sorted(OUT.glob("shard_*.jsonl")):
        rows.extend(json.loads(l) for l in p.read_text().splitlines() if l.strip())
    ids=[(r["ix"],r["iy"]) for r in rows]; expected={(r["ix"],r["iy"]) for r in frame()}
    if len(ids)!=len(set(ids)) or set(ids)!=expected:raise ValueError("incomplete/duplicate frozen cells")
    attr=Counter();valid=[];current_index=[]
    for r in rows:
        if not r["all_retrieved"]:attr["query_failed"]+=1;continue
        if not r["dated_partition_ok"] or not r["butterfly_partition_ok"]:attr["partition_failed"]+=1;continue
        if not all(eligible(r[k]) for k in GROUPS):attr["monthly_support_failed"]+=1;continue
        z={k:r[k] for k in ("ix","iy","block","matches_coverage_counts")}
        z.update(hits={k:r[k]["hits"] for k in GROUPS},dominanceE=r["E"]["max_species_share"],dominanceS=r["S"]["max_species_share"],speciesE=r["E"]["species_with_hits"],speciesS=r["S"]["species_with_hits"],**contrasts(r,"S"))
        current_index.append(z)
        if not r["matches_coverage_counts"]:attr["index_count_changed"]+=1;continue
        valid.append(z)
    attr["eligible_primary"]=len(valid)
    fields=("directional_D","D0","Dplus1","Dminus1","Dplus1_minus_D0")
    result={"status":"pooled_month_replication_diagnostic_not_fertility","frozen_sha256":hashlib.sha256(FROZEN.read_bytes()).hexdigest(),"n_frozen":25,"n_completed":len(rows),"n_all_retrieved":sum(r["all_retrieved"] for r in rows),"n_exact_count_match":sum(r["matches_coverage_counts"] for r in rows),"attrition":dict(attr),
      "total_dated_hits":{k:sum(r[k]["hits"] for r in rows if r[k]["status"]=="retrieved") for k in GROUPS},
      "primary":block_summary(valid,"directional_D"),"secondary":{f:block_summary(valid,f) for f in fields[1:]},
      "sensitivity_50_each":block_summary([r for r in valid if min(r["hits"].values())>=50],"directional_D"),
      "sensitivity_dominance80":block_summary([r for r in valid if max(r["dominanceE"],r["dominanceS"])<=.8],"directional_D"),
      "sensitivity_two_observed_frog_species_each":block_summary([r for r in valid if min(r["speciesE"],r["speciesS"])>=2],"directional_D"),
      "sensitivity_current_index":block_summary(current_index,"directional_D"),
      "previous_v1_6_paired":{"n":5,"blocks":3,"block_balanced_mean":.051383787128295964,"status":"previous_underpowered_discovery"},
      "limits":["Prior-unsampled cells but shared geographic blocks and overlapping species; no independent continental replication.",
                "Pooled calendar-month observations, not joint year-month, climate anomalies, actual frog breeding or recipient mating/fertilization.",
                "Original provisional exposure types, no-ground sensitivity not identified by these queries.",
                "Species and observer sampling bias; block bootstrap and sign flips descriptive with at most five blocks.",
                "Exact expected-count gate separates live-index drift. No sample replacement."]}
    dump(OUT/"cell_contrasts.json",valid);dump(OUT/"summary.json",result)
    print("REPLICATION_RESULT "+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)

def test():
    assert overlap([1]+[0]*11,[0,1]+[0]*10,1)==1
    a=[1]+[0]*11;b=[0,1]+[0]*10
    r={"E":{"months":a},"S":{"months":[1]*12},"P":{"months":b},"B":{"months":[1]*12}}
    q=contrasts(r,"S")
    assert q["directional_D"]>0
    r["S"]=r["E"];assert all(abs(v)<1e-12 for k,v in contrasts(r,"S").items() if k.startswith("D") or k=="directional_D")
    m=block_summary([{"block":"a","directional_D":.1},{"block":"b","directional_D":-.1}],"directional_D")
    assert m["block_balanced_mean"]==0 and m["sign_flip_diagnostic_two_sided_p"]==1
    print("frozen frame and statistic checks",len(frame()))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("task",choices=["test","collect","analyze"]);p.add_argument("--shard",type=int,default=0);p.add_argument("--nshards",type=int,default=3);a=p.parse_args()
    if a.task=="test":test()
    elif a.task=="collect":collect(a.shard,a.nshards)
    else:analyze()
