#!/usr/bin/env python3
"""Bounded raw-data acquisition and schema audit. No duration inference from file names."""
import hashlib,io,json,urllib.request,urllib.parse,zipfile
from pathlib import Path
from openpyxl import load_workbook
OUT=Path("results/v2.1_sources");OUT.mkdir(parents=True,exist_ok=True)
def fetch(url,max_bytes=15000000):
    q=urllib.request.Request(url,headers={"User-Agent":"AECO research 2.1 (https://github.com/zuizui0223/aeco)","Accept":"*/*"})
    with urllib.request.urlopen(q,timeout=30) as r:
        b=r.read(max_bytes+1)
        if len(b)>max_bytes:raise ValueError("cap exceeded")
        return b,{"url":url,"final_url":r.geturl(),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"md5":hashlib.md5(b).hexdigest()}
def schema(name,b):
    ext=Path(name).suffix.lower()
    if ext in {".xlsx",".xlsm"}:
        w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
        s=[]
        for a in w:
            head=[]
            for row in a.iter_rows(min_row=1,max_row=min(4,a.max_row or 4),max_col=min(35,a.max_column or 35),values_only=True):
                head.append([str(v)[:100] if v is not None else None for v in row])
            s.append({"name":a.title,"rows":a.max_row,"columns":a.max_column,"first_four_rows":head})
        w.close();return {"sheets":s}
    if ext in {".csv",".tsv",".txt"}:
        return {"first_four_lines":b.decode("utf-8-sig",errors="replace").splitlines()[:4]}
    if ext==".zip":
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            return {"members":[{"name":i.filename,"uncompressed_bytes":i.file_size} for i in z.infolist()]}
    return {"status":"not_parsed"}
def figshare():
    url="https://api.figshare.com/v2/articles/23667387"
    b,m=fetch(url,2000000);d=json.loads(b)
    if str(d.get("id"))!="23667387" or not str(d.get("doi","")).lower().startswith("10.6084/m9.figshare.23667387"):raise ValueError("Figshare DOI/id mismatch: "+str({k:d.get(k) for k in ("id","doi","title")}))
    result={"metadata":m,"title":d.get("title"),"doi":d.get("doi"),"license":d.get("license"),"files":[]}
    for f in d.get("files",[]):
        q={k:f.get(k) for k in ("id","name","size","computed_md5","supplied_md5","downloadUrl")}
        try:
            if f["size"]>15000000:raise ValueError("file over cap")
            b,m=fetch(f["downloadUrl"])
            if len(b)!=f["size"] or (f.get("computed_md5") and m["md5"]!=f["computed_md5"]):raise ValueError("file checksum mismatch")
            q.update(status="acquired",provenance=m,schema=schema(f["name"],b))
        except Exception as e:q.update(status="failed",error=repr(e))
        result["files"].append(q)
    return result
def dryad(doi):
    url="https://datadryad.org/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe="")
    b,m=fetch(url,2000000);d=json.loads(b)
    if d.get("identifier") not in {doi,"doi:"+doi}:raise ValueError("Dryad DOI mismatch")
    result={"metadata":m,"identifier":d.get("identifier"),"title":d.get("title"),"files":[]}
    def link(href):
        return urllib.parse.urljoin("https://datadryad.org",href)
    vurl=link(d["_links"]["stash:version"]["href"])
    b,vm=fetch(vurl,2000000);v=json.loads(b)
    furl=link(v["_links"]["stash:files"]["href"])
    b,fm=fetch(furl,2000000);files=json.loads(b)
    result["file_manifest_provenance"]=fm
    for f in files["_embedded"]["stash:files"]:
        q={"path":f.get("path"),"size":f.get("size"),"digest":f.get("digest"),"digestType":f.get("digestType")}
        name=f.get("path") or ""
        if not name.lower().endswith((".xlsx",".csv",".txt",".md")):continue
        try:
            if f.get("size",0)>15000000:raise ValueError("file over cap")
            b,m=fetch(link(f["_links"]["stash:download"]["href"]))
            if f.get("size") is not None and len(b)!=f["size"]:raise ValueError("size mismatch")
            dt=str(f.get("digestType","")).lower().replace("-","")
            if dt in {"md5","sha256"} and f.get("digest")!=m[dt]:raise ValueError("digest mismatch")
            q.update(status="acquired",provenance=m,schema=schema(name,b))
        except Exception as e:q.update(status="failed",error=repr(e))
        result["files"].append(q)
    return result
if __name__=="__main__":
    out={}
    for key,fn in [("japan_thermal_nests",figshare),("panama_hydration",lambda:dryad("10.5061/dryad.866t1g1r2")),("africa_nest_geometry",lambda:dryad("10.5061/dryad.9s4mw6mx8"))]:
        try:out[key]=fn()
        except Exception as e:out[key]={"status":"failed","error":repr(e)}
    (OUT/"source_audit.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("LEGACY_SOURCE_AUDIT "+json.dumps(out,ensure_ascii=False),flush=True)
