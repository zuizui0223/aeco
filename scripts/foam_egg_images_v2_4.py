#!/usr/bin/env python3
"""Bounded iNaturalist egg-image retrieval. Selection independent of image brightness.
Images are candidates, not confirmed foam/egg masses. Only permissively licensed photos.
No coordinates, dates, observer identifiers (apart from required photo credit) exported."""
import argparse,hashlib,io,json,time,urllib.parse,urllib.request
from pathlib import Path
from collections import Counter
from PIL import Image,ImageOps,ImageDraw
OUT=Path("results/v2.4_candidates");OUT.mkdir(parents=True,exist_ok=True)
SPECIES={
 "Rhacophorus malabaricus":"E","Polypedates leucomystax":"E","Polypedates megacephalus":"E","Chiromantis xerampelina":"E",
 "Engystomops pustulosus":"E","Physalaemus cuvieri":"E","Leptodactylus latrans":"E",
 "Leptodactylus fuscus":"S","Leptodactylus mystacinus":"S","Adenomera marmorata":"S",
 "Agalychnis callidryas":"N","Boana faber":"N","Dendropsophus minutus":"N","Lithobates catesbeianus":"N"}
LICENSES={"cc0","cc-by","cc-by-sa"}
UA="AECO-research/2.4 (https://github.com/zuizui0223/aeco; licensed egg image research)"
def fetch(url,cap):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=25) as r:b=r.read(cap+1)
    if len(b)>cap:raise ValueError("cap exceeded")
    return b
def api(path,params):
    time.sleep(1.05)
    return json.loads(fetch("https://api.inaturalist.org/v1/"+path+"?"+urllib.parse.urlencode(params),8_000_000))
def main():
    audit=[];rows=[];seen=set()
    for name,cls in SPECIES.items():
        a={"name":name,"source_class":cls,"status":"unresolved","annotation":"Life Stage=Egg"}
        try:
            tr=api("taxa",{"q":name,"rank":"species","is_active":"true","per_page":30})
            matches=[r for r in tr["results"] if r.get("name")==name and r.get("rank")=="species" and r.get("is_active")]
            if len(matches)!=1:raise ValueError("no unique active exact species")
            tax=int(matches[0]["id"]);a["taxon_id"]=tax
            d=api("observations",{"taxon_id":tax,"term_id":1,"term_value_id":7,"photos":"true","quality_grade":"research","per_page":40,"order_by":"id","order":"desc"})
            a["query_total"]=d["total_results"];a["records_returned"]=len(d["results"])
            obs=[r for r in d["results"] if r.get("taxon",{}).get("id")==tax and any(int(t.get("controlled_attribute_id",-1))==1 and int(t.get("controlled_value_id",-1))==7 for t in r.get("annotations",[]))]
            a["exact_taxon_egg_annotation_records"]=len(obs)
            pool=[]
            for r in obs:
                ps=[p for p in r.get("photos",[]) if str(p.get("license_code")).lower() in LICENSES and p.get("url") and p.get("attribution")]
                if ps:
                    ps=sorted(ps,key=lambda p:int(p["id"]));pool.append((r,ps[0]))
            a["licensed_observations"]=len(pool)
            # Fixed hash order within the bounded latest-results page, not population sampling.
            pool.sort(key=lambda z:hashlib.sha256(("AECO-v2.4:"+str(z[0]["id"])).encode()).hexdigest())
            for r,p in pool[:4]:
                photo_id=int(p["id"])
                if photo_id in seen:continue
                seen.add(photo_id); idx=len(rows)+1
                row={"candidate_id":idx,"species":name,"source_class":cls,"taxon_id":tax,"observation_id":int(r["id"]),"photo_id":photo_id,"source_url":"https://www.inaturalist.org/observations/"+str(r["id"]),"credit":p["attribution"],"license":p["license_code"]}
                try:
                    u=p["url"]
                    # Use documented photo URL size token only, not arbitrary URL manipulation.
                    import re
                    u=re.sub(r"/(square|thumb|small|medium|large)\.(jpg|jpeg|png)(?=\?|$)",r"/medium.\2",u,flags=re.I)
                    time.sleep(1.05)
                    b=fetch(u,3_000_000)
                    im=ImageOps.exif_transpose(Image.open(io.BytesIO(b))).convert("RGB");im.thumbnail((640,640))
                    path=OUT/f"egg_{idx:02d}.png";im.save(path)
                    row.update(status="downloaded_unreviewed",file=path.name,width=im.width,height=im.height,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                except Exception as e:row.update(status="download_failed",error=repr(e))
                rows.append(row)
            a["status"]="queried"
        except Exception as e:a.update(status="failed",error=repr(e))
        audit.append(a);print("EGG_SOURCE_PROGRESS",name,a["status"],a.get("query_total"),a.get("licensed_observations"),flush=True)
    good=[r for r in rows if r["status"]=="downloaded_unreviewed"]
    for off in range(0,len(good),20):
        g=good[off:off+20]
        canvas=Image.new("RGB",(1000,245*((len(g)+3)//4)),"white");dr=ImageDraw.Draw(canvas)
        for i,r in enumerate(g):
            im=Image.open(OUT/r["file"]);im.thumbnail((238,210));x=(i%4)*250;y=(i//4)*245
            canvas.paste(im,(x,y));dr.text((x+3,y+213),f'{r["candidate_id"]:02d} {r["source_class"]} {r["species"]}',fill="black")
        canvas.save(OUT/f"review_{off//20+1}.png")
    report={"status":"licensed_egg_annotation_candidates_not_nest_verified","species_queries":audit,"rows":rows,"downloaded":len(good),"by_source_class":dict(Counter(r["source_class"] for r in good)),"limitations":"Annotation and source reproductive mode do not establish visible foam. One licensed photo per observation, at most four observations per species within latest 40 research-grade results, hash ordering unrelated to contrast. Not random globally; no true absence from failed or empty query. N = no documented froth or bubble in trait source, not definitive biological absence."}
    (OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("EGG_SOURCE_RESULT "+json.dumps({k:v for k,v in report.items() if k!="rows"},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
