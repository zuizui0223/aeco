#!/usr/bin/env python3
"""Actual public source acquisition audit; no ecological inference from failures."""
import argparse,csv,hashlib,io,json,math,re,time,urllib.parse,urllib.request,zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from openpyxl import load_workbook
ROOT=Path("results/v1.3_acquisition")
ROOT.mkdir(parents=True,exist_ok=True)
SOURCES={
 "nunes2021":("https://www.salamandra-journal.com/salamandra/57-2021/57-3/57-3%2C%2012%20Nunes-de-Almeida%20et%20al%20Supplementary%20Table.xlsx","xlsx"),
 "pereira2015":("https://media.springernature.com/original/springer-static/esm/art%3A10.1186%2Fs12862-015-0365-6/MediaObjects/12862_2015_365_MOESM2_ESM.docx","docx")
}
def request(url,max_bytes=15_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"AECO-research/1.3 (github.com/zuizui0223/aeco)","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read(max_bytes+1)
        if len(raw)>max_bytes: raise ValueError("oversize")
        return raw,r.geturl(),r.headers.get("Content-Type")

def normalize_nunes(w, source_sha):
    """Parse one-hot documented modes, retaining all modes and uncertain rows."""
    s=w["Table S1"]
    rows=s.iter_rows(values_only=True)
    next(rows)
    header=next(rows)
    assert tuple(header[:3])==("Group","Family","Species"), repr(header[:3])
    cols={}
    for i,v in enumerate(header):
        if str(v).strip().isdigit():
            code=int(str(v).strip())
            if 1<=code<=74:
                assert code not in cols, code
                cols[code]=i
    assert set(cols)==set(range(1,75)), sorted(cols)
    cross={int(r["mode"]):r for r in csv.DictReader(Path("data/literature/foam_mode_crosswalk_v1.2.csv").open())}
    assert set(cross)==set(range(44,66))
    records=[]; anomalies=Counter(); marker_values=Counter(); excluded_groups=Counter()
    for row in rows:
        group=str(row[0] or "").strip()
        if group.lower()!="anura":
            if group: excluded_groups[group]+=1
            continue
        family=str(row[1] or "").strip()
        name=str(row[2] or "").strip()
        if not family or not name:
            anomalies["missing_family_or_species"]+=1
            continue
        modes=[]; unusual=[]
        for k,i in cols.items():
            v=row[i] if i<len(row) else None
            if v is None or str(v).strip()=="": continue
            marker_values[str(v)]+=1
            if str(v).strip() in {"1","1.0"}: modes.append(k)
            elif str(v).strip() not in {"0","0.0"}: unusual.append(f"{k}:{v}")
        froth=[k for k in modes if 44<=k<=64]
        exposure=sorted({cross[k]["potential_exposure_class"] for k in froth})
        if unusual: typ="unresolved_marker"
        elif not modes: typ="unknown_mode"
        elif froth:
            typ="froth_"+(exposure[0] if len(exposure)==1 else "mixed_exposure")
        elif 65 in modes: typ="bubble_only"
        else: typ="no_documented_froth_or_bubble"
        records.append(dict(species_as_used=name,family_as_used=family,modes=";".join(map(str,modes)),froth_modes=";".join(map(str,froth)),potential_exposure=";".join(exposure),trait_class=typ,unusual_markers=";".join(unusual)))
    name_counts=Counter(r["species_as_used"] for r in records)
    duplicate_names={k:v for k,v in name_counts.items() if v>1}
    unique=[r for r in records if name_counts[r["species_as_used"]]==1]
    by_class=Counter(r["trait_class"] for r in unique)
    foam=[r for r in unique if r["trait_class"].startswith("froth_")]
    mode_counts=Counter(int(m) for r in foam for m in r["froth_modes"].split(";") if m)
    fam=Counter(r["family_as_used"] for r in foam)
    n_known=sum(v for k,v in by_class.items() if k not in {"unresolved_marker","unknown_mode"})
    report=dict(status="normalized_source_taxonomy",source_sha256=source_sha,anura_rows=len(records),unique_species_name_rows=len(unique),duplicate_names=duplicate_names,excluded_groups=dict(excluded_groups),anomalies=dict(anomalies),marker_values=dict(marker_values),trait_counts=dict(by_class),n_known_modes=n_known,n_strict_froth=len(foam),froth_by_family=dict(fam),froth_mode_counts=dict(sorted(mode_counts.items())),n_multiple_froth_modes=sum(";" in r["froth_modes"] for r in foam),notes="Documented reproductive modes, not global completeness or fixed exposure; duplicate names excluded from aggregate. No taxonomic harmonization, spatial or fertility inference.")
    (ROOT/"nunes2021_trait_summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    if records:
        with (ROOT/"nunes2021_traits.csv").open("w",newline="",encoding="utf-8") as fh:
            out=csv.DictWriter(fh,fieldnames=list(records[0]))
            out.writeheader()
            out.writerows(records)
    print("NUNES_NORMALIZED "+json.dumps(report,ensure_ascii=False))
    return report

def get_sources():
    report={}
    for name,(url,kind) in SOURCES.items():
        entry={"url":url,"status":"not_acquired"}
        try:
            raw,final,ctype=request(url)
            if not raw.startswith(b"PK"): raise ValueError("not a ZIP-based Office file")
            entry.update(final_url=final,content_type=ctype,size_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            if kind=="xlsx":
                w=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
                entry["sheets"]=[]
                for s in w:
                    preview=[[str(v)[:100] if v is not None else None for v in r] for r in s.iter_rows(min_row=1,max_row=6,max_col=min(s.max_column or 25,25),values_only=True)]
                    entry["sheets"].append({"name":s.title,"rows":s.max_row,"cols":s.max_column,"preview":preview})
                entry["trait_summary"]=normalize_nunes(w,entry["sha256"])
                w.close()
            else:
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    root=ET.fromstring(z.read("word/document.xml"))
                    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                    entry["tables"]=[]
                    for table in root.findall(".//w:tbl",ns):
                        rows=[]
                        for tr in table.findall("./w:tr",ns):
                            rows.append([" ".join(t.text or "" for t in tc.findall(".//w:t",ns))[:100] for tc in tr.findall("./w:tc",ns)])
                        entry["tables"].append({"rows":len(rows),"preview":rows[:6]})
            entry["status"]="normalized_source_taxonomy" if kind=="xlsx" else "schema_acquired_not_normalized"
        except Exception as exc:
            entry.update(error=type(exc).__name__+": "+str(exc))
        report[name]=entry
    return report
def query(path,params):
    url="https://api.gbif.org/v1/"+path+"?"+urllib.parse.urlencode(params,doseq=True)
    raw,_,_=request(url,4_000_000)
    return json.loads(raw)
def gbif_seed():
    # Facet counts are ordinary adult/unknown-stage observations, not breeding or foam supply.
    # Query exact taxon matches and public count facets. No raw coordinates are exported.
    src=list(csv.DictReader(Path("data/literature/foam_seed_species_v1.3.csv").open()))
    out=[]
    for s in src:
        name=s["species_as_used"]; row={"name":name,"status":"unresolved"}
        try:
            m=query("species/match",{"name":name,"strict":"true"})
            key=m.get("speciesKey") or m.get("usageKey")
            if m.get("matchType")!="EXACT" or m.get("rank")!="SPECIES" or not key or m.get("family")!=s["family_as_used"]:
                row.update(match=m);out.append(row);continue
            # Exact or accepted synonym match; preserve taxonomy and do not infer absent months from truncated facet.
            q={"taxonKey":key,"year":"2010,2021","hasCoordinate":"true","hasGeospatialIssue":"false","occurrenceStatus":"PRESENT","limit":0,"facet":["month","country"],"facetLimit":300}
            d=query("occurrence/search",q)
            if not isinstance(d.get("count"),int): raise ValueError("invalid GBIF count")
            row.update(status="occurrence_facets_not_reproductive_data",key=key,match=m,count=d["count"],facets=d.get("facets",[]))
            time.sleep(0.4)
        except Exception as e:
            row.update(status="query_failed",error=type(e).__name__+": "+str(e))
        out.append(row)
    return out
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sources-only",action="store_true")
    a=p.parse_args()
    r={"source_audits":get_sources(),"scope":"Source acquisition, ordinary occurrence counts, no actual nesting rates or butterfly associations"}
    (ROOT/"source_schema.json").write_text(json.dumps(r,ensure_ascii=False,indent=2))
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if not a.sources_only:
        rows=gbif_seed()
        out={"status":"pilot_only","records":rows,"n_queried":len(rows),"n_success":sum(x["status"]=="occurrence_facets_not_reproductive_data" for x in rows)}
        (ROOT/"gbif_seed_facets.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
        print(json.dumps({"n_queried":out["n_queried"],"n_success":out["n_success"],"per_species_counts":[{"name":x["name"],"count":x.get("count"),"status":x["status"]} for x in rows]},ensure_ascii=False,indent=2))
