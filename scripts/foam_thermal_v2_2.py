#!/usr/bin/env python3
"""Nest-level thermal transfer audit of Ichioka & Kajimura (2024).
Never equate internal temperature with butterfly exposure or foam persistence."""
import hashlib, io, json, re, datetime as dt
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from foam_legacy_sources_v2_1 import fetch
OUT=Path("results/v2.2");OUT.mkdir(parents=True,exist_ok=True)
SHA="f15f470e06a05ddd0de4ac1954e16517741463951a2b0eb6657a2ef8c8b77176"
MD5="a426d6c058926846959e1aa797efa463"
A="arboreal";G="terrestrial"
GROUPS=[A,G]
def write(name,d): (OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def sheet(w,prefix):
    n=[s for s in w.sheetnames if s.startswith(prefix)]
    assert len(n)==1,n
    it=w[n[0]].iter_rows(values_only=True);h=list(next(it))
    return pd.DataFrame(it,columns=h)
def num(v):
    s=re.fullmatch(r"(?:nest\s*)?(\d+)(?:\.0)?",str(v).strip(),re.I)
    if not s:raise ValueError("bad nest ID "+str(v))
    return int(s[1])
def date(v):
    if isinstance(v,dt.datetime):return v
    s=str(v).strip().replace("'",":")
    return dt.datetime.strptime(s,"%Y/%m/%d %H:%M:%S")
def mean(x):return float(np.mean(x))
def desc(x):
    a=np.asarray(x,dtype=float)
    if not len(a):return {"n":0}
    return {"n":len(a),"mean":mean(a),"median":float(np.median(a)),"min":float(a.min()),"max":float(a.max())}
def balanced_diff(tab,col,unit="nest"):
    a=tab.groupby(["placement",unit])[col].mean().reset_index()
    x=a[a.placement==A][col].to_numpy();y=a[a.placement==G][col].to_numpy()
    return {"arboreal":desc(x),"terrestrial":desc(y),"ground_minus_tree":mean(y)-mean(x) if len(x) and len(y) else None}
def regression(x,y):
    x=np.asarray(x);y=np.asarray(y)
    if len(x)<3 or np.std(x)<1e-8:return None
    coef=np.linalg.lstsq(np.c_[np.ones(len(x)),x-18],y,rcond=None)[0]
    return {"intercept_Tin_at18":float(coef[0]),"slope":float(coef[1]),"rmse":float(np.sqrt(np.mean((y-coef[0]-coef[1]*(x-18))**2)))}
def main():
    raw,prov=fetch("https://figshare.com/ndownloader/files/41534736",1000000)
    assert len(raw)==399803 and prov["sha256"]==SHA and prov["md5"]==MD5
    w=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    frames=[]
    for prefix,group,expected in [("➀",A,1929),("➁",G,1964)]:
        f=sheet(w,prefix)
        assert len(f)==expected
        assert set(f.columns)=={"Nest place","record date&time","Nest number","time of the day","inside temperature","surrounding temperature","Difference in temperature"}
        assert set(f["Nest place"].astype(str).str.lower().str.strip())=={group}
        t=pd.DataFrame({"placement":group,"nest":f["Nest number"].map(num),"timestamp":f["record date&time"].map(date),"inside":pd.to_numeric(f["inside temperature"],errors="raise"),"outside":pd.to_numeric(f["surrounding temperature"],errors="raise"),"printed_delta":pd.to_numeric(f["Difference in temperature"],errors="raise")})
        assert np.isfinite(t[["inside","outside","printed_delta"]]).all().all()
        t["delta"]=t.inside-t.outside
        assert np.allclose(t.delta,t.printed_delta,atol=1e-8)
        frames.append(t)
    t=pd.concat(frames,ignore_index=True).sort_values(["nest","timestamp"])
    assert not t.duplicated(["nest","timestamp"]).any()
    assert t.timestamp.dt.year.eq(2022).all()
    assert t.timestamp.dt.minute.isin([0,15,30,45]).all() and t.timestamp.dt.second.eq(0).all()
    t["day"]=t.timestamp.dt.strftime("%Y-%m-%d")
    t["hour"]=t.timestamp.dt.hour+t.timestamp.dt.minute/60
    t["night"]=((t.hour<6)|(t.hour>=18))
    nest_rows=[];day_rows=[];bin_rows=[]
    for (place,nest),f in t.groupby(["placement","nest"]):
        reg=regression(f.outside,f.inside)
        r={"placement":place,"nest":int(nest),"n":len(f),"days":int(f.day.nunique()),"mean_delta":mean(f.delta),"mean_inside":mean(f.inside),"mean_outside":mean(f.outside),"outside_min":float(f.outside.min()),"outside_max":float(f.outside.max()),"inside_min":float(f.inside.min()),"inside_max":float(f.inside.max()),"night_mean_delta":mean(f.loc[f.night,"delta"]) if f.night.any() else None,"day_mean_delta":mean(f.loc[~f.night,"delta"]) if (~f.night).any() else None,**reg}
        # Difference on exactly adjacent 15 minute measurements, no spanning gaps.
        ok=f.timestamp.diff().eq(pd.Timedelta(minutes=15))
        dx=f.outside.diff()[ok];dy=f.inside.diff()[ok]
        r["adjacent_pairs"]=int(ok.sum())
        r["adjacent_sd_ratio"]=float(dy.std()/dx.std()) if dx.std()>0 else None
        nest_rows.append(r)
        for day,d in f.groupby("day"):
            # Whole day coverage criterion, frozen before outcome: >=80 of 96 slots
            # and >=16 of 24 slots in every fixed six-hour sector.
            counts=d.groupby((d.hour//6).astype(int)).size().reindex(range(4),fill_value=0)
            full=len(d)>=80 and counts.min()>=16
            dr={"placement":place,"nest":int(nest),"day":day,"n":len(d),"complete_day":bool(full),"mean_delta":mean(d.delta),"inside_range":float(d.inside.max()-d.inside.min()),"outside_range":float(d.outside.max()-d.outside.min()),"range_reduction":float((d.outside.max()-d.outside.min())-(d.inside.max()-d.inside.min())),"min_inside_minus_min_outside":float(d.inside.min()-d.outside.min()),"max_inside_minus_max_outside":float(d.inside.max()-d.outside.max()),"night_mean_delta":mean(d.loc[d.night,"delta"]) if d.night.any() else None,"day_mean_delta":mean(d.loc[~d.night,"delta"]) if (~d.night).any() else None}
            day_rows.append(dr)
        # Common ambient bins with >=8 observations per nest/bin. Fixed 2 C bins.
        for lo in range(8,28,2):
            x=f[(f.outside>=lo)&(f.outside<lo+2)]
            if len(x)>=8:bin_rows.append({"placement":place,"nest":int(nest),"bin_low":lo,"n":len(x),"mean_delta":mean(x.delta),"mean_outside":mean(x.outside)})
    ns=pd.DataFrame(nest_rows);ds=pd.DataFrame(day_rows);bs=pd.DataFrame(bin_rows)
    assert len(ns)==10 and ns.groupby("placement").size().to_dict()=={A:5,G:5}
    # Restrict thermal comparison to exact simultaneous dates/time and both placements.
    # Average multiple nests in each placement at a given time first.
    matched=t.groupby(["timestamp","placement"]).delta.mean().unstack().dropna()
    matched["day"]=matched.index.strftime("%Y-%m-%d")
    matched["difference"]=matched[G]-matched[A]
    matched_day=matched.groupby("day").agg(n=("difference","size"),delta=("difference","mean"))
    # This time comparison is paired calendar context, not equal nest age/environment.
    # Same external temperature bins reduce ambient differences, not all covariates.
    bins=[]
    for lo,d in bs.groupby("bin_low"):
        if all((d.placement==k).sum()>=2 for k in GROUPS):
            bins.append({"lower":int(lo),"upper":int(lo+2),"contrast":balanced_diff(d,"mean_delta")})
    full=ds[ds.complete_day].copy()
    daystats={k:balanced_diff(full,k) for k in ["mean_delta","range_reduction","min_inside_minus_min_outside","max_inside_minus_max_outside","night_mean_delta","day_mean_delta"]}
    # Leave-one-nest-out evaluation: no timestamp random splits. Per training nest
    # balance weights so long recordings do not dominate. Baseline Tin=Tout.
    # Use only test temperatures within training min/max; exclude extrapolation.
    loo=[]
    for (place,nest),test in t.groupby(["placement","nest"]):
        train=t[(t.placement==place)&(t.nest!=nest)]
        support=test.outside.between(train.outside.min(),train.outside.max())
        ev=test[support]
        if len(ev)<20:continue
        weights=1/train.groupby("nest").outside.transform("size").to_numpy()
        X=np.c_[np.ones(len(train)),train.outside-18];Y=train.inside.to_numpy()
        coef=np.linalg.lstsq(X*np.sqrt(weights[:,None]),Y*np.sqrt(weights),rcond=None)[0]
        pred=coef[0]+coef[1]*(ev.outside.to_numpy()-18);err=ev.inside.to_numpy()-pred
        baseline=ev.inside.to_numpy()-ev.outside.to_numpy()
        loo.append({"placement":place,"nest":int(nest),"n_test":len(ev),"excluded_out_of_support":int((~support).sum()),"baseline_MSE":mean(baseline**2),"calibrated_MSE":mean(err**2),"slope":float(coef[1]),"intercept_Tin_at18":float(coef[0])})
    cv=pd.DataFrame(loo)
    cv_summary={}
    for place,g in cv.groupby("placement"):
        base=mean(g.baseline_MSE);cal=mean(g.calibrated_MSE)
        cv_summary[place]={"n_nests":len(g),"n_test":int(g.n_test.sum()),"n_out_of_support":int(g.excluded_out_of_support.sum()),"equal_nest_RMSE_baseline":float(np.sqrt(base)),"equal_nest_RMSE_calibrated":float(np.sqrt(cal)),"relative_MSE_gain":1-cal/base}
    # Raw egg and nest outcome sheets independently reconcile with each other.
    eggs=sheet(w,"➂");h=sheet(w,"➃");w.close()
    assert len(eggs)==3597 and len(h)==9
    eggs["nest"]=eggs["Foam nest eggs belonged to"].map(num)
    eggs["place"]=eggs["Nest place"].astype(str).str.lower().str.strip()
    eggs["outcome"]=eggs.survival.astype(str).str.lower().str.strip()
    levels=sorted(eggs.outcome.unique())
    hrows=[]
    for _,r in h.iterrows():
        n=num(r["Nest number"]);p=str(r["Nest place"]).lower().strip()
        n0=int(r["Number of dead eggs"]);n1=int(r["Number of hatched eggs"]);total=int(r["Total egg number"]);pct=float(r["Hatching rate (%)"])
        ef=eggs[eggs.nest==n];assert set(ef.place)=={p}
        assert len(ef)==total==n0+n1 and abs(100*n1/total-pct)<1e-6
        assert int((ef.outcome=="dead").sum())==n0
        assert len(ef)-int((ef.outcome=="dead").sum())==n1
        hrows.append({"nest":n,"placement":p,"dead":n0,"hatched":n1,"eggs":total,"hatch_fraction":n1/total})
    hh=pd.DataFrame(hrows)
    assert set(ns.nest)-set(hh.nest)=={12}
    hatch=balanced_diff(hh,"hatch_fraction")
    hatch["without_nest6"]=balanced_diff(hh[hh.nest!=6],"hatch_fraction")
    hatch["egg_weighted_descriptive"]={k:float(g.hatched.sum()/g.eggs.sum()) for k,g in hh.groupby("placement")}
    hatch["missing_nest"]=12;hatch["missing_nest_note"]="Published predation loss; no observed egg denominator/hatching outcome. Excluded from hatching fractions; do not assign zero without an explicit nest-fate endpoint."
    # No regression of hatch against thermal measurements at egg level; n=9 nests.
    report={"status":"raw_thermal_and_hatch_audit","source":{"doi":"10.6084/m9.figshare.23667387.v1","file_id":41534736,"bytes":len(raw),"sha256":SHA,"md5":MD5},"rows":len(t),"n_nests":len(ns),"egg_outcome_labels":levels,"group_timestamp_summary":{k:{"n":len(g),"inside":desc(g.inside),"outside":desc(g.outside),"delta":desc(g.delta)} for k,g in t.groupby("placement")},"nest_weighted_mean_delta":balanced_diff(ns,"mean_delta"),"nest_weighted_night_delta":balanced_diff(ns,"night_mean_delta"),"nest_weighted_day_delta":balanced_diff(ns,"day_mean_delta"),"nest_weighted_Tin_slope":balanced_diff(ns,"slope"),"nest_weighted_15min_sd_ratio":balanced_diff(ns,"adjacent_sd_ratio"),"whole_day_coverage":{"all_nest_days":len(ds),"complete_nest_days":len(full),"by_group":{k:{"all":len(g),"complete":int(g.complete_day.sum()),"n_nests_complete":int(g[g.complete_day].nest.nunique())} for k,g in ds.groupby("placement")},"complete_day_equal_nest":daystats},"simultaneous_recording":{"n_times":len(matched),"n_days":len(matched_day),"equal_day_ground_minus_tree_delta":desc(matched_day.delta),"timestamp_weighted_ground_minus_tree_delta":desc(matched.difference)},"common_ambient_bin_contrasts":bins,"leave_one_nest_out_temperature":cv_summary,"hatch":hatch,"limits":["Ten experimental nests, originally arboreal, five per placement; local study, not global replication.","Temperature loggers recorded inside about 5 cm deep and surrounding air about 10 cm above nest, not external foam surface temperature.","Fixed night 18:00–06:00 is a descriptive clock window, not astronomical night.","Equal nest weighting, complete-day and simultaneous-recording comparisons are diagnostic; dates, stage and habitat can still differ.","No no-foam control, no foam surface moisture, chemistry, persistence after departure, recipient contact or butterfly fertilization.","Leave-one-nest-out calibration only transfers to other nests at the same site within measured temperature support; no global validation."]}
    for name,df in [("nest_thermal.csv",ns),("nest_day_thermal.csv",ds),("ambient_bins.csv",bs),("matched_day_delta.csv",matched_day.reset_index()),("leave_one_nest_out.csv",cv),("nest_hatch.csv",hh)]:
        df.to_csv(OUT/name,index=False)
    write("summary.json",report);print("THERMAL_RESULT "+json.dumps(report,ensure_ascii=False,allow_nan=False),flush=True)
if __name__=="__main__":main()
