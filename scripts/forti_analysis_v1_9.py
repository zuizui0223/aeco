#!/usr/bin/env python3
"""Behavior-coded frog phenology validation; no raw records, observer IDs, or locations exported."""
import datetime as dt, hashlib, io, json, math, re
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from forti_audit_v1_9 import acquire, OUT
from global_acquisition_v1_3 import SOURCES,request,normalize_nunes,ROOT
FLAGS=["airsac","vocalisation","amplexus","tadpole"]
CLASSES=["froth_potentially_exposed","froth_sheltered","froth_variable","froth_mixed_exposure","bubble_only","no_documented_froth_or_bubble"]
# Pre-outcome diagnostic; no threshold search.
MIN_CUE=10;MIN_NO_CUE=20;MIN_SPECIES_PER_GROUP=5
def norm(x):return " ".join(str(x).strip().replace("_"," ").split()) if x is not None else ""
def marker(x):
    s=norm(x).casefold()
    if s in {"1","1.0","yes","y","true","t","sim","presence","present"}:return 1
    if s in {"0","0.0","no","n","false","f","não","nao","absence","absent"}:return 0
    return None
def parsed_date(v):
    if isinstance(v,dt.datetime):return v.date(),"excel_datetime"
    if isinstance(v,dt.date):return v,"excel_date"
    if v is None:return None,"missing"
    s=str(v).strip()
    # Explicit MDY column; ISO strings have year first. Do not assume DMY.
    for pat,fmt,label in [(r"\d{4}-\d{1,2}-\d{1,2}","%Y-%m-%d","iso_dash"),(r"\d{4}/\d{1,2}/\d{1,2}","%Y/%m/%d","iso_slash"),(r"\d{1,2}/\d{1,2}/\d{4}","%m/%d/%Y","mdy_slash"),(r"\d{1,2}-\d{1,2}-\d{4}","%m-%d-%Y","mdy_dash")]:
        if re.fullmatch(pat,s):
            try:return dt.datetime.strptime(s,fmt).date(),label
            except ValueError:return None,label+"_invalid"
    return None,"other_"+re.sub(r"[A-Za-z]","A",re.sub(r"\d","D",s))[:40]
def get_sheet(w,name):
    it=w[name].iter_rows(values_only=True);h=next(it)
    return pd.DataFrame(it,columns=[f"{v}_{i}" if list(h).count(v)>1 else v for i,v in enumerate(h)])
def vector(months):
    a=np.bincount(np.array(months,dtype=int)-1,minlength=12).astype(float)
    assert a.size==12 and a.sum()>0
    return a/a.sum()
def metrics(p,q):
    # month-bin centers; no claim of exact daily reproduction date.
    roots=np.exp(2j*np.pi*(np.arange(12)+.5)/12)
    zp=p@roots;zq=q@roots
    diff=np.angle(zp*np.conj(zq))*12/(2*np.pi)
    return {"R_cue":float(abs(zp)),"R_no_recorded_cue":float(abs(zq)),"delta_R":float(abs(zp)-abs(zq)),"phase_difference_months":float(diff),"overlap":float(np.minimum(p,q).sum())}
def profile(x):
    p=vector(x.month)
    return {"n":len(x),"n_species":int(x.species.nunique()),"month_counts":np.bincount(x.month-1,minlength=12).tolist(),"R":float(abs(p@np.exp(2j*np.pi*(np.arange(12)+.5)/12)))}
def grouped_profiles(x):
    out={}
    for k,a in x.groupby("trait",sort=True):
        out[k]={k2:profile(b) for k2,b in a.groupby("evidence",sort=True) if len(b)}
    return out
def main():
    raw,prov=acquire()
    w=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    d=get_sheet(w,"inaturalist");lit=get_sheet(w,"literature");w.close()
    assert len(d)==8478 and len(lit)==760 and set(FLAGS+["species","family","MDY","ID","climate"])<=set(d)
    report={"status":"source_audit_and_descriptive_validation","provenance":prov,"rows":len(d),"literature_rows":len(lit),
        "flag_raw_counts":{k:{str(x):int(n) for x,n in d[k].value_counts(dropna=False).items()} for k in FLAGS},
        "unique_ids":int(d.ID.nunique()),"duplicate_id_rows":int(d.ID.duplicated(keep=False).sum()),
        "definitions":{"adult_cue":"airsac OR vocalisation OR amplexus explicit positive; no direct nest flag","no_recorded_cue":"all four fields explicitly negative; not absence of reproduction","tadpole_only":"tadpole positive, adult fields negative","unclassified":"other/unknown flags"}}
    dates=[parsed_date(v) for v in d.MDY]
    report["date_parse_status"]=dict(Counter(s for _,s in dates))
    d["month"]=[v.month if v else None for v,_ in dates]
    d["year"]=[v.year if v else None for v,_ in dates]
    report["dated_rows"]=int(d.month.notna().sum())
    report["dated_year_range"]=[int(d.year.min()),int(d.year.max())] if d.year.notna().any() else None
    print("FORTI_FLAGS "+json.dumps({k:report[k] for k in ("flag_raw_counts","unique_ids","duplicate_id_rows","date_parse_status","dated_rows","dated_year_range")},ensure_ascii=False),flush=True)
    # Fail closed on ambiguous marker encodings or incomplete dates, leave audit receipt.
    for k in FLAGS:d[k+"_parsed"]=[marker(v) for v in d[k]]
    report["unparsed_marker_counts"]={k:int(d[k+"_parsed"].isna().sum()) for k in FLAGS}
    v=d[[k+"_parsed" for k in FLAGS]].to_numpy(dtype=float)
    adult=np.any(v[:,:3]==1,axis=1);negative=np.all(v==0,axis=1)
    tad=(v[:,3]==1)&np.all(v[:,:3]==0,axis=1)
    d["evidence"]=np.select([adult,negative,tad],["adult_cue","no_recorded_cue","tadpole_only"],default="unclassified")
    report["evidence_all_rows"]={str(k):int(n) for k,n in d.evidence.value_counts().items()}
    # Exact source binomial names; duplicate rows excluded. No genus-based fill.
    b,_,_=request(SOURCES["nunes2021"][0]);sha=hashlib.sha256(b).hexdigest()
    assert sha=="3ec2b6ab0d457cf6bcd4bcbabd7bf51aa2ea3f1ec898d297f1f68a46a883b964"
    a=load_workbook(io.BytesIO(b),read_only=True,data_only=True);normalize_nunes(a,sha);a.close()
    t=pd.read_csv(ROOT/"nunes2021_traits.csv",dtype=str,keep_default_na=False)
    t["species"]=t.species_as_used.map(norm);t=t.loc[~t.species.duplicated(keep=False)].copy()
    t["strict_no_ground"]=t.froth_modes.map(lambda x:bool(x) and set(map(int,x.split(";")))<=set([44,45,51,52,53,54,55]))
    assert len(t)==2010
    d["species"]=d.species.map(norm)
    d["family"]=d.family.map(norm);d["climate"]=d.climate.map(norm)
    d=d.merge(t[["species","family_as_used","trait_class","strict_no_ground"]],on="species",how="left",validate="many_to_one")
    compatible=d.family==d.family_as_used
    d["trait"]=d.trait_class.where(compatible,"unresolved")
    d["strict_no_ground"]=d.strict_no_ground.eq(True)&compatible
    report["species_total"]=int(d.species.nunique())
    report["matched_trait_rows"]=int((d.trait!="unresolved").sum())
    report["matched_trait_species"]=int(d.loc[d.trait!="unresolved","species"].nunique())
    report["trait_counts_all_rows"]={k:{"n":len(a),"species":int(a.species.nunique()),"adult_cue":int((a.evidence=="adult_cue").sum())} for k,a in d.groupby("trait")}
    x=d.loc[d.month.notna()&~d.ID.duplicated(keep=False)].copy();x.month=x.month.astype(int)
    report["profiles_record_weighted"]=grouped_profiles(x)
    report["strict_exposed_profile"]={k:profile(a) for k,a in x.loc[x.strict_no_ground].groupby("evidence") if len(a)}
    report["all_record_profiles"]={k:profile(a) for k,a in x.groupby("evidence") if len(a)}
    # Match species AND climate category to reduce compositional confounding.
    # Equal-size random sampling of no-cue observations avoids small-n inflation in R.
    units=[];rng=np.random.default_rng(20261126)
    for (species,climate),a in x[(x.trait!="unresolved")&(x.climate!="")].groupby(["species","climate"],sort=True):
        cue=a.loc[a.evidence=="adult_cue","month"].to_numpy()
        other=a.loc[a.evidence=="no_recorded_cue","month"].to_numpy()
        if len(cue)<MIN_CUE or len(other)<MIN_NO_CUE:continue
        n=min(len(cue),len(other));pc=vector(cue);pn=vector(other)
        sims=[]
        for _ in range(500):
            cp=vector(rng.choice(cue,n,replace=False));np_=vector(rng.choice(other,n,replace=False))
            sims.append(metrics(cp,np_)["delta_R"])
        z=metrics(pc,pn)
        units.append({"species":species,"family":a.family.iloc[0],"climate":climate,"trait":a.trait.iloc[0],"strict_no_ground":bool(a.strict_no_ground.iloc[0]),"n_cue":len(cue),"n_no_cue":len(other),**z,"equal_n_delta_R_mean":float(np.mean(sims))})
    report["matched_species_climate_units"]=len(units)
    uu=pd.DataFrame(units)
    def balanced(a):
        if not len(a):return {"n_units":0,"n_species":0,"status":"no_support"}
        s=a.groupby("species",sort=True).equal_n_delta_R_mean.mean()
        return {"n_units":len(a),"n_species":len(s),"n_climates":int(a.climate.nunique()),"mean_equal_n_delta_R_species_weighted":float(s.mean()),"median_equal_n_delta_R_species_weighted":float(s.median()),"positive_species":int((s>0).sum()),"median_abs_phase_difference_months":float(a.phase_difference_months.abs().median()),"median_monthly_overlap":float(a.overlap.median()),"status":"descriptive_support" if len(s)>=MIN_SPECIES_PER_GROUP else "sparse_descriptive_only"}
    report["matched_summary"]={}
    if len(uu):
        report["matched_summary"]["all"]=balanced(uu)
        for k in CLASSES:report["matched_summary"][k]=balanced(uu[uu.trait==k])
        report["matched_summary"]["strict_exposed"]=balanced(uu[uu.strict_no_ground])
        for k in ("froth_potentially_exposed","froth_sheltered"):report["matched_summary"]["Leptodactylidae_"+k]=balanced(uu[(uu.family=="Leptodactylidae")&(uu.trait==k)])
    else:report["matched_summary"]["all"]={"n_units":0,"n_species":0,"status":"no_support"}
    # Literature month matrix: schema and exact source-name join only, no NA=0.
    lm="checked name (FROST)";mc=["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
    lit["species"]=lit[lm].map(norm);lv=lit[mc].apply(pd.to_numeric,errors="coerce")
    complete=lv.notna().all(axis=1)&lv.isin([0,1]).all(axis=1)
    report["literature_audit"]={"rows":len(lit),"unique_names":int(lit.species.nunique()),"complete_binary_month_rows":int(complete.sum()),"exact_trait_name_matched_rows":int(lit.species.isin(t.species).sum()),"scope":"Study/site breeding calendars, potentially repeated species/study; not independent observation events. No inferred nonbreeding from missing."}
    report["limitations"]=["No explicit nest/egg flag in source sheet; adult behavior and tadpole categories are not foam observations or fertilization.","Marker encodings must be checked against source and unknown markers retained.","Observational date/method and observer bias; no recorded cue is not a biological negative.","Exact binomial/family matching only, incomplete traits; no source data redistribution.","Equal-N descriptive within-species/climate comparison; not proof of actual abundance or cross-taxon causal relation."]
    (OUT/"forti_analysis.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    if len(uu):uu.to_csv(OUT/"species_climate_descriptive.csv",index=False)
    print("FORTI_RESULT "+json.dumps(report,ensure_ascii=False,allow_nan=False),flush=True)
if __name__=="__main__":main()
