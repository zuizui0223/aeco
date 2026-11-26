#!/usr/bin/env python3
"""Verify v2.4 new image comparison against frozen polygons and exact source archive."""
import argparse,hashlib,io,json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata
W=np.array([.2126,.7152,.0722])
def sha(b):return hashlib.sha256(b).hexdigest()
def mask(im,polys):
 m=Image.new("1",im.size,0);d=ImageDraw.Draw(m)
 for poly in polys:d.polygon([tuple(v) for v in poly],fill=1)
 return np.asarray(m,dtype=bool)
def metric(y,f,b):
 a=y[f];q=y[b];n=len(a);m=len(q);assert min(n,m)>=500
 A=float(np.median(a));B=float(np.median(q));r=rankdata(np.r_[a,q],method="average")
 return {"contrast":(A-B)/(A+B),"rank_AUC":float((r[:n].sum()-n*(n+1)/2)/(n*m)),"target_pixels":n,"background_pixels":m,"target_Y":A,"background_Y":B}
def main():
 p=argparse.ArgumentParser();p.add_argument("zip");p.add_argument("--record",default="results/foam_egg_comparison_v2.4_verified.json");p.add_argument("--out",default="egg_comparison_replay.json");a=p.parse_args()
 r=json.loads(Path(a.record).read_text());raw=Path(a.zip).read_bytes();assert sha(raw)==r["zip_sha256"]
 rows=[]
 with ZipFile(io.BytesIO(raw)) as z:
  meta=json.loads(z.read("manifest.json"));assert len(meta["rows"])==20
  by={x["candidate_id"]:x for x in meta["rows"]}
  for rec in r["rows"]:
   i=rec["id"];m=by[i];b=z.read(m["file"]);assert sha(b)==m["sha256"]==rec["sha256"]
   assert m["species"]==rec["species"] and m["source_class"]==rec["source_class"]
   im=Image.open(io.BytesIO(b)).convert("RGB")
   f=mask(im,rec["polygons"]["target"]);g=mask(im,rec["polygons"]["background"]);assert not np.any(f&g)
   p=np.asarray(im)/255.;lin=np.where(p<=.04045,p/12.92,((p+.055)/1.055)**2.4);y=lin@W
   d=distance_transform_edt(~f);rad=np.sqrt(f.sum()/np.pi);near=(d>=.35*rad)&(d<=rad)
   row={"id":i,"species":m["species"],"source_class":m["source_class"],"photo_id":m["photo_id"],"source_url":m["source_url"],"credit":m["credit"],"license":m["license"]}
   for k,bg in {"manual":g,"near":near,"whole":~f}.items():
    row[k]=metric(y,f,bg);assert abs(row[k]["contrast"]-rec["rounded_contrast"][k])<1e-8
   rows.append(row)
 for k in ("manual","near","whole"):
  for group in ("E","N"):
   q=[x for x in rows if x["source_class"]==group];sp=sorted({x["species"] for x in q})
   means=[np.mean([x[k]["contrast"] for x in q if x["species"]==s]) for s in sp]
   assert abs(np.mean(means)-r["comparison"][k][group]["species_balanced"])<1e-8
   print(k,group,len(q),len(sp),float(np.mean(means)))
 Path(a.out).write_text(json.dumps(rows,indent=2,ensure_ascii=False)+"\n")
if __name__=="__main__":main()
