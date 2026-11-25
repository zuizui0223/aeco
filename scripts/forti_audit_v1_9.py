#!/usr/bin/env python3
"""Fetch Forti et al. 2022 Table S2 by published checksum; schema audit without raw observations."""
import hashlib,io,json,time,urllib.request
from pathlib import Path
from collections import Counter
from openpyxl import load_workbook
URLS=["https://zenodo.org/records/6811407/files/TableS2.xlsx?download=1","https://zenodo.org/api/records/6811407/files/TableS2.xlsx/content","https://zenodo.org/record/6811407/files/TableS2.xlsx?download=1"]
MD5="1da34c8eda2252cfb2bb12a4e9055555"
OUT=Path("results/v1.9");OUT.mkdir(parents=True,exist_ok=True)
def acquire():
    errors=[]
    for url in URLS:
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"AECO/1.9 research (https://github.com/zuizui0223/aeco)"})
            with urllib.request.urlopen(req,timeout=30) as r:
                b=r.read(5_000_001);final=r.geturl()
            if len(b)>5_000_000 or hashlib.md5(b).hexdigest()!=MD5:raise ValueError("checksum mismatch or oversize")
            return b,{"url":url,"final_url":final,"md5":MD5,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"previous_errors":errors}
        except Exception as e:errors.append({"url":url,"error":repr(e)});time.sleep(2)
    raise RuntimeError(str(errors))
def main():
    b,meta=acquire()
    w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    sheets=[]
    for s in w:
        # Only headers, structure and aggregated frequency of cell data types.
        # No exact coordinates, dates, usernames, individual observations or URLs.
        it=s.iter_rows(values_only=True)
        first=list(next(it));types=[Counter() for _ in first]
        sample_rows=0
        for row in it:
            sample_rows+=1
            for i,v in enumerate(row[:len(first)]):
                types[i][type(v).__name__]+=1
        sheets.append({"name":s.title,"max_rows":s.max_row,"max_columns":s.max_column,"header":[str(v) if v is not None else None for v in first],"types":[dict(v) for v in types],"remaining_rows":sample_rows})
    w.close()
    result={"status":"checksum_verified_workbook_schema","provenance":meta,"sheets":sheets}
    (OUT/"forti_schema.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("FORTI_SCHEMA "+json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
