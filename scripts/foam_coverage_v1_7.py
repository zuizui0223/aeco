#!/usr/bin/env python3
"""V1.7 coverage census, not a biological effect test.
Only total and annual support queried; never query month facets or calculate temporal direction.
All 408 historical exposed+sheltered candidate cells, including zero and failed queries.
"""
import argparse, hashlib, json, math
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
import pyproj
from foam_temporal_v1_6 import api, taxmap, polygon, facet, KEYS, CL, OLD_SUPPORT, dump

OUT=Path("results/v1.7"); OUT.mkdir(parents=True,exist_ok=True)
YEARS=list(range(2010,2022))
BASE={"year":"2010,2021","month":"1,12","hasCoordinate":"true","hasGeospatialIssue":"false","occurrenceStatus":"PRESENT","basisOfRecord":"HUMAN_OBSERVATION","limit":0}
# Thresholds are frozen before querying. Annual coverage is necessary, not sufficient,
# for a year-month analysis. No outcome-based selection.
MIN_TAX=.8
MIN_TOTAL=30
MIN_ANNUAL=12
MIN_COMMON_YEARS=6
STRONG_ANNUAL=24
MIN_CELLS=20
MIN_BLOCKS=5

def prepare():
    from global_range_v1_4 import load_traits,read_ranges,PROVENANCE
    t=load_traits(); d,_=read_ranges()
    j=d.merge(t[["species","trait_class","family_as_used"]],on="species",validate="many_to_one")
    assert j.species.nunique()==1698
    tr=pyproj.Transformer.from_crs(4326,6933,always_xy=True)
    x,y=tr.transform(j.x.to_numpy(),j.y.to_numpy())
    j["ix"]=np.floor(x/200000).astype(int);j["iy"]=np.floor(y/200000).astype(int)
    u=j[["ix","iy","species","trait_class"]].drop_duplicates()
    g=u.groupby(["ix","iy","trait_class"]).size().unstack(fill_value=0).reset_index()
    g["n_frogs"]=g.drop(columns=["ix","iy"]).sum(axis=1)
    inv=pyproj.Transformer.from_crs(6933,4326,always_xy=True)
    g["lon"],g["lat"]=inv.transform((g.ix+.5)*200000,(g.iy+.5)*200000)
    g["block"]=np.floor((g.lon+180)/30).astype(int).astype(str)+"_"+np.floor((g.lat+90)/20).astype(int).astype(str)
    g=g[g.n_frogs>=5].copy()
    p=g[(g[CL["E"]]>0)&(g[CL["S"]]>0)].copy()
    b=g[(g[CL["E"]]>0)&(g[CL["N"]]>0)].copy()
    assert len(p)==408 and p.block.nunique()==8 and len(b)==921 and b.block.nunique()==26
    old=set(map(tuple,OLD_SUPPORT))
    def old_select(f,tag,n):
        out=[]
        for block,df in f.groupby("block",sort=True):
            records=df.to_dict("records")
            records.sort(key=lambda r:(0 if (r["ix"],r["iy"]) in old else 1,hashlib.sha256(f'v1.6:{tag}:{r["ix"]}:{r["iy"]}'.encode()).hexdigest()))
            out.extend((int(r["ix"]),int(r["iy"])) for r in records[:n])
        return set(out)
    prior=old_select(p,"paired",6)|old_select(b,"broad",2)
    assert len(prior)==90
    # Explicitly mark every previous global temporal sample, not just eligible cells.
    # Untouched cells are a geographic extension; they are not independent of old blocks.
    mapping,tax=taxmap();bycell={k:v for k,v in u.groupby(["ix","iy"])}
    rows=[]
    for r in p.sort_values(["ix","iy"]).to_dict("records"):
        key=(int(r["ix"]),int(r["iy"]))
        groups={}
        for label in ("E","S"):
            ns=sorted(bycell[key].loc[bycell[key].trait_class==CL[label],"species"].unique())
            ks=sorted({mapping[n] for n in ns if n in mapping})
            groups[label]={"range_names":len(ns),"mapped_keys":ks,"unmatched_names":[n for n in ns if n not in mapping]}
        assert not set(groups["E"]["mapped_keys"])&set(groups["S"]["mapped_keys"])
        rows.append({"ix":key[0],"iy":key[1],"lon":float(r["lon"]),"lat":float(r["lat"]),"block":r["block"],"n_frogs":int(r["n_frogs"]),"groups":groups,"previous_temporal_sample":key in prior})
    meta={"status":"coverage_only_frame","n":len(rows),"blocks":p.block.nunique(),"previous_global_temporal_cells_in_frame":sum(r["previous_temporal_sample"] for r in rows),"new_cells":sum(not r["previous_temporal_sample"] for r in rows),"taxonomy":tax,"source_provenance":PROVENANCE,"criteria":{"total_dated_hits_each":MIN_TOTAL,"minimum_taxonomic_fraction":MIN_TAX,"common_years":MIN_COMMON_YEARS,"hits_per_group_per_common_year":MIN_ANNUAL,"strong_hits_per_group_per_common_year":STRONG_ANNUAL,"minimum_new_cells":MIN_CELLS,"minimum_new_blocks":MIN_BLOCKS}}
    dump(OUT/"frame.json",{"meta":meta,"rows":rows});print("COVERAGE_PREP "+json.dumps(meta),flush=True)

def safe_query(base,keys,field,known=None):
    if not keys:return {"status":"unmapped","count":None,"counts":None}
    try:
        d=api("occurrence/search",{**base,"taxonKey":keys,"facet":field,"facetLimit":1000})
        n=int(d["count"]); c=facet(d,field)
        if n<0 or sum(c.values())!=n:raise ValueError("unpartitioned counts: "+field+":"+str((n,sum(c.values()))))
        if known is not None and set(c)-set(known):raise ValueError("unexpected facet keys")
        return {"status":"retrieved","count":n,"counts":c}
    except Exception as e:return {"status":"failed","count":None,"counts":None,"error":repr(e)}

def collect(shard,nshards):
    frame=json.loads((OUT/"frame.json").read_text())
    rows=[r for i,r in enumerate(frame["rows"]) if i%nshards==shard]
    out=OUT/f"coverage_{shard}.jsonl";out.write_text("")
    for i,r in enumerate(rows):
        base={**BASE,"geometry":polygon(r)}
        # Exactly two requests per cell unless an empty frog-key set is known.
        # Species facet verifies E/S disjoint and partitions count; family facet
        # verifies Pieridae vs five other diurnal butterfly families.
        ek=r["groups"]["E"]["mapped_keys"];sk=r["groups"]["S"]["mapped_keys"]
        qf=safe_query(base,ek+sk,"speciesKey",ek+sk)
        qb=safe_query(base,list(KEYS.values()),"familyKey",list(KEYS.values()))
        z={**r,"frog_status":qf["status"],"butterfly_status":qb["status"],"frog_error":qf.get("error"),"butterfly_error":qb.get("error"),"taxE":len(ek)/r["groups"]["E"]["range_names"],"taxS":len(sk)/r["groups"]["S"]["range_names"],"E":None,"S":None,"P":None,"B":None,"E_species_with_hits":None,"S_species_with_hits":None}
        if qf["status"]=="retrieved":
            c=qf["counts"]
            z["E"]=sum(c.get(k,0) for k in ek);z["S"]=sum(c.get(k,0) for k in sk)
            z["E_species_with_hits"]=sum(c.get(k,0)>0 for k in ek);z["S_species_with_hits"]=sum(c.get(k,0)>0 for k in sk)
        if qb["status"]=="retrieved":
            z["P"]=qb["counts"].get(KEYS["Pieridae"],0);z["B"]=qb["count"]-z["P"]
        if qf["status"]!="retrieved" or qb["status"]!="retrieved":z["eligibility"]="query_or_taxon_unavailable"
        elif min(z["taxE"],z["taxS"])<MIN_TAX:z["eligibility"]="taxonomy_below_80pct"
        elif min(z[k] for k in ("E","S","P","B"))<MIN_TOTAL:z["eligibility"]="dated_hits_below_30"
        else:z["eligibility"]="total_support_pass"
        # Necessary bound for 6 years x 12 records each, before annual requests.
        z["annual_candidate"]=z["eligibility"]=="total_support_pass" and min(z[k] for k in ("E","S","P","B"))>=MIN_COMMON_YEARS*MIN_ANNUAL
        with out.open("a") as fh:fh.write(json.dumps(z,ensure_ascii=False,allow_nan=False)+"\n")
        if (i+1)%10==0 or i+1==len(rows):print("COVERAGE_PROGRESS",shard,i+1,len(rows),flush=True)

def load_complete(prefix,expected):
    rows=[]
    for path in sorted(OUT.glob(prefix+"*.jsonl")):
        rows.extend(json.loads(l) for l in path.read_text().splitlines() if l.strip())
    key=lambda r:(r["ix"],r["iy"])
    keys=[key(r) for r in rows];wanted={key(r) for r in expected}
    if len(keys)!=len(set(keys)) or set(keys)!=wanted:raise ValueError("incomplete or duplicate "+prefix+" "+str((len(keys),len(wanted),len(set(keys)&wanted))))
    return sorted(rows,key=key)

def stage1():
    frame=json.loads((OUT/"frame.json").read_text());rows=load_complete("coverage_",frame["rows"])
    candidate=[r for r in rows if r["annual_candidate"]]
    dump(OUT/"annual_frame.json",{"rows":candidate,"n":len(candidate)})
    def report(rs):
        return {"n":len(rs),"blocks":len({r["block"] for r in rs}),"eligibility":dict(Counter(r["eligibility"] for r in rs)),"all_query_success":sum(r["frog_status"]==r["butterfly_status"]=="retrieved" for r in rs),"annual_candidates":sum(r["annual_candidate"] for r in rs),"annual_candidate_blocks":len({r["block"] for r in rs if r["annual_candidate"]}),"total_supported_blocks":len({r["block"] for r in rs if r["eligibility"]=="total_support_pass"}),"below30_by_group":{k:sum(r[k] is not None and r[k]<MIN_TOTAL for r in rs) for k in ("E","S","P","B")},"zero_by_group":{k:sum(r[k]==0 for r in rs) for k in ("E","S","P","B")},"dated_hits":{k:sum(r[k] for r in rs if r[k] is not None) for k in ("E","S","P","B")}}
    meta={"status":"total_dated_support_census","frame":frame["meta"],"all":report(rows),"previous":report([r for r in rows if r["previous_temporal_sample"]]),"untouched":report([r for r in rows if not r["previous_temporal_sample"]]),"by_block":{b:report([r for r in rows if r["block"]==b]) for b in sorted({r["block"] for r in rows})},"errors":dict(Counter(str(r[k]) for r in rows for k in ("frog_error","butterfly_error") if r[k]))}
    # Keep all rows as aggregated counts and coarse cell keys.
    dump(OUT/"coverage_summary.json",meta)
    print("COVERAGE_RESULT "+json.dumps(meta,ensure_ascii=False,allow_nan=False),flush=True)

def annual(shard,nshards):
    frame=json.loads((OUT/"annual_frame.json").read_text())
    rows=[r for i,r in enumerate(frame["rows"]) if i%nshards==shard]
    out=OUT/f"annual_{shard}.jsonl";out.write_text("")
    for i,r in enumerate(rows):
        base={**BASE,"geometry":polygon(r)}
        queries={"E":r["groups"]["E"]["mapped_keys"],"S":r["groups"]["S"]["mapped_keys"],"P":[KEYS["Pieridae"]],"B":[v for k,v in KEYS.items() if k!="Pieridae"]}
        year={k:safe_query(base,ks,"year",YEARS) for k,ks in queries.items()}
        z={**r,"annual":year,"common_years_12":None,"common_years_24":None,"annual_status":"failed"}
        if all(a["status"]=="retrieved" for a in year.values()):
            # Live-index change between stages is reported, not silently accepted.
            if any(year[k]["count"]!=r[k] for k in queries):
                z["annual_status"]="index_count_changed"
            else:
                z["annual_status"]="retrieved"
                z["common_years_12"]=[y for y in YEARS if min(year[k]["counts"].get(y,0) for k in queries)>=MIN_ANNUAL]
                z["common_years_24"]=[y for y in YEARS if min(year[k]["counts"].get(y,0) for k in queries)>=STRONG_ANNUAL]
        with out.open("a") as fh:fh.write(json.dumps(z,ensure_ascii=False,allow_nan=False)+"\n")
        if (i+1)%5==0 or i+1==len(rows):print("ANNUAL_PROGRESS",shard,i+1,len(rows),flush=True)

def finish():
    frame=json.loads((OUT/"annual_frame.json").read_text());coverage=json.loads((OUT/"coverage_summary.json").read_text())
    rows=load_complete("annual_",frame["rows"])
    def summary(rs):
        passed=[r for r in rs if r["annual_status"]=="retrieved" and len(r["common_years_12"])>=MIN_COMMON_YEARS]
        stronger=[r for r in rs if r["annual_status"]=="retrieved" and len(r["common_years_24"])>=MIN_COMMON_YEARS]
        return {"n":len(rs),"status":dict(Counter(r["annual_status"] for r in rs)),"passes_12":len(passed),"blocks_12":len({r["block"] for r in passed}),"passes_24":len(stronger),"blocks_24":len({r["block"] for r in stronger}),"cell_years_12":sum(len(r["common_years_12"]) for r in passed)}
    new=[r for r in rows if not r["previous_temporal_sample"]]
    selected=[r for r in new if r["annual_status"]=="retrieved" and len(r["common_years_12"])>=MIN_COMMON_YEARS]
    # All passing previously unsampled cells, not post hoc ranked by direction.
    holdout=[{"ix":r["ix"],"iy":r["iy"],"block":r["block"],"common_years_12":r["common_years_12"],"common_years_24":r["common_years_24"]} for r in selected]
    dump(OUT/"frozen_new_annual_support.json",{"rows":holdout})
    m={"status":"annual_support_gate_only","coverage":coverage,"annual_all":summary(rows),"annual_previous":summary([r for r in rows if r["previous_temporal_sample"]]),"annual_untouched":summary(new),"new_blocks_with_annual_support":sorted({r["block"] for r in selected}),"year_month_gate":len(selected)>=MIN_CELLS and len({r["block"] for r in selected})>=MIN_BLOCKS,"limitations":["Annual record coverage is necessary, not sufficient for monthly analysis. No joint year-month outcomes, seasonal direction, climate correction, or foam/mating/fertilization inference.","Prior unsampled cells share geographic blocks and are not independent continent-level replications.","Range taxa are exact accepted-name matches from an historical distribution panel; absence from mapped records is not biological absence.","Live GBIF index counts and date filters are snapshots; mismatches retained."]}
    dump(OUT/"summary.json",m)
    compact={k:v for k,v in m.items() if k!="coverage"}
    print("ANNUAL_RESULT "+json.dumps(compact,ensure_ascii=False,allow_nan=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("task",choices=["prepare","collect","stage1","annual","finish"]);p.add_argument("--shard",type=int,default=0);p.add_argument("--nshards",type=int,default=6);a=p.parse_args()
    if a.task=="prepare":prepare()
    elif a.task=="collect":collect(a.shard,a.nshards)
    elif a.task=="stage1":stage1()
    elif a.task=="annual":annual(a.shard,a.nshards)
    else:finish()
