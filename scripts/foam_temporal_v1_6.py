#!/usr/bin/env python3
"""Monthly-climatology pilot, v1.6. Ordinary occurrence vs independently calling-source comparison.
No actual foam counts, mating records, or fertilization inference."""
import argparse,hashlib,json,math,re,time,urllib.error,urllib.parse,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import pyproj

OUT=Path("results/v1.6")
OUT.mkdir(parents=True,exist_ok=True)
KEYS={"Hesperiidae":6953,"Papilionidae":9417,"Pieridae":5481,"Nymphalidae":7017,"Lycaenidae":5473,"Riodinidae":1933999}
BACKBONE="d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
FROGID="47c9fee2-619a-481c-a114-386bc4748256"
OLD_SUPPORT=[[-60,22],[-60,28],[-54,17],[-53,15],[-52,15],[-52,16],[-48,14],[-48,21],[-44,8],[-40,14],[-38,14],[-38,29],[-37,12],[-35,-22],[-35,-19],[-35,25],[-32,-19],[-30,-19],[-30,6],[-29,27],[-28,2],[-27,-19],[-26,-18],[-26,-17],[-24,-16],[-9,8],[-3,23],[-2,5],[-2,21],[-1,3],[4,4],[10,-21],[11,-21],[11,-8],[12,-16],[13,-18],[13,-16],[14,-20],[14,-19],[14,-18],[14,-16],[14,31],[15,-19],[22,-16],[22,-14],[22,29],[23,-10],[37,6],[37,19],[41,13],[43,15],[50,1],[53,17],[54,-16],[55,-21],[55,17],[56,-21],[58,15],[58,19],[60,0],[61,16],[62,-10],[66,-21],[66,21],[67,21],[67,22],[68,-21],[70,-10],[72,-21],[74,-17],[85,-23]]
CL={"E":"froth_potentially_exposed","S":"froth_sheltered","N":"no_documented_froth_or_bubble"}
LAST=0.;CALLS=0
def api(path,params):
    global LAST,CALLS
    url="https://api.gbif.org/v1/"+path+"?"+urllib.parse.urlencode(params,doseq=True)
    for i in range(3):
        time.sleep(max(0.,1.0-(time.monotonic()-LAST)))
        LAST=time.monotonic();CALLS+=1
        try:
            r=urllib.request.Request(url,headers={"User-Agent":"AECO seasonal research/1.6 (https://github.com/zuizui0223/aeco)","Accept":"application/json"})
            with urllib.request.urlopen(r,timeout=25) as response:b=response.read(12_000_001)
            if len(b)>12_000_000:raise ValueError("API response cap")
            return json.loads(b)
        except (OSError,ValueError) as e:
            if i==2:raise
            delay=2**(i+1)
            if isinstance(e,urllib.error.HTTPError) and e.code==429:
                try:delay=max(delay,min(60,int(e.headers.get("Retry-After","5"))))
                except ValueError:pass
            time.sleep(delay)
def dump(path,ob):
    Path(path).write_text(json.dumps(ob,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def taxmap():
    m=api("species/match",{"name":"Anura","rank":"ORDER","strict":"true"})
    assert m.get("matchType")=="EXACT" and m.get("rank")=="ORDER",m
    k=m["usageKey"]; seen={};total=None;off=0
    for _ in range(60):
        a=api("species/search",{"higherTaxonKey":k,"datasetKey":BACKBONE,"rank":"SPECIES","status":"ACCEPTED","limit":1000,"offset":off})
        if total is None:total=int(a["count"])
        if int(a["count"])!=total:raise ValueError("taxonomic list count changed")
        rows=a.get("results",[])
        if not rows and off<total:raise ValueError("empty taxonomy page")
        for r in rows:
            if r.get("rank")!="SPECIES" or r.get("taxonomicStatus")!="ACCEPTED" or r.get("order")!="Anura":
                raise ValueError("taxonomy filter failed "+str({x:r.get(x) for x in ("rank","taxonomicStatus","order","canonicalName")}))
            key=int(r["key"])
            if key in seen:raise ValueError("duplicate page key")
            seen[key]=r.get("canonicalName","")
        off+=len(rows)
        if off>=total or a.get("endOfRecords"):break
    if len(seen)!=total or not 3000<=total<=20000:raise ValueError("incomplete accepted Anura taxonomy: "+str((len(seen),total)))
    names=defaultdict(list)
    for k,n in seen.items():names[n].append(k)
    return {n:ks[0] for n,ks in names.items() if len(ks)==1}, {"accepted_species_keys":total,"ambiguous_names":sum(len(ks)>1 for ks in names.values()),"order_key":m["usageKey"]}
def prepare():
    from global_range_v1_4 import load_traits,read_ranges,PROVENANCE
    t=load_traits();d,_=read_ranges()
    j=d.merge(t[["species","trait_class","family_as_used"]],on="species",validate="many_to_one")
    assert j.species.nunique()==1698
    tr=pyproj.Transformer.from_crs(4326,6933,always_xy=True)
    x,y=tr.transform(j.x.to_numpy(),j.y.to_numpy())
    j["ix"]=np.floor(x/200000).astype(int);j["iy"]=np.floor(y/200000).astype(int)
    u=j[["ix","iy","species","trait_class","family_as_used"]].drop_duplicates()
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
    def select(f,tag,n):
        out=[]
        for block,df in f.groupby("block",sort=True):
            records=df.to_dict("records")
            # Use prior total observation support only; never Pieridae share/coefficients.
            records.sort(key=lambda r:(0 if (r["ix"],r["iy"]) in old else 1,hashlib.sha256(f'v1.6:{tag}:{r["ix"]}:{r["iy"]}'.encode()).hexdigest()))
            out.extend(records[:n])
        return out
    paired=select(p,"paired",6);broad=select(b,"broad",2)
    au=select(b[b.lon.between(112,154)&b.lat.between(-44,-10)],"calling_AU",4)
    target={}
    for label,rows in [("paired",paired),("broad",broad),("calling_AU",au)]:
        for r in rows:
            key=(int(r["ix"]),int(r["iy"]),"calling" if label=="calling_AU" else "global")
            if key not in target:target[key]={"ix":key[0],"iy":key[1],"source":key[2],"block":r["block"],"lon":r["lon"],"lat":r["lat"],"cohorts":[],"prior_total_support":(key[0],key[1]) in old}
            target[key]["cohorts"].append(label)
    # Accepted exact-name mapping only; no inference for missing taxonomy.
    mapping,tax=taxmap()
    bycell={k:df for k,df in u.groupby(["ix","iy"])}
    rows=[]
    for key,r in sorted(target.items()):
        df=bycell[key[:2]]
        classes={}
        for k,v in CL.items():
            ns=sorted(df.loc[df.trait_class==v,"species"].unique().tolist())
            ks=sorted(set(mapping[n] for n in ns if n in mapping))
            classes[k]={"range_names":len(ns),"mapped_keys":ks,"unmatched_names":[n for n in ns if n not in mapping]}
        if any(set(classes[a]["mapped_keys"])&set(classes[b]["mapped_keys"]) for a,b in [("E","S"),("E","N"),("S","N")]):raise ValueError("cross-class key conflict")
        r["groups"]=classes;rows.append(r)
    meta={"status":"prequery_sample","frame_broad":len(b),"frame_paired":len(p),"broad_blocks":int(b.block.nunique()),"paired_blocks":int(p.block.nunique()),"cohort_sizes":{tag:sum(tag in r["cohorts"] for r in rows) for tag in ["broad","paired","calling_AU"]},"n_grid_source_pairs":len(rows),"global_taxonomy":tax,"matched_range_species_in_backbone":int(t[t.species.isin(set(j.species))].species.isin(mapping).sum()),"source_provenance":PROVENANCE,"design":"six paired per block, two broad per block, four calling-region per block; prior total observation support then deterministic SHA order. 2010–2021 global, 2018–2021 FrogID-AU. Not representative grid census."}
    dump(OUT/"sample.json",{"meta":meta,"rows":rows})
    print("TEMPORAL_PREP "+json.dumps(meta,ensure_ascii=False),flush=True)
def polygon(r):
    inv=pyproj.Transformer.from_crs(6933,4326,always_xy=True)
    x0,y0=inv.transform(r["ix"]*200000,r["iy"]*200000)
    x1,y1=inv.transform((r["ix"]+1)*200000,(r["iy"]+1)*200000)
    assert -180<=x0<x1<=180 and -90<=y0<y1<=90
    return "POLYGON(("+",".join(f"{x:.7f} {y:.7f}" for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)])+"))"
def facet(d,field):
    wanted=re.sub(r"[^a-z]","",field.lower())
    found=[f for f in d.get("facets",[]) if re.sub(r"[^a-z]","",str(f.get("field","")).lower())==wanted]
    if not found and d.get("count")==0:return {}
    if len(found)!=1:raise ValueError("missing facet "+field)
    a={}
    for z in found[0]["counts"]:
        k=int(z["name"]);n=int(z["count"])
        if k in a or n<=0:raise ValueError("invalid facet")
        a[k]=n
    return a
def query_month(base,keys,verify_species=False):
    if not keys:return {"status":"no_mapped_taxa","hits":None,"months":None}
    months=np.zeros(12,dtype=np.int64);total=0;sp=Counter()
    for start in range(0,len(keys),50):
        chunk=keys[start:start+50]
        d=api("occurrence/search",{**base,"taxonKey":chunk,"limit":0,"facet":["month","speciesKey"] if verify_species else "month","facetLimit":1000})
        n=int(d["count"]);m=facet(d,"month")
        if set(m)-set(range(1,13)) or sum(m.values())>n:raise ValueError("invalid months")
        if verify_species:
            s=facet(d,"speciesKey")
            if set(s)-set(chunk) or sum(s.values())!=n:raise ValueError("taxon filter or species resolution failed")
            sp.update(s)
        total+=n
        for k,v in m.items():months[k-1]+=v
    return {"status":"retrieved","hits":total,"months":months.tolist(),"month_coverage":float(months.sum()/total) if total else None,"species_with_hits":len(sp) if verify_species else None,"max_species_share":max(sp.values())/total if sp and total else None}
def safe(base,keys,verify=False):
    try:return query_month(base,keys,verify)
    except Exception as e:return {"status":"query_failed","error":repr(e),"hits":None,"months":None}
def collect(shard,nshards):
    src=json.loads((OUT/"sample.json").read_text());out=OUT/f"shard_{shard}.jsonl";out.write_text("")
    subset=[r for i,r in enumerate(src["rows"]) if i%nshards==shard]
    for i,r in enumerate(subset):
        base={"year":"2018,2021" if r["source"]=="calling" else "2010,2021","hasCoordinate":"true","hasGeospatialIssue":"false","occurrenceStatus":"PRESENT","basisOfRecord":"HUMAN_OBSERVATION","geometry":polygon(r)}
        if r["source"]=="calling":base["country"]="AU"
        res={**r}
        # Support screen depends on all butterfly hits, not Pieridae share.
        res["B_all"]=safe(base,list(KEYS.values()))
        a=res["B_all"]
        if a["status"]=="retrieved" and a["hits"]>=60:
            res["P"]=safe(base,[KEYS["Pieridae"]])
            res["B"]=safe(base,[v for k,v in KEYS.items() if k!="Pieridae"])
            # Separate groups and check OR semantics before interpretation.
            for k in CL:
                b=base.copy()
                if r["source"]=="calling":
                    b.pop("basisOfRecord",None);b["datasetKey"]=FROGID
                res[k]=safe(b,r["groups"][k]["mapped_keys"],True)
            P,B=res["P"],res["B"]
            if P["status"]==B["status"]=="retrieved":
                res["butterfly_partition_ok"]=(P["hits"]+B["hits"]==a["hits"] and np.array_equal(np.asarray(P["months"])+np.asarray(B["months"]),a["months"]))
            else:res["butterfly_partition_ok"]=False
        else:res["screen"]="all_butterfly_support_below_60_or_query_failure"
        with out.open("a") as f:f.write(json.dumps(res,ensure_ascii=False,allow_nan=False)+"\n")
        if (i+1)%5==0 or i+1==len(subset):print("TEMPORAL_PROGRESS",shard,i+1,len(subset),"requests",CALLS,flush=True)
    print("TEMPORAL_SHARD",shard,"n",len(subset),"requests",CALLS,flush=True)
def eligible(x,min_n=30):
    return x and x.get("status")=="retrieved" and sum(x["months"])>=min_n and x["month_coverage"]>=.9 and sum(n>0 for n in x["months"])>=2
def overlap(a,b,lag=0):
    x=np.asarray(a,dtype=float);y=np.asarray(b,dtype=float)
    return float(np.minimum(np.roll(x/x.sum(),lag),y/y.sum()).sum())
def contrasts(r,control):
    m={k:r[k]["months"] for k in ["E",control,"P","B"]}
    a={}
    for lag in (-1,0,1):
        # D>0: exposed vs control has stronger alignment to Pieridae than other butterflies.
        d=overlap(m["E"],m["P"],lag)-overlap(m["E"],m["B"],lag)-overlap(m[control],m["P"],lag)+overlap(m[control],m["B"],lag)
        a[str(lag)]=d
    return {"D0":a["0"],"Dplus1":a["1"],"Dminus1":a["-1"],"directional_D":a["1"]-a["-1"],"Dplus1_minus_D0":a["1"]-a["0"],"overlap_EP0":overlap(m["E"],m["P"]),"overlap_CP0":overlap(m[control],m["P"])}
def summarize(blockrows,field):
    vals=pd.DataFrame(blockrows)
    if vals.empty:return {"status":"no_eligible_pairs"}
    v=vals.groupby("block")[field].mean().to_numpy()
    n=len(vals);k=len(v);mean=float(np.mean(v))
    if k<2:return {"n":n,"blocks":k,"block_balanced_mean":mean,"status":"descriptive_only"}
    rng=np.random.default_rng(20261125)
    sims=v[rng.integers(0,k,size=(10000,k))].mean(axis=1)
    return {"status":"exploratory" if n>=20 and k>=5 else "insufficient_support_descriptive_only","n":n,"blocks":k,"block_balanced_mean":mean,"cell_mean":float(vals[field].mean()),"block_bootstrap_interval_95":np.quantile(sims,[.025,.975]).tolist(),"positive_blocks":int((v>0).sum()),"negative_blocks":int((v<0).sum())}
def analyze():
    sample=json.loads((OUT/"sample.json").read_text());rows=[]
    for f in sorted(OUT.glob("shard_*.jsonl")):
        rows.extend(json.loads(line) for line in f.read_text().splitlines() if line.strip())
    keys=[(r["ix"],r["iy"],r["source"]) for r in rows]
    if len(set(keys))!=len(keys):raise ValueError("duplicate cell-source rows")
    expected={(r["ix"],r["iy"],r["source"]) for r in sample["rows"]}
    if not set(keys)<=expected:raise ValueError("unexpected cell")
    # Algebraic check lag sign: provider month 1 precedes recipient month 2.
    assert overlap([1]+[0]*11,[0,1]+[0]*10,1)==1
    report={"status":"monthly_observation_climatology_only","prequery_sample":sample["meta"],"completed_cells":len(rows),"expected_cells":len(expected),"complete":len(rows)==len(expected),"cohorts":{}}
    results=[]
    for label,c in [("broad","N"),("paired","S"),("calling_AU","N")]:
        cohort=[r for r in rows if label in r["cohorts"]]
        attr=Counter();pairs=[]
        for r in cohort:
            if r.get("screen"):attr[r["screen"]]+=1;continue
            if not r.get("butterfly_partition_ok"):attr["butterfly_partition_failed"]+=1;continue
            missing=[k for k in ["P","B","E",c] if not eligible(r.get(k))]
            if missing:attr["support_missing_"+"/".join(missing)]+=1;continue
            if any(len(r["groups"][k]["mapped_keys"])/r["groups"][k]["range_names"]<.8 for k in ["E",c]):attr["frog_taxonomic_coverage_under80pct"]+=1;continue
            z={"cohort":label,"ix":r["ix"],"iy":r["iy"],"block":r["block"],"frogE_hits":r["E"]["hits"],"frogC_hits":r[c]["hits"],"P_hits":r["P"]["hits"],"B_hits":r["B"]["hits"],"dominanceE":r["E"]["max_species_share"],"dominanceC":r[c]["max_species_share"],**contrasts(r,c)}
            pairs.append(z);results.append(z)
        attr["eligible"]=len(pairs)
        fields=["D0","Dplus1","Dminus1","directional_D","Dplus1_minus_D0"]
        report["cohorts"][label]={"source":"FrogID calling records" if label=="calling_AU" else "GBIF ordinary frog observations","n_queried":len(cohort),"blocks_queried":len({r["block"] for r in cohort}),"attrition":dict(attr),"primary_directional":summarize(pairs,"directional_D"),"secondary":{f:summarize(pairs,f) for f in fields if f!="directional_D"},"sensitivity_50_each":summarize([z for z in pairs if min(z["frogE_hits"],z["frogC_hits"],z["P_hits"],z["B_hits"])>=50],"directional_D"),"sensitivity_species_dominance_80pct":summarize([z for z in pairs if max(z["dominanceE"],z["dominanceC"])<=.8],"directional_D")}
    pd.DataFrame(results).to_csv(OUT/"paired_cell_contrasts.csv",index=False)
    dump(OUT/"summary.json",report);print("TEMPORAL_RESULT "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("task",choices=["prepare","collect","analyze"]);p.add_argument("--shard",type=int,default=0);p.add_argument("--nshards",type=int,default=3);a=p.parse_args()
    if a.task=="prepare":prepare()
    elif a.task=="collect":collect(a.shard,a.nshards)
    else:analyze()
