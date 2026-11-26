#!/usr/bin/env python3
"""Bounded licensed Commons candidate acquisition, not a census or visual-response assay."""
import hashlib,io,json,re,time,urllib.request,urllib.parse,html
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
OUT=Path("results/v2.3_visual");OUT.mkdir(parents=True,exist_ok=True)
QUERIES=['"foam nest" frog','"foam nest" Polypedates','"foam nest" Rhacophorus','"foam nest" Zhangixalus','"foam nest" Leptodactylus','"foam nest" Engystomops']
UA="AECO-research/2.3 (https://github.com/zuizui0223/aeco; public scientific image audit)"
def read(url,cap):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=18) as r:
        b=r.read(cap+1)
    if len(b)>cap:raise ValueError("cap exceeded")
    return b
def plain(v):
    return html.unescape(re.sub(r"<[^>]+>"," ",str(v or ""))).strip()
def main():
    candidates={};errs=[]
    for q in QUERIES:
        params={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":6,"gsrlimit":12,"prop":"imageinfo","iiprop":"url|size|sha1|mime|extmetadata","iiurlwidth":640,"format":"json","formatversion":2}
        try:
            d=json.loads(read("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params),4_000_000))
            if "error" in d:raise ValueError(str(d["error"]))
            for p in d.get("query",{}).get("pages",[]):
                infos=p.get("imageinfo",[])
                if not infos:continue
                i=infos[0];m=i.get("extmetadata",{})
                key=i.get("sha1") or p["title"]
                if key not in candidates:
                    candidates[key]={"title":p["title"],"source_page":i.get("descriptionurl"),"thumburl":i.get("thumburl"),"originalurl":i.get("url"),"mime":i.get("mime"),"source_sha1":i.get("sha1"),"license":plain(m.get("LicenseShortName",{}).get("value")),"license_url":plain(m.get("LicenseUrl",{}).get("value")),"artist":plain(m.get("Artist",{}).get("value")),"description":plain(m.get("ImageDescription",{}).get("value"))[:600],"queries":[]}
                candidates[key]["queries"].append(q)
        except Exception as e:errs.append({"query":q,"error":repr(e)})
        time.sleep(.5)
    # Deterministic order; maximum 24 licensed JPEG/PNG candidate thumbnails.
    valid=[]
    for k,c in sorted(candidates.items(),key=lambda kv:hashlib.sha256(kv[0].encode()).hexdigest()):
        lic=c["license"].lower()
        if c["mime"] not in {"image/jpeg","image/png"} or not c["thumburl"] or not c["artist"] or not c["source_page"]:continue
        if not (lic.startswith("cc by ") or lic.startswith("cc by-sa ") or lic in {"cc0","public domain"}):continue
        if lic not in {"cc0","public domain"} and not c["license_url"]:continue
        valid.append(c)
    rows=[]
    for i,c in enumerate(valid[:24],1):
        r={k:v for k,v in c.items() if k not in {"thumburl","originalurl"}}
        r["candidate_id"]=i
        try:
            b=read(c["thumburl"],3_000_000)
            img=ImageOps.exif_transpose(Image.open(io.BytesIO(b))).convert("RGB")
            img.thumbnail((640,640))
            dest=OUT/f"candidate_{i:02d}.png";img.save(dest)
            r.update(status="downloaded_candidate_unreviewed",width=img.width,height=img.height,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),file=dest.name)
        except Exception as e:r.update(status="failed",error=repr(e))
        rows.append(r);time.sleep(.5)
    downloaded=[r for r in rows if r["status"]=="downloaded_candidate_unreviewed"]
    if downloaded:
        canvas=Image.new("RGB",(800,220*((len(downloaded)+3)//4)),"white")
        draw=ImageDraw.Draw(canvas)
        for j,r in enumerate(downloaded):
            im=Image.open(OUT/r["file"]);im.thumbnail((192,192));x=(j%4)*200;y=(j//4)*220
            canvas.paste(im,(x,y));draw.text((x+2,y+194),f'{r["candidate_id"]:02d} {r["width"]}x{r["height"]}',fill="black")
        canvas.save(OUT/"contact_sheet.png")
    report={"status":"candidate_acquisition_not_nest_identification","queries":QUERIES,"query_errors":errs,"unique_candidates":len(candidates),"eligible_license_candidates":len(valid),"downloaded":len(downloaded),"rows":rows,"limits":"Search hits can be adults, tadpoles, nonfoam or duplicates of the same nest. Photographer-selected images, automatic exposure, white balance and unknown scale. Do not infer UV, reflectance or behavior; manual review before ROI measurement."}
    (OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("VISUAL_SOURCE_RESULT "+json.dumps({k:v for k,v in report.items() if k!="rows"},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
