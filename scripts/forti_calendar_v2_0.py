#!/usr/bin/env python3
"""V2.0 reported breeding-calendar breadth; source-level matched descriptive analysis.
No imputation of nonbreeding, actual nest lifetimes, or butterfly reproduction."""
import hashlib,io,json,math,re,unicodedata
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from forti_audit_v1_9 import acquire
from global_acquisition_v1_3 import SOURCES,request,normalize_nunes,ROOT

OUT=Path("results/v2.0");OUT.mkdir(parents=True,exist_ok=True)
MC="jan feb mar apr may jun jul aug sep oct nov dec".split()
E="froth_potentially_exposed";S="froth_sheltered"
MIN_STUDIES=10;MIN_SPECIES=5
def norm(v):
    return " ".join(str(v).strip().replace("_"," ").split()) if pd.notna(v) else ""
def token(v):
    return "".join(c for c in unicodedata.normalize("NFKD",norm(v).casefold()) if not unicodedata.combining(c))
def hashed(v):return hashlib.sha256(str(v).encode()).hexdigest()[:20]
def number(v):
    s=norm(v)
    if not re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?",s):return None
    return float(s.replace(",","."))
def calendar(v):
    # Complete binary monthly calendars only; an unmarked month is not verified absence.
    a=np.array(v,dtype=float)
    if a.shape!=(12,) or not np.isin(a,[0,1]).all() or a.sum()<1:return None
    a=a.astype(int);n=int(a.sum())
    if n==12:run=span=12
    else:
        # Longest consecutive reported month sequence across the Dec/Jan boundary.
        run=0;k=0;gap=0;g=0
        for x in np.tile(a,2):
            k=k+1 if x else 0;run=max(run,k)
            g=g+1 if not x else 0;gap=max(gap,g)
        span=12-gap
    z=a@np.exp(2j*np.pi*(np.arange(12)+.5)/12)/n
    return {"months":n,"longest_run":int(run),"covering_arc":int(span),"R":float(abs(z)),"calendar":"".join(map(str,a))}
def acquire_frame():
    raw,prov=acquire();assert prov["sha256"]=="472ac7f596b16d09559295c622fa4b17de735391ddc88fd5d08a24ef70d81430"
    w=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    it=w["literature"].iter_rows(values_only=True);h=list(next(it));d=pd.DataFrame(it,columns=[f"{v}_{i}" if h.count(v)>1 else v for i,v in enumerate(h)]);w.close()
    assert len(d)==760 and set(MC+["citation","Link","family","species","checked name (FROST)","state","city_18","Latitude","Longitude"])<=set(d.columns)
    d["taxon"]=d["checked name (FROST)"].map(norm)
    d["orig_taxon"]=d.species.map(norm)
    d["source_family"]=d.family.map(norm)
    d["study"]=d.citation.map(token);d["link"]=d.Link.map(token)
    d["state_norm"]=d.state.map(token);d["city_norm"]=d.city_18.map(token)
    d["municipality"]=np.where((d.state_norm!="")&(d.city_norm!=""),d.state_norm+"|"+d.city_norm,"")
    lat=d.Latitude.map(number);lon=d.Longitude.map(number)
    d["coordinate"]= [f"{a:.4f}|{b:.4f}" if pd.notna(a) and pd.notna(b) and -35<=a<=6 and -75<=b<=-32 else "" for a,b in zip(lat,lon)]
    rawm=d[MC].apply(pd.to_numeric,errors="coerce")
    complete=rawm.notna().all(axis=1)&rawm.isin([0,1]).all(axis=1)
    # Report the published 4039 species-location-month count alongside source row sum,
    # not assume they must agree after aggregation or incomplete rows.
    audit={"source":prov,"n_rows":len(d),"n_raw_names":int(d.orig_taxon.nunique()),"n_checked_names":int(d.taxon.nunique()),"n_citations":int(d.loc[d.study!="","study"].nunique()),"n_links":int(d.loc[d.link!="","link"].nunique()),"n_complete_binary":int(complete.sum()),"n_complete_positive":int((complete&(rawm.sum(axis=1)>0)).sum()),"n_complete_zero":int((complete&(rawm.sum(axis=1)==0)).sum()),"source_nonmissing_ones":int((rawm==1).sum().sum()),"n_nonbinary_nonmissing_cells":int((rawm.notna()&~rawm.isin([0,1])).sum().sum()),"n_missing_month_cells":int(rawm.isna().sum().sum()),"valid_municipality_rows":int((d.municipality!="").sum()),"plausible_numeric_coord_rows":int((d.coordinate!="").sum()),"multiple_links_per_citation":int((d[d.study!=""].groupby("study").link.nunique()>1).sum()),"multiple_citations_per_link":int((d[d.link!=""].groupby("link").study.nunique()>1).sum())}
    # Primary exact source-name and family match to prior trait release.
    b,_,_=request(SOURCES["nunes2021"][0]);sha=hashlib.sha256(b).hexdigest()
    assert sha=="3ec2b6ab0d457cf6bcd4bcbabd7bf51aa2ea3f1ec898d297f1f68a46a883b964"
    a=load_workbook(io.BytesIO(b),read_only=True,data_only=True);normalize_nunes(a,sha);a.close()
    t=pd.read_csv(ROOT/"nunes2021_traits.csv",dtype=str,keep_default_na=False)
    t["taxon"]=t.species_as_used.map(norm);t=t.loc[~t.taxon.duplicated(keep=False)].copy()
    assert len(t)==2010
    t["strict_E"]=t.froth_modes.map(lambda x:bool(x) and set(map(int,x.split(";")))<=set([44,45,51,52,53,54,55])) & t.trait_class.eq(E)
    d=d.merge(t[["taxon","family_as_used","trait_class","strict_E","froth_modes"]],on="taxon",how="left",validate="many_to_one")
    d["trait"]=d.trait_class.where(d.source_family==d.family_as_used,"unresolved").fillna("unresolved")
    d["strict_E"]=d.strict_E.eq(True)&d.trait.eq(E)
    d["genus"]=d.taxon.str.split().str[0]
    audit["matched_name_rows"]=int(d.taxon.isin(t.taxon).sum())
    audit["matched_name_family_rows"]=int(d.trait.ne("unresolved").sum())
    audit["name_family_conflict_rows"]=int((d.taxon.isin(t.taxon)&d.trait.eq("unresolved")).sum())
    audit["original_name_matches_checked_name"]=int(d.orig_taxon.eq(d.taxon).sum())
    records=[]
    for i,r in d.iterrows():
        c=calendar(rawm.iloc[i].values)
        if c is None or not r.study or not r.taxon:continue
        records.append(dict(taxon=r.taxon,genus=r.genus,family=r.source_family,trait=r.trait,strict_E=bool(r.strict_E),study=r.study,municipality=r.municipality,coordinate=r.coordinate,**c))
    f=pd.DataFrame(records)
    assert len(f)>0
    before=len(f)
    f=f.drop_duplicates(["study","municipality","coordinate","taxon","calendar"]).copy()
    audit["valid_rows_before_duplicate_removal"]=before;audit["exact_calendar_duplicate_rows_removed"]=before-len(f)
    audit["valid_rows"]=len(f);audit["valid_matched_rows"]=int(f.trait.ne("unresolved").sum())
    return f,audit
def group_summary(f):
    res={}
    for k,a in f.groupby("trait",sort=True):
        # Mean within species before equal species weighting; not pooled row count.
        sp=a.groupby("taxon")[["months","R","longest_run","covering_arc"]].mean()
        res[k]={"rows":len(a),"species":len(sp),"studies":int(a.study.nunique()),"mean_months_species_balanced":float(sp.months.mean()),"median_months_species_balanced":float(sp.months.median()),"mean_R_species_balanced":float(sp.R.mean()),"mean_longest_run_species_balanced":float(sp.longest_run.mean()),"mean_covering_arc_species_balanced":float(sp.covering_arc.mean())}
    return res
def paired(f,unit,strict=False,within_genus=False,min_each=1):
    a=f[(f.family=="Leptodactylidae") & f.trait.isin([E,S])].copy()
    if strict:a=a[(a.trait==S)|a.strict_E]
    if unit!="study":a=a[a[unit]!=""]
    cols=["study"]+([unit] if unit!="study" else [])+(["genus"] if within_genus else [])
    vals=[];es=set();ss=set()
    for key,g in a.groupby(cols,sort=True):
        key=key if isinstance(key,tuple) else (key,)
        # Within a study/site/species, average repeated distinct calendars
        # (not union, which would inflate duration with sampling effort).
        sp=g.groupby(["taxon","trait"],sort=True)[["months","R","longest_run","covering_arc"]].mean().reset_index()
        e=sp[sp.trait==E];s=sp[sp.trait==S]
        if min(len(e),len(s))<min_each:continue
        es.update(e.taxon);ss.update(s.taxon)
        vals.append({"study":key[0],"unit":hashed(key),"n_E":len(e),"n_S":len(s),"delta_months":float(e.months.mean()-s.months.mean()),"delta_R":float(e.R.mean()-s.R.mean()),"delta_longest_run":float(e.longest_run.mean()-s.longest_run.mean()),"delta_arc":float(e.covering_arc.mean()-s.covering_arc.mean())})
    if not vals:return {"status":"no_paired_support","n_units":0,"n_studies":0},[]
    v=pd.DataFrame(vals);study=v.groupby("study")[["delta_months","delta_R","delta_longest_run","delta_arc"]].mean()
    b=study.delta_months.to_numpy();mu=float(b.mean());n=len(b)
    res={"status":"descriptive_support" if n>=MIN_STUDIES and min(len(es),len(ss))>=MIN_SPECIES else "sparse_descriptive_only","n_units":len(v),"n_studies":n,"species_E":len(es),"species_S":len(ss),"positive_studies":int((b>1e-12).sum()),"negative_studies":int((b< -1e-12).sum()),"zero_studies":int((abs(b)<=1e-12).sum()),"study_balanced_delta_months":mu,"unit_balanced_delta_months":float(v.delta_months.mean()),"study_balanced_delta_R":float(study.delta_R.mean()),"study_balanced_delta_longest_run":float(study.delta_longest_run.mean()),"study_balanced_delta_arc":float(study.delta_arc.mean()),"species_lists":{"E":sorted(es),"S":sorted(ss)}}
    if n>=2:
        rng=np.random.default_rng(20261126)
        sims=b[rng.integers(0,n,size=(10000,n))].mean(axis=1)
        loo=(b.sum()-b)/(n-1)
        res["descriptive_study_bootstrap_interval"]=np.quantile(sims,[.025,.975]).tolist()
        res["leave_one_study_out_range"]=[float(loo.min()),float(loo.max())]
    # No site coordinates, names or raw study links exported.
    for z in vals:z["study"]=hashed(z["study"])
    return res,vals
def main():
    assert calendar([1]+[0]*10+[1])["longest_run"]==2
    assert calendar([1,0,1]+[0]*9)["covering_arc"]==3
    assert calendar([1]*12)["months"]==12 and calendar([0]*12) is None
    f,audit=acquire_frame()
    report={"status":"reported_month_calendar_comparison","audit":audit,"all_class_summary":group_summary(f),"strict_E_summary":group_summary(f[f.strict_E]),"leptodactylidae_summary":group_summary(f[f.family=="Leptodactylidae"]),"paired":{}}
    allout=[]
    for unit,strict,genus,min_each in [("municipality",False,False,1),("municipality",True,False,1),("coordinate",False,False,1),("coordinate",True,False,1),("study",False,False,1),("municipality",False,True,1),("municipality",False,False,2)]:
        tag=f"{unit}_{'strict' if strict else 'original'}_{'within_genus' if genus else 'all_genera'}_min{min_each}"
        result,rows=paired(f,unit,strict,genus,min_each)
        report["paired"][tag]=result
        allout.extend({"analysis":tag,**r} for r in rows)
    report["limits"]=["Reported breeding months from literature, not detection-corrected durations; no sampling-month denominator available. Zero month means not reported, not confirmed nonbreeding.","Same publication+municipality comparison within Leptodactylidae reduces site/study and family confounding but may pool different ponds, years or survey schedules. Coordinate matching is approximate and some coordinates reconstructed by original authors.","Repeated species across studies and genus-specific trait conservatism violate simple independence. Bootstrap intervals descriptive, not phylogenetically corrected.","Ground excluded in strict E; actual accessible nest area/persistence unknown. No butterfly observation or fertilization endpoint."]
    (OUT/"calendar_summary.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    if allout:pd.DataFrame(allout).to_csv(OUT/"study_site_contrasts.csv",index=False)
    print("CALENDAR_RESULT "+json.dumps(report,ensure_ascii=False,allow_nan=False),flush=True)
if __name__=="__main__":main()
