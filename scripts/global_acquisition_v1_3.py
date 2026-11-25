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
            entry["status"]="schema_acquired_not_normalized"
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
