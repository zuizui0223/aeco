#!/usr/bin/env python3
"""V1.4: exact-name range join + equal-area grid + satellite-gauge rainfall.
Only range-cell centers, never a nest abundance or fertility surface."""
import hashlib,io,json,math,os,re,urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import pyreadr
import pyproj
import xarray as xr
from global_acquisition_v1_3 import SOURCES, request, normalize_nunes, ROOT
from openpyxl import load_workbook

OUT=Path("results/v1.4")
OUT.mkdir(parents=True,exist_ok=True)
WORK=Path("scratch/v1.4")
WORK.mkdir(parents=True,exist_ok=True)
PROVENANCE={}
def get(url,name,max_bytes=60_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"AECO/1.4 academic research (github.com/zuizui0223/aeco)"})
    p=WORK/name
    with urllib.request.urlopen(req,timeout=90) as res, p.open("wb") as f:
        size=0; sha=hashlib.sha256()
        while True:
            block=res.read(1024*1024)
            if not block: break
            size+=len(block)
            if size>max_bytes: raise ValueError("download exceeds bound: "+name)
            sha.update(block); f.write(block)
        PROVENANCE[name]={"url":url,"final_url":res.geturl(),"bytes":size,"sha256":sha.hexdigest()}
    return p
def names(x):
    return x.astype("string").str.replace("_"," ",regex=False).str.strip().str.replace(r"\s+"," ",regex=True)
def load_traits():
    raw,final,ctype=request(SOURCES["nunes2021"][0])
    sha=hashlib.sha256(raw).hexdigest()
    if sha!="3ec2b6ab0d457cf6bcd4bcbabd7bf51aa2ea3f1ec898d297f1f68a46a883b964":
        raise ValueError("trait source changed, re-audit")
    PROVENANCE["nunes2021"]={"url":final,"sha256":sha,"bytes":len(raw)}
    w=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    normalize_nunes(w,sha);w.close()
    t=pd.read_csv(ROOT/"nunes2021_traits.csv",dtype=str,keep_default_na=False)
    t["species"]=names(t.species_as_used)
    t=t.loc[~t.species.duplicated(keep=False)].copy()
    assert len(t)==2010 and t.trait_class.str.startswith("froth_").sum()==253
    return t
def read_ranges():
    # Frozen verified v1.4 source (avoid a moving API query or rate-limit dependency).
    ref="8c007900ceb2679f8aee04aec4d936648df5191b"
    path=get(f"https://raw.githubusercontent.com/RS-eco/rasterSp/{ref}/data/amphibians_dist.rda","amphibians_dist.rda",40_000_000)
    if PROVENANCE["amphibians_dist.rda"]["sha256"]!="f197cff80d0de3f9b3b7e524540903db429a549c4dea2d5d462079cfac478f84":
        raise ValueError("Frozen amphibian range bytes changed")
    o=pyreadr.read_r(str(path))
    assert len(o)==1,list(o)
    d=next(iter(o.values()))
    print("RANGE_SCHEMA",json.dumps({"ref":ref,"n":len(d),"columns":list(d.columns),"head":d.head(3).to_dict("records")},default=str),flush=True)
    assert {"x","y","species"}<=set(d.columns),list(d.columns)
    d=d[["x","y","species"]].copy()
    d["species"]=names(d.species)
    d["x"]=pd.to_numeric(d.x,errors="coerce")
    d["y"]=pd.to_numeric(d.y,errors="coerce")
    before=len(d)
    d=d.dropna().drop_duplicates()
    if not (d.x.between(-180,180).all() and d.y.between(-90,90).all()): raise ValueError("coordinates not WGS84")
    for v in ("x","y"):
        if not np.allclose((d[v].to_numpy()-.25)/.5,np.rint((d[v].to_numpy()-.25)/.5),atol=1e-5): raise ValueError("unexpected half-degree cell centers")
    return d,{"source_ref":ref,"source_rows":before,"unique_valid_rows":len(d),"species":int(d.species.nunique()),"native_cells":len(d[["x","y"]].drop_duplicates())}
def rainfall(d):
    p=get("https://psl.noaa.gov/thredds/fileServer/Datasets/gpcp/precip.mon.mean.nc","gpcp_monthly.nc",50_000_000)
    with xr.open_dataset(p,decode_times=False) as ds:
        # PSL file uses a non-standard timezone suffix "0:00". Decode the verified
        # numeric day offset explicitly, and fail closed for a different epoch.
        units=str(ds.time.attrs.get("units",""))
        if not re.match(r"^days since 1800-0?1-0?1(?:\s|$)",units):
            raise ValueError("Unexpected GPCP time units: "+units)
        dates=pd.to_datetime(ds.time.values,unit="D",origin="1800-01-01")
        assert pd.Index(dates).is_unique and dates.is_monotonic_increasing
        a=ds["precip"].assign_coords(time=dates).sel(time=slice("2010-01-01","2021-12-31"))
        assert list(pd.DatetimeIndex(a.time.values).to_period("M"))==list(pd.period_range("2010-01","2021-12",freq="M"))
        assert a.sizes["time"]==144 and a.sizes["lat"]==72 and a.sizes["lon"]==144,dict(a.sizes)
        assert a.attrs.get("units") in ("mm/day","mm/d","mm day-1"),a.attrs
        # Total rain per month, then climatology, at the native 2.5-degree scale.
        mm=a*a.time.dt.days_in_month
        clim=mm.groupby("time.month").mean("time",skipna=False)
        ann=clim.sum("month",skipna=False)
        cv=clim.std("month",skipna=False)/clim.mean("month",skipna=False).where(clim.mean("month",skipna=False)>0)
        c=d[["x","y"]].drop_duplicates().copy()
        yi=xr.DataArray(c.y.to_numpy(),dims=["points"])
        xi=xr.DataArray(c.x.to_numpy()%360,dims=["points"])
        # Periodic longitude nearest bins; grid centers are 1.25, 3.75, ..., 358.75.
        # floor bin indexing maps 359.9 to 358.75, 0.1 to 1.25.
        lons=(np.floor(xi/2.5)*2.5+1.25)
        lats=(np.floor((yi+90)/2.5)*2.5-88.75).clip(-88.75,88.75)
        c["rain_annual_mm"]=ann.sel(lat=lats,lon=lons,method="nearest").values
        c["rain_month_cv"]=cv.sel(lat=lats,lon=lons,method="nearest").values
        c["gpcp_lon"]=lons.values; c["gpcp_lat"]=lats.values
        return c,{"months":144,"native_resolution_deg":2.5,"variables":["annualized 2010–2021 monthly climatology precipitation (mm/year)","CV across 12 climatological monthly totals"],"valid_native_cells":int(np.isfinite(ann.values).sum()),"years":"2010–2021"}
def grid(d,scale):
    tr=pyproj.Transformer.from_crs(4326,6933,always_xy=True)
    f=d.loc[d.y.between(-86,86)].copy()
    x,y=tr.transform(f.x.to_numpy(),f.y.to_numpy())
    f["ix"]=np.floor(x/(scale*1000)).astype(int)
    f["iy"]=np.floor(y/(scale*1000)).astype(int)
    u=f[["ix","iy","species","trait_class","family_as_used"]].drop_duplicates()
    g=u.groupby(["ix","iy","trait_class"],observed=True).size().unstack(fill_value=0)
    g=g.reindex(columns=["froth_potentially_exposed","froth_sheltered","froth_variable","froth_mixed_exposure","bubble_only","no_documented_froth_or_bubble"],fill_value=0).reset_index()
    cols=["froth_potentially_exposed","froth_sheltered","froth_variable","froth_mixed_exposure"]
    g["froth_total"]=g[cols].sum(axis=1)
    g["known_traits_total"]=g[cols+["bubble_only","no_documented_froth_or_bubble"]].sum(axis=1)
    g["froth_fraction"]=g.froth_total/g.known_traits_total
    g.to_csv(OUT/f"frog_grid_{scale}km.csv",index=False)
    # Family-specific exposure contrasts: within families with both mapped classes.
    fam=u[u.trait_class.isin(["froth_potentially_exposed","froth_sheltered"])].groupby(["family_as_used","trait_class"],observed=True).species.nunique().unstack(fill_value=0)
    return {"cells_with_known_traits":len(g),"cells_with_any_froth":int((g.froth_total>0).sum()),"cells_with_exposed":int((g.froth_potentially_exposed>0).sum()),"cells_with_sheltered":int((g.froth_sheltered>0).sum()),"cells_with_both_exposed_sheltered":int(((g.froth_potentially_exposed>0)&(g.froth_sheltered>0)).sum()),"max_froth_richness":int(g.froth_total.max()),"max_exposed_richness":int(g.froth_potentially_exposed.max()),"max_sheltered_richness":int(g.froth_sheltered.max()),"species_cell_pairs":len(u),"family_exposed_sheltered_species":fam.to_dict()}
def summarize_climate(j,c):
    f=j.merge(c,on=["x","y"],how="left",validate="many_to_one")
    f=f[np.isfinite(f.rain_annual_mm)&np.isfinite(f.rain_month_cv)].copy()
    f["w"]=np.cos(np.deg2rad(f.y))
    f["w_rain"]=f.w*f.rain_annual_mm
    f["w_cv"]=f.w*f.rain_month_cv
    s=f.groupby(["species","family_as_used","trait_class"],observed=True).agg(native_cells=("w","size"),w=("w","sum"),rain=("w_rain","sum"),cv=("w_cv","sum")).reset_index()
    s["rain_annual_mm"]=s.rain/s.w
    s["rain_month_cv"]=s.cv/s.w
    # Species-weighted descriptive medians; no p-values (phylogeny and geography).
    by=s.groupby("trait_class",observed=True).agg(n_species=("species","nunique"),median_rain_mm=("rain_annual_mm","median"),median_rain_cv=("rain_month_cv","median")).reset_index()
    q=s[s.trait_class.isin(["froth_potentially_exposed","froth_sheltered"])]
    fam=q.groupby(["family_as_used","trait_class"],observed=True).agg(n_species=("species","size"),median_rain_mm=("rain_annual_mm","median"),median_rain_cv=("rain_month_cv","median")).reset_index()
    return {"species_weighted":by.to_dict("records"),"within_family_descriptive":fam.to_dict("records"),"species_with_climate":len(s),"native_range_cell_rows_with_climate":len(f),"distinct_gpcp_cells":len(f[["gpcp_lat","gpcp_lon"]].drop_duplicates())}
def main():
    t=load_traits()
    d,range_meta=read_ranges()
    mapped=t[t.species.isin(set(d.species))]
    coverage=t.groupby("trait_class").size().rename("source").to_frame().join(mapped.groupby("trait_class").size().rename("matched")).fillna(0).astype(int)
    coverage["unmatched"]=coverage.source-coverage.matched
    j=d.merge(t[["species","trait_class","family_as_used"]],on="species",how="inner",validate="many_to_one")
    if not len(j): raise ValueError("no name matches")
    report={"status":"range_join_complete","range_source":range_meta,"trait_coverage":coverage.to_dict("index"),"matched_species":int(j.species.nunique()),"matched_species_cell_rows":len(j),"unmatched_species_by_class":t.loc[~t.species.isin(set(d.species))].groupby("trait_class").species.apply(list).to_dict(),"grid":{str(k):grid(j,k) for k in (100,200)},"limitations":["Exact normalized binomial join only; unresolved synonyms and historical range omissions not absence.","Range maps derived from 2017 IUCN data, trait source 2021; no direct occurrences or reproduction records.","0.5-degree source-cell centers assigned to EPSG:6933 squares; not exact polygon intersection. Known-trait richness, not total frog richness.","Mode-based potential exposure, not actual nest surface or abundance. No butterflies or fertilization outcomes."]}
    try:
        climate,meta=rainfall(j)
        report.update(status="range_and_rainfall_complete",rainfall_source=meta,climate=summarize_climate(j,climate))
    except Exception as exc:
        report.update(rainfall_status="failed",rainfall_error=repr(exc))
    report["provenance"]=PROVENANCE
    (OUT/"frog_range_summary.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False))
    compact={k:v for k,v in report.items() if k not in {"unmatched_species_by_class","limitations"}}
    print("GLOBAL_RANGE_RESULT "+json.dumps(compact,ensure_ascii=False,allow_nan=False),flush=True)
if __name__=="__main__": main()
