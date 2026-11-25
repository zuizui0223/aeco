#!/usr/bin/env python3
"""Acquire exact published workbook and audit schema; no automatic inference of species traits.
Optional explicit schema: one taxon per row and integer reproductive-mode cells.
Unknown or mixed codes remain unknown; modes outside 44-65 are not automatically true absences
if completeness of the species' nesting behavior has not been verified.
"""
import argparse,csv,hashlib,json,re,urllib.request
from pathlib import Path
from collections import Counter
from openpyxl import load_workbook

URL="https://www.salamandra-journal.com/salamandra/57-2021/57-3/57-3%2C%2012%20Nunes-de-Almeida%20et%20al%20Supplementary%20Table.xlsx"
MAP=Path("data/literature/foam_mode_crosswalk_v1.2.csv")
OUT=Path("results/global_trait_audit_v1.2.json")
MAX_BYTES=15_000_000

def get(path):
    if path.exists():
        raw=path.read_bytes()
    else:
        req=urllib.request.Request(URL,headers={"User-Agent":"AECO/1.2 research (github.com/zuizui0223/aeco)"})
        with urllib.request.urlopen(req,timeout=45) as r:
            raw=r.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES or not raw.startswith(b"PK"):
            raise ValueError("unexpected workbook bytes")
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)
    if len(raw)>MAX_BYTES or not raw.startswith(b"PK"):
        raise ValueError("invalid or oversized workbook")
    return hashlib.sha256(raw).hexdigest()

def parse_codes(val):
    if val is None or isinstance(val,bool): return None
    if isinstance(val,int): return [val] if 1<=val<=74 else None
    if isinstance(val,float): return [int(val)] if val.is_integer() and 1<=val<=74 else None
    s=str(val).strip()
    if not re.fullmatch(r"\d{1,2}(?:\s*[,;/|]\s*\d{1,2})*",s): return None
    a=[int(x) for x in re.split(r"\s*[,;/|]\s*",s)]
    return a if all(1<=x<=74 for x in a) else None

def classify(codes,mapping):
    if not codes: return "unknown",[]
    hits=[mapping[c] for c in sorted(set(codes)) if c in mapping]
    strict=[x for x in hits if x["foam_strict"]=="1"]
    if strict:
        return "foam_reported",sorted({x["potential_exposure_class"] for x in strict})
    if any(x["mode"]=="65" for x in hits): return "bubble_reported",[]
    return "no_foam_mode_reported",[]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("scratch/foam_modes_2021.xlsx"))
    p.add_argument("--output",type=Path,default=OUT)
    p.add_argument("--sheet")
    p.add_argument("--header-row",type=int)
    p.add_argument("--species-col",type=int,help="1-based")
    p.add_argument("--mode-col",type=int,action="append",help="1-based, repeat for separate mode columns")
    a=p.parse_args()
    report={"source":URL,"status":"started","scope":"workbook schema audit; not a global ecology result"}
    try:
        sha=get(a.input)
        w=load_workbook(a.input,read_only=True,data_only=True)
        report.update(sha256=sha,byte_count=a.input.stat().st_size,sheets=[{"name":s.title,"reported_max_row":s.max_row,"reported_max_column":s.max_column,"preview_first_8_rows":[[str(v)[:160] if v is not None else None for v in row] for row in s.iter_rows(min_row=1,max_row=8,max_col=min(s.max_column or 25,25),values_only=True)]} for s in w])
        report["status"]="schema_acquired_not_normalized"
        if any(v is not None for v in (a.sheet,a.header_row,a.species_col,a.mode_col)):
            if not(a.sheet and a.header_row and a.species_col and a.mode_col): raise ValueError("all schema arguments required")
            if min([a.header_row,a.species_col,*a.mode_col])<1: raise ValueError("column/row indices must be positive")
            with MAP.open() as h: mapping={int(r["mode"]):r for r in csv.DictReader(h)}
            assert set(mapping)==set(range(44,66))
            species={}; malformed=0; blank=0; duplicate=0
            for row in w[a.sheet].iter_rows(min_row=a.header_row+1,values_only=True):
                value=row[a.species_col-1] if len(row)>=a.species_col else None
                name=" ".join(str(value).split()) if value is not None else ""
                if not re.fullmatch(r"[A-Z][a-z]+ [a-z][a-z-]+",name):
                    blank+=1;continue
                parsed=[]
                for col in a.mode_col:
                    val=row[col-1] if len(row)>=col else None
                    if val is None or not str(val).strip(): continue
                    codes=parse_codes(val)
                    if codes is None: malformed+=1
                    else: parsed.extend(codes)
                if name in species: duplicate+=1
                species.setdefault(name,set()).update(parsed)
            totals=Counter();classes=Counter()
            for codes in species.values():
                state,labels=classify(codes,mapping); totals[state]+=1; classes.update(labels)
            report.update(status="explicit_schema_descriptive_only",n_binomials=len(species),duplicates=duplicate,non_binomial_rows=blank,unparsed_nonempty_mode_cells=malformed,trait_status_counts=dict(totals),nonexclusive_foam_exposure_counts=dict(classes),warning="No-foam-mode-reported is not verified non-foam. Multiple modes retained; exposure is potential, not measured. No species-name harmonization or order check yet.")
        w.close()
    except Exception as e:
        report.update(status="failed",error=type(e).__name__+": "+str(e))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(report["status"])
    if report["status"]=="failed": raise SystemExit(2)
if __name__=="__main__": main()
