#!/usr/bin/env python3
"""V1.5 global stratified grid pilot: observed butterflies, not actual abundance or breeding.
GBIF facets are public aggregates; no raw point records or exact wildlife locations published.
"""
import argparse,hashlib,json,math,time,urllib.error,urllib.parse,urllib.request,re
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
import pyproj
import xarray as xr
import statsmodels.api as sm
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LinearRegression
from global_range_v1_4 import load_traits,read_ranges,rainfall,get,PROVENANCE

FAMILIES=["Hesperiidae","Papilionidae","Pieridae","Nymphalidae","Lycaenidae","Riodinidae"]
CLASSES=["froth_potentially_exposed","froth_sheltered","froth_variable","froth_mixed_exposure","bubble_only","no_documented_froth_or_bubble"]
BASE={"year":"2010,2021","hasCoordinate":"true","hasGeospatialIssue":"false","occurrenceStatus":"PRESENT","basisOfRecord":"HUMAN_OBSERVATION","limit":0}
LAST=0.
CALLS=0
def api(path,p):
    global LAST,CALLS
    url="https://api.gbif.org/v1/"+path+"?"+urllib.parse.urlencode(p,doseq=True)
    for i in range(3):
        # One request at a time in each job. Respect backoff; no infinite retries.
        time.sleep(max(0.,.85-(time.monotonic()-LAST)))
        LAST=time.monotonic();CALLS+=1
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"AECO global pilot/1.5 (https://github.com/zuizui0223/aeco)","Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=25) as r:
                b=r.read(4_000_001)
            if len(b)>4_000_000: raise ValueError("oversize JSON")
            return json.loads(b)
        except (OSError,ValueError) as e:
            if i==2: raise
            wait=2**(i+1)
            if isinstance(e,urllib.error.HTTPError) and e.code==429:
                try: wait=max(wait,min(60,int(e.headers.get("Retry-After","5"))))
                except ValueError: pass
            time.sleep(wait)
def facet(d,field):
    wanted=re.sub(r"[^a-z]","",field.lower())
    hits=[f for f in d.get("facets",[]) if re.sub(r"[^a-z]","",str(f.get("field","")).lower())==wanted]
    if len(hits)!=1:
        if int(d.get("count",-1))==0: return {}
        raise ValueError("facet unavailable: "+field)
    out={}
    for z in hits[0]["counts"]:
        key=int(z["name"]);n=int(z["count"])
        if n<=0 or key in out: raise ValueError("invalid facet entry")
        out[key]=n
    return out
def taxonomy():
    keys={}
    for fam in FAMILIES:
        m=api("species/match",{"name":fam,"rank":"FAMILY","strict":"true"})
        if m.get("matchType")!="EXACT" or m.get("rank")!="FAMILY" or m.get("scientificName","").split()[0]!=fam or not m.get("usageKey"): raise ValueError("family resolution failed "+fam+str(m))
        keys[fam]=int(m["usageKey"])
    assert len(set(keys.values()))==6
    # Independent global Pieridae key list under the same date & basis filters.
    # Page if needed; verify disjoint keys and stable counts across pages.
    pier={};total=None
    for offset in range(0,10000,1000):
        d=api("occurrence/search",{**BASE,"taxonKey":keys["Pieridae"],"facet":"speciesKey","facetLimit":1000,"facetOffset":offset})
        if total is None: total=int(d["count"])
        if int(d["count"])!=total: raise ValueError("global count changed while paginating")
        counts=facet(d,"speciesKey")
        if set(counts)&set(pier): raise ValueError("facet page repeated")
        pier.update(counts)
        if len(counts)<1000: break
    else: raise ValueError("global species facet cap reached")
    if not pier or sum(pier.values())>total: raise ValueError("invalid global pieridae facet")
    return keys,pier,{"family_keys":keys,"global_pieridae_species_keys":len(pier),"global_pieridae_hits":total,"global_pieridae_species_resolved_hits":sum(pier.values())}

def grid_index(frame,scale):
    xy=pyproj.Transformer.from_crs(4326,6933,always_xy=True)
    a=frame.loc[frame.y.between(-86,86)].copy()
    x,y=xy.transform(a.x.to_numpy(),a.y.to_numpy())
    a["ix"]=np.floor(x/(scale*1000)).astype(int)
    a["iy"]=np.floor(y/(scale*1000)).astype(int)
    return a
def temperature(c):
    # Native 2.5-degree NCEP/NCAR surface monthly reanalysis. Source is not satellite-only.
    # NCSS requests 2010–2021 only to avoid downloading all years.
    base="https://psl.noaa.gov/thredds/ncss/grid/Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"
    params={"var":"air","north":90,"south":-90,"west":0,"east":359.9,"horizStride":1,"time_start":"2010-01-01T00:00:00Z","time_end":"2021-12-01T00:00:00Z","timeStride":1,"accept":"netcdf"}
    p=get(base+"?"+urllib.parse.urlencode(params),"temperature_ncss.nc",25_000_000)
    with xr.open_dataset(p,decode_times=False) as ds:
        units=str(ds.time.attrs.get("units",""));m=re.match(r"^(hours|days) since (\d{4})-0?1-0?1",units)
        if not m: raise ValueError("unexpected temp time units "+units)
        dates=pd.to_datetime(ds.time.values,unit={"hours":"h","days":"D"}[m[1]],origin=m[2]+"-01-01")
        assert list(pd.DatetimeIndex(dates).to_period("M"))==list(pd.period_range("2010-01","2021-12",freq="M"))
        a=ds.air
        if a.attrs.get("units") in ("degK","K"): a=a-273.15
        elif a.attrs.get("units") not in ("degC","C","degrees_Celsius"): raise ValueError("unexpected temp units "+str(a.attrs))
        lon=c.x.to_numpy()%360
        xi=xr.DataArray((np.rint(lon/2.5)*2.5)%360,dims=["points"]);yi=xr.DataArray(np.clip(np.rint(c.y.to_numpy()/2.5)*2.5,-90,90),dims=["points"])
        vals=a.mean("time",skipna=False).sel(lat=yi,lon=xi,method="nearest").values
        assert vals.shape==(len(c),) and np.nanmin(vals)>-90 and np.nanmax(vals)<60
        return vals
def frame(scale):
    t=load_traits();d,_=read_ranges()
    j=d.merge(t[["species","trait_class","family_as_used"]],on="species",how="inner",validate="many_to_one")
    assert j.species.nunique()==1698
    native=j[["x","y"]].drop_duplicates()
    g=grid_index(j,scale)
    u=g[["ix","iy","species","trait_class"]].drop_duplicates()
    x=u.groupby(["ix","iy","trait_class"]).size().unstack(fill_value=0).reindex(columns=CLASSES,fill_value=0).reset_index()
    x["n_frogs"]=x[CLASSES].sum(axis=1)
    x["n_froth"]=x[CLASSES[:4]].sum(axis=1)
    for col,new in zip(CLASSES[:4],["exposed","sheltered","variable","mixed"]):
        x[new]=x[col]/x.n_frogs
    cg=grid_index(native,scale).groupby(["ix","iy"]).size().rename("native_centers").reset_index()
    x=x.merge(cg,on=["ix","iy"],validate="one_to_one")
    inv=pyproj.Transformer.from_crs(6933,4326,always_xy=True)
    x["lon"],x["lat"]=inv.transform((x.ix+.5).to_numpy()*scale*1000,(x.iy+.5).to_numpy()*scale*1000)
    # Exclude partial dateline/near-pole squares rather than using invalid geometry.
    xmax=pyproj.Transformer.from_crs(4326,6933,always_xy=True).transform(180,0)[0]
    ymax=pyproj.Transformer.from_crs(4326,6933,always_xy=True).transform(0,86)[1]
    ok=(x.ix*scale*1000>=-xmax)&((x.ix+1)*scale*1000<=xmax)&(x.iy*scale*1000>=-ymax)&((x.iy+1)*scale*1000<=ymax)
    x=x.loc[ok].copy()
    x["exposure_stratum"]=np.select([x.sheltered>0,x.exposed>0,x.n_froth>0],["sheltered_present","exposed_no_sheltered","other_froth"],default="no_froth")
    x["latitude_stratum"]=pd.cut(x.lat,[-90,-23.5,23.5,90],labels=["south","tropics","north"]).astype(str)
    x["longitude_stratum"]=np.floor((x.lon+180)/60).astype(int)
    x["block"]=np.floor((x.lon+180)/30).astype(int).astype(str)+"_"+np.floor((x.lat+90)/20).astype(int).astype(str)
    groups=["latitude_stratum","longitude_stratum","exposure_stratum"]
    # Deterministic stratified sampling before recipient query. 4 cells per stratum.
    samples=[]
    for k,v in x.sort_values(["ix","iy"]).groupby(groups,sort=True,observed=True):
        seed=int(hashlib.sha256(("AECO-v1.5:"+str(scale)+":"+str(k)).encode()).hexdigest()[:8],16)
        z=v.sample(n=min(4,len(v)),random_state=seed).copy()
        z["stratum_population"]=len(v);z["stratum_sample"]=len(z);samples.append(z)
    f=pd.concat(samples).sort_values(["ix","iy"]).reset_index(drop=True)
    return f,{"frame_cells":len(x),"sample_cells":len(f),"strata":len(samples),"source_provenance":PROVENANCE},native

def climate_after_recipient(native,sample,scale):
    """Do not block or lose actual butterfly facets when climate host is unavailable."""
    c=grid_index(native,scale).merge(sample[["ix","iy"]],on=["ix","iy"],how="inner",validate="many_to_one")
    c=c[["x","y"]].drop_duplicates()
    report={}
    try:
        c,meta=rainfall(c)
        report["rainfall_status"]="success";report["rainfall_metadata"]=meta
    except Exception as e:
        report["rainfall_status"]="failed";report["rainfall_error"]=repr(e)
        c["rain_annual_mm"]=np.nan;c["rain_month_cv"]=np.nan
    try:
        c["temperature_c"]=temperature(c);report["temperature_status"]="success"
    except Exception as e:
        c["temperature_c"]=np.nan;report["temperature_status"]="failed";report["temperature_error"]=repr(e)
    c=grid_index(c,scale);c["weight"]=np.cos(np.deg2rad(c.y))
    for k in ["rain_annual_mm","rain_month_cv","temperature_c"]:c[k+"_w"]=c[k]*c.weight
    g=c.groupby(["ix","iy"]).agg(w=("weight","sum"),rain=("rain_annual_mm_w",lambda v:v.sum(min_count=len(v))),rain_cv=("rain_month_cv_w",lambda v:v.sum(min_count=len(v))),temp=("temperature_c_w",lambda v:v.sum(min_count=len(v)))).reset_index()
    for k in ["rain","rain_cv","temp"]:g[k]/=g.w
    return g[["ix","iy","rain","rain_cv","temp"]],report

def polygon(r,scale):
    inv=pyproj.Transformer.from_crs(6933,4326,always_xy=True)
    x0,y0=inv.transform(r.ix*scale*1000,r.iy*scale*1000)
    x1,y1=inv.transform((r.ix+1)*scale*1000,(r.iy+1)*scale*1000)
    assert -180<=x0<x1<=180 and -90<=y0<y1<=90
    return "POLYGON(("+",".join(f"{x:.7f} {y:.7f}" for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)])+"))"
def rare(c,N,k):
    # E[presence in a sample of k records without replacement]. Counts are occurrence hits.
    n=np.asarray(c,dtype=float)
    if k>N or k<1: raise ValueError("invalid rarefaction size")
    with np.errstate(divide="ignore",invalid="ignore"):
        z=np.maximum(0,1-n[:,None]/(N-np.arange(k))[None,:])
        return -np.expm1(np.log(z).sum(axis=1))
def collect(r,scale,keys,pier):
    d=api("occurrence/search",{**BASE,"taxonKey":list(keys.values()),"geometry":polygon(r,scale),"facet":["speciesKey","familyKey"],"facetLimit":1000})
    total=int(d["count"]);sp=facet(d,"speciesKey");fam=facet(d,"familyKey")
    if set(fam)-set(keys.values()): raise ValueError("unexpected family facet")
    if len(sp)>=1000: raise ValueError("species facet may be truncated")
    n=sum(sp.values());p=sum(c for s,c in sp.items() if s in pier);fc=fam.get(keys["Pieridae"],0)
    if n>total or p>fc or sum(fam.values())>total or sum(fam.values())!=total:
        raise ValueError("inconsistent species/family counts")
    result={"status":"retrieved","hits":total,"identified_species_hits":n,"pieridae_hits":fc,"pieridae_identified_hits":p,"observed_species":len(sp),"pieridae_observed_species":sum(s in pier for s in sp),"species_coverage":n/total if total else None,"pieridae_species_coverage":p/fc if fc else 1.}
    # Rarefaction denominator is all species-identified hits; fail if classification coverage poor.
    if total and n/total>=.95 and (fc==0 or p/fc>=.95):
        a=np.array(list(sp.values()));isp=np.array([s in pier for s in sp])
        for k in (50,100):
            if n>=k:
                w=rare(a,n,k)
                result[f"rarefied_all_{k}"]=float(w.sum())
                result[f"rarefied_pieridae_{k}"]=float(w[isp].sum())
                result[f"share_{k}"]=float(w[isp].sum()/w.sum())
    return result
def fit(df,outcome,include_temp=False,include_rain=True):
    f=df.copy()
    f["log_frogs"]=np.log1p(f.n_frogs);f["log_rain"]=np.log1p(f.rain);f["log_effort"]=np.log1p(f.identified_species_hits)
    f["abs_lat"]=f.lat.abs();f["sin_lon"]=np.sin(np.deg2rad(f.lon));f["cos_lon"]=np.cos(np.deg2rad(f.lon));f["log_support"]=np.log1p(f.native_centers)
    f["other_foam"]=f.variable+f.mixed
    base=["log_frogs","abs_lat","lat","sin_lon","cos_lon","log_effort","log_support"]+(["log_rain","rain_cv"] if include_rain else [])+(["temp"] if include_temp else [])
    extra=["exposed","sheltered","other_foam"]
    f=f.dropna(subset=[outcome,*base,*extra])
    n=len(f);b=f.block.nunique()
    if n<40 or b<8 or f.exposed.nunique()<3 or f.sheltered.nunique()<3:return {"status":"insufficient_support","n":n,"blocks":b}
    X=f[base+extra].astype(float);y=f[outcome].astype(float)
    if np.linalg.matrix_rank(sm.add_constant(X).values)<len(X.columns)+1:return {"status":"rank_deficient","n":n,"blocks":b}
    mod=sm.OLS(y,sm.add_constant(X)).fit(cov_type="cluster",cov_kwds={"groups":f.block},use_t=True)
    contrast=np.zeros(len(mod.params));contrast[list(mod.params.index).index("exposed")]=.1;contrast[list(mod.params.index).index("sheltered")]=-.1
    c=mod.t_test(contrast)
    ci=np.asarray(c.conf_int()).ravel()
    coefs={}
    for k in extra:
        coefs[k]={"effect_per_10pp":float(.1*mod.params[k]),"ci95":[float(.1*v) for v in mod.conf_int().loc[k]],"p":float(mod.pvalues[k])}
    fold=[]
    for train,test in GroupKFold(n_splits=5).split(f,groups=f.block):
        yy=y.iloc[test].to_numpy()
        p0=LinearRegression().fit(f.iloc[train][base],y.iloc[train]).predict(f.iloc[test][base])
        p1=LinearRegression().fit(f.iloc[train][base+extra],y.iloc[train]).predict(f.iloc[test][base+extra])
        fold.append({"n":len(test),"sse_base":float(np.sum((yy-p0)**2)),"sse_full":float(np.sum((yy-p1)**2))})
    s0=sum(z["sse_base"] for z in fold);s1=sum(z["sse_full"] for z in fold)
    return {"status":"exploratory_association","n":n,"blocks":b,"outcome":outcome,"temperature_included":include_temp,"rainfall_included":include_rain,"coefficients":coefs,"exposed_minus_sheltered_per_10pp":{"effect":float(np.asarray(c.effect).item()),"ci95":ci.tolist(),"p":float(np.asarray(c.pvalue).item())},"blocked_cv_mse_base":s0/n,"blocked_cv_mse_full":s1/n,"blocked_cv_relative_mse_gain":1-s1/s0 if s0>0 else None,"folds":fold,"r2":float(mod.rsquared)}
def main():
    p=argparse.ArgumentParser();p.add_argument("--scale",type=int,choices=[100,200],required=True);a=p.parse_args()
    out=Path("results/v1.5")/str(a.scale);out.mkdir(parents=True,exist_ok=True)
    f,meta,native=frame(a.scale);f.to_csv(out/"frozen_sample.csv",index=False)
    keys,pier,tax=taxonomy()
    print("PILOT_START "+json.dumps({"scale":a.scale,**meta,**tax},default=str),flush=True)
    rows=[]
    for i,r in enumerate(f.itertuples(index=False)):
        try:z=collect(r,a.scale,keys,pier)
        except Exception as e:z={"status":"query_failed","error":repr(e)}
        rows.append(z)
        if (i+1)%20==0:print("PILOT_PROGRESS",a.scale,i+1,len(f),flush=True)
    d=pd.concat([f,pd.DataFrame(rows)],axis=1)
    d.to_csv(out/"recipient_facets_before_climate.csv",index=False)
    # Preserve the occurrence output even when climate acquisition returns 429.
    clim,clim_meta=climate_after_recipient(native,f,a.scale)
    meta.update(clim_meta)
    d=d.merge(clim,on=["ix","iy"],how="left",validate="one_to_one")
    d.to_csv(out/"grid_butterfly_pilot.csv",index=False)
    for k in ["share_50","share_100","identified_species_hits","hits","pieridae_hits"]:
        if k not in d:d[k]=np.nan
    d["record_share"]=d.pieridae_hits/d.hits.where(d.hits>0)
    report={"status":"sampled_grid_pilot_not_fertilization","scale_km":a.scale,"sampling":meta,"taxonomy":tax,"api_requests":CALLS,"query_status":dict(Counter(d.status)),"errors":dict(Counter(d.loc[d.status!="retrieved","error"])) if "error" in d else {},"n_50":int(d.share_50.notna().sum()),"n_100":int(d.share_100.notna().sum()),"total_hits":int(d.hits.sum()),"zero_hits":int((d.hits==0).sum()),"strata_retention":d.groupby("exposure_stratum").share_50.agg(["size","count"]).to_dict("index"),"models":{}}
    for k in [50,100]:
        # Geography-only diagnostic explicitly not climate-adjusted.
        report["models"][str(k)+"_geography_only"]=fit(d,"share_"+str(k),include_rain=False)
        if meta["rainfall_status"]=="success":
            report["models"][str(k)+"_rain_lat"]=fit(d,"share_"+str(k))
            report["models"][str(k)+"_rain_lat_min5_frogs"]=fit(d.loc[d.n_frogs>=5],"share_"+str(k))
            if meta["temperature_status"]=="success":
                report["models"][str(k)+"_temperature"]=fit(d,"share_"+str(k),include_temp=True)
    if meta["rainfall_status"]=="success":
        report["models"]["record_share_rain_lat"]=fit(d.loc[d.identified_species_hits>=50],"record_share")
    (out/"summary.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str,allow_nan=False))
    print("BUTTERFLY_GRID_RESULT "+json.dumps(report,ensure_ascii=False,default=str,allow_nan=False),flush=True)
if __name__=="__main__":main()
