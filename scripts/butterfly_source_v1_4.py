#!/usr/bin/env python3
"""Audit existing global butterfly data sources. No whole multi-GB archive download."""
import hashlib,io,json,urllib.request
from pathlib import Path
import pandas as pd
OUT=Path("results/v1.4");OUT.mkdir(parents=True,exist_ok=True)
def get(url,max_bytes):
    req=urllib.request.Request(url,headers={"User-Agent":"AECO/1.4 academic research (github.com/zuizui0223/aeco)"})
    with urllib.request.urlopen(req,timeout=60) as r:
        data=r.read(max_bytes+1)
        if len(data)>max_bytes: raise ValueError("download cap exceeded")
        return data,{"url":url,"final_url":r.geturl(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
report={}
url="https://storage.googleapis.com/cdn.mol.org/dataset_downloads/butterflies_country_checklist_v4.csv"
try:
    data,meta=get(url,30_000_000)
    d=pd.read_csv(io.BytesIO(data),dtype=str)
    report["checklist"]={**meta,"status":"schema_acquired","rows":len(d),"columns":list(d.columns),"first_rows":d.head(3).to_dict("records"),"scope":"country occurrence checklist, not gridded distribution or behavior"}
    for col in d.columns:
        if col.lower() in {"family","family_name","familyname","family_nam"}:
            report["checklist"]["family_counts"]=d[col].value_counts().to_dict()
except Exception as e: report["checklist"]={"status":"failed","error":repr(e),"url":url}
url="https://datadryad.org/downloads/file_stream/3377657"
try:
    req=urllib.request.Request(url,headers={"Range":"bytes=-65536","User-Agent":"AECO/1.4 academic research (github.com/zuizui0223/aeco)","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=60) as r:
        if r.status!=206: raise ValueError("server does not honor byte range; not downloading full archive")
        data=r.read(65537)
        if len(data)>65536: raise ValueError("range too large")
        report["range_archive_probe"]={"status":"range_supported","content_range":r.headers.get("Content-Range"),"bytes":len(data),"zip_end_signature_found":b"PK\x05\x06" in data,"scope":"archive range probe only, no species ranges"}
except Exception as e: report["range_archive_probe"]={"status":"failed","error":repr(e),"url":url}
(OUT/"butterfly_sources.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str))
print("BUTTERFLY_SOURCE_RESULT "+json.dumps(report,ensure_ascii=False,default=str),flush=True)
