#!/usr/bin/env python3
"""Replay manually annotated within-image RGB contrast from the frozen Commons artifact."""
import argparse,hashlib,io,json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from PIL import Image,ImageDraw
RECORD=Path("results/foam_visual_roi_v2.3_verified.json")
def calc(image,polygons):
    mask=Image.new("1",image.size,0);draw=ImageDraw.Draw(mask)
    for poly in polygons:draw.polygon([tuple(v) for v in poly],fill=1)
    pixels=np.asarray(image.convert("RGB"))[np.asarray(mask,dtype=bool)]/255.
    linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4)
    return float(np.median(linear@np.array([.2126,.7152,.0722])))
def main():
    p=argparse.ArgumentParser();p.add_argument("zip",type=Path);a=p.parse_args()
    r=json.loads(RECORD.read_text())
    assert hashlib.sha256(a.zip.read_bytes()).hexdigest()==r["source_zip_sha256"]
    cs=[]
    with ZipFile(a.zip) as z:
        for row in r["rows"]:
            b=z.read(f'candidate_{row["id"]:02d}.png')
            assert hashlib.sha256(b).hexdigest()==row["image_sha256"]
            im=Image.open(io.BytesIO(b));poly=row["polygons"]
            f=calc(im,poly["foam"]);bg=calc(im,poly["background"]);c=(f-bg)/(f+bg)
            assert abs(f-row["Y_foam"])<1e-12 and abs(bg-row["Y_background"])<1e-12 and abs(c-row["contrast"])<1e-12
            if "alternate" in poly:
                bg2=calc(im,poly["alternate"])
                assert abs((f-bg2)/(f+bg2)-row["alternate_contrast"])<1e-12
            cs.append(c);print(row["id"],f,bg,c,f/bg)
    assert abs(float(np.median(cs))-r["median_contrast"])<1e-12
    print("Verified image-value contrasts only; not spectral reflectance or animal visual response.")
if __name__=="__main__":main()
