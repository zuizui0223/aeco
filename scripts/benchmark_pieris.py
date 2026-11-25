#!/usr/bin/env python3
"""Published P. napi heat experiment: descriptive postcopulatory hatch benchmark.
Not direct fertilization; no frog/landscape treatment.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request
from collections import defaultdict
from pathlib import Path

URL = "https://datadryad.org/downloads/file_stream/3925622"
REQUIRED = ("Experiment","Female","Treatment_Female","Treatment_Male","Eggs_day_3","Larvae_day_3")
MISSING = {"","na","nan","null"}

def number(value):
    if value is None or str(value).strip().lower() in MISSING:
        return None
    n=float(value)
    if not math.isfinite(n) or n<0 or n!=int(n):
        raise ValueError("Invalid count")
    return int(n)

def summarize(raw):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames is None:
        raise ValueError("Empty source")
    reader.fieldnames=[s.strip() for s in reader.fieldnames]
    if not set(REQUIRED)<=set(reader.fieldnames):
        raise ValueError("Unexpected CSV schema; inspect Dryad version and headers")
    groups=defaultdict(lambda: dict(rows=0,complete=0,missing=0,missing_female_id=0,zero_eggs=0,any_hatch=0,eggs=0,larvae=0))
    ids=set()
    for row in reader:
        if None in row:
            raise ValueError("Malformed CSV")
        ft,mt=number(row["Treatment_Female"]),number(row["Treatment_Male"])
        if ft not in (22,29) or mt not in (22,29):
            raise ValueError("Unrecognized treatment")
        year=(row["Experiment"] or "").strip()
        female=(row["Female"] or "").strip()
        g=groups[(year,ft,mt)]
        g["rows"]+=1
        if female.lower() in MISSING or year.lower() in MISSING:
            g["missing_female_id"]+=1
        else:
            key=(year,female)
            if key in ids:
                raise ValueError("Duplicate experiment/female ID; verify grain before aggregating")
            ids.add(key)
        e,l=number(row["Eggs_day_3"]),number(row["Larvae_day_3"])
        if e is None or l is None:
            g["missing"]+=1
            continue
        if l>e:
            raise ValueError("Hatched larvae exceed eggs")
        g["complete"]+=1
        g["zero_eggs"]+=int(e==0)
        g["any_hatch"]+=int(l>0)
        g["eggs"]+=e
        g["larvae"]+=l
    if not groups:
        raise ValueError("No rows")
    out=[]
    for (year,ft,mt),g in sorted(groups.items()):
        out.append(dict(experiment=year,female_temp=ft,male_temp=mt,**g,
                        proportion_rows_with_any_hatch=g["any_hatch"]/g["complete"] if g["complete"] else None,
                        pooled_hatch_fraction=g["larvae"]/g["eggs"] if g["eggs"] else None))
    return dict(status="descriptive_mated_rows_only",doi="10.5061/dryad.dfn2z35cj",source=URL,
                sha256=hashlib.sha256(raw).hexdigest(),groups=out,
                caveats="Hatch is not direct fertilization. Only rows in postcopulatory experiment; unmated population denominator unavailable here. Missing IDs and incomplete counts reported; no causal spatial inference. No confidence intervals from pooled eggs.")

def self_test():
    raw=b"Experiment,Female,Treatment_Female,Treatment_Male,Eggs_day_3,Larvae_day_3\n1,F1,22,22,10,5\n1,F2,22,22,0,0\n1,F3,22,22,NA,NA\n1,F4,22,29,8,0\n"
    a=summarize(raw)["groups"][0]
    assert a["rows"]==3 and a["complete"]==2 and a["missing"]==1 and a["zero_eggs"]==1
    assert a["pooled_hatch_fraction"]==.5 and a["proportion_rows_with_any_hatch"]==.5
    try:
        summarize(raw+b"1,F1,22,22,1,0\n")
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate not detected")
    print("Synthetic schema checks passed; no empirical inference.")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path,default=Path("results/pieris_hatch_benchmark.json"))
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        self_test()
        return
    try:
        if args.input:
            raw=args.input.read_bytes()
        else:
            req=urllib.request.Request(URL,headers={"User-Agent":"AECO-research/0.3 (github.com/zuizui0223/aeco)"})
            with urllib.request.urlopen(req,timeout=40) as response:
                raw=response.read(1000001)
        if len(raw)>1000000:
            raise ValueError("Source unexpectedly large")
        out=summarize(raw)
    except (OSError,ValueError) as exc:
        out={"status":"acquisition_or_schema_failed","source":URL,"error":str(exc),"groups":[]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(out["status"])
    if out["status"]!="descriptive_mated_rows_only":
        raise SystemExit(2)

if __name__=="__main__":
    main()
