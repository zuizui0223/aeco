#!/usr/bin/env python3
"""Replay camera-space comparisons; never infer reflectance, UV or animal behavior."""
import argparse,json,hashlib,io
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata
W=np.array([.2126,.7152,.0722])
def sha(b):return hashlib.sha256(b).hexdigest()
def mask(im,poly):
    m=Image.new('1',im.size);d=ImageDraw.Draw(m)
    for pts in poly:d.polygon([tuple(p) for p in pts],fill=1)
    return np.asarray(m,dtype=bool)
def stats(p,q):
    a=p@W;b=q@W;n=len(a);m=len(b);assert min(n,m)>=300
    A,B=float(np.median(a)),float(np.median(b))
    rank=rankdata(np.r_[a,b],method='average')
    u=p[p.sum(1)>1e-5];v=q[q.sum(1)>1e-5]
    ch=u/u.sum(1)[:,None];cb=v/v.sum(1)[:,None]
    ac=np.median(ch,axis=0);bc=np.median(cb,axis=0);ac/=ac.sum();bc/=bc.sum()
    sat=np.max(ch,axis=1)-np.min(ch,axis=1)
    return dict(target_Y=A,background_Y=B,C=(A-B)/(A+B),rank_AUC=float((rank[:n].sum()-n*(n+1)/2)/(n*m)),rgb_chromaticity_target=ac.tolist(),rgb_chromaticity_background=bc.tolist(),chroma_spread=float(np.median(sat)),chromaticity_distance=float(np.linalg.norm(ac-bc)),target_luminance_IQR=float(np.quantile(a,.75)-np.quantile(a,.25)),target_pixels=n,comparison_pixels=m)
def process(zpath,rec,old):
    r=json.loads(Path(rec).read_text());b=Path(zpath).read_bytes()
    assert sha(b)==(r.get('source_zip_sha256') or r['zip_sha256'])
    res=[]
    with ZipFile(io.BytesIO(b)) as z:
        met=json.loads(z.read('manifest.json'));by={x['candidate_id']:x for x in met['rows']}
        for row in r['rows']:
            i=row['id'];m=by[i];img=z.read(m['file']);assert sha(img)==m['sha256']==row['sha256']
            im=Image.open(io.BytesIO(img)).convert('RGB');p=np.asarray(im)/255.;lin=np.where(p<=.04045,p/12.92,((p+.055)/1.055)**2.4)
            fo=mask(im,row['polygons']['target']);bg=mask(im,row['polygons']['background']);assert not np.any(fo&bg)
            d=distance_transform_edt(~fo);rad=np.sqrt(fo.sum()/np.pi);near=(d>=.35*rad)&(d<=rad)
            group={'E':'foam','N':'nonfoam_eggs'}[m['source_class']] if old else m['source_class']
            v={'id':i,'sample':'v2.4' if old else 'v2.5','group':group,'species':m['species'],'photo_id':m['photo_id'],'sha256':m['sha256'],'source_url':m['source_url'],'credit':m['credit'],'license':m['license'],'polygons':row['polygons'],'context':row.get('context','')}
            for k,g in [('manual',bg),('near',near),('whole',~fo)]:v[k]=stats(lin[fo],lin[g])
            if old:
                expected=row.get('rounded_contrast')
                for k in ('manual','near','whole'):assert abs(v[k]['C']-(expected[k] if expected else row[k]['contrast']))<1e-8
            else:
                for k in ('manual','near','whole'):assert abs(v[k]['C']-row['rounded_expected'][k])<1e-8
                assert abs(v['manual']['chroma_spread']-row['rounded_expected']['chroma'])<1e-8
            res.append(v)
    return res
def summary(rows):
    o={}
    for g in sorted({x['group'] for x in rows}):
        q=[x for x in rows if x['group']==g];sp=sorted({x['species'] for x in q});o[g]={'n':len(q),'species':len(sp),'by_context':{}}
        for key in ('manual','near','whole'):
            d={s:{k:float(np.mean([x[key][k] for x in q if x['species']==s])) for k in ('C','chroma_spread','chromaticity_distance','rank_AUC')} for s in sp}
            o[g]['by_context'][key]={'median_C':float(np.median([x[key]['C'] for x in q])),'species_balanced':{k:float(np.mean([v[k] for v in d.values()])) for k in next(iter(d.values()))},'by_species':d,'positive_C':sum(x[key]['C']>0 for x in q)}
    return o
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('old_zip');p.add_argument('new_zip');p.add_argument('--old-roi',default='results/foam_egg_comparison_v2.4_verified.json');p.add_argument('--new-roi',default='data/frozen/foam_cross_structure_v2.5_rois.json');p.add_argument('--out',default='foam_cross_structure_v2.5_replay.json');a=p.parse_args()
    rows=process(a.old_zip,a.old_roi,True)+process(a.new_zip,a.new_roi,False)
    assert len(rows)==36 and len({x['photo_id'] for x in rows})==36
    report={'status':'cross_structure_camera_space_descriptive','rows':rows,'summary':summary(rows),'context_sensitivity':summary([x for x in rows if not ((x['sample']=='v2.5' and x['id'] in [9,14,15]) or (x['sample']=='v2.4' and x['id'] in [12,19]))])}
    Path(a.out).write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    for g,r in report['summary'].items():print(g,r['n'],r['species'],r['by_context']['manual']['species_balanced'])
