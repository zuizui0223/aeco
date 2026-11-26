#!/usr/bin/env python3
"""Spatial blur sensitivity of the fixed V2.5 photo sample; no calibrated distance or receiver model."""
import argparse, hashlib, io, json
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, distance_transform_edt
from scipy.stats import rankdata
import pandas as pd

ZIPS = {'v2.4':'e5f67ea337a7287cc968bf3873ade4ff605d941eb67baf540655060156c2ccda', 'v2.5':'1ab5c727de1ad6e88e2e3cbb68d8de3e49d27effefac22c8cb326b6ff15c2d33'}
W = np.array([.2126,.7152,.0722])
SCALES = [0., .125, .25, .5, 1., 2.]
CONTEXTS = ['manual','near','whole']
EXCLUDE = {('v2.5',9),('v2.5',14),('v2.5',15),('v2.4',12),('v2.4',19)}

def sha(b): return hashlib.sha256(b).hexdigest()
def mask(im, polygons):
    m=Image.new('1',im.size,0); d=ImageDraw.Draw(m)
    for p in polygons: d.polygon([tuple(v) for v in p], fill=1)
    return np.asarray(m,dtype=bool)
def metrics(p,y,target,bg):
    a,b=y[target],y[bg]; n,m=len(a),len(b)
    A,B=float(np.median(a)),float(np.median(b))
    rank=rankdata(np.r_[a,b],method='average')
    t=p[target]; t=t[t.sum(1)>1e-5]; t=t/t.sum(1)[:,None]
    chroma=float(np.median(t.max(1)-t.min(1)))
    z={'C':(A-B)/(A+B), 'chroma':chroma, 'AUC':float((rank[:n].sum()-n*(n+1)/2)/(n*m)), 'IQR':float(np.quantile(a,.75)-np.quantile(a,.25))}
    return z

def load(record,zpaths):
    rr=json.loads(Path(record).read_text()); assert len(rr['rows'])==36
    assert len({x['photo_id'] for x in rr['rows']})==36
    for source,zpath in zpaths.items():
        b=Path(zpath).read_bytes(); assert sha(b)==ZIPS[source]
        with ZipFile(io.BytesIO(b)) as z:
            m=json.loads(z.read('manifest.json')); by={x['candidate_id']:x for x in m['rows']}
            for r in rr['rows']:
                if r['sample']!=source:continue
                q=by[r['id']]; raw=z.read(q['file']); assert sha(raw)==q['sha256']==r['sha256']
                assert r['photo_id']==q['photo_id'] and r['species']==q['species']
                g={'E':'foam','N':'nonfoam_eggs'}.get(q['source_class'],q['source_class']); assert g==r['group']
                im=Image.open(io.BytesIO(raw)).convert('RGB'); v=np.asarray(im,dtype=np.float64)/255
                lin=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
                t=mask(im,r['polygons']['target']); bg=mask(im,r['polygons']['background']); assert not np.any(t&bg)
                rad=np.sqrt(t.sum()/np.pi); d=distance_transform_edt(~t)
                contexts={'manual':bg,'near':(d>=.35*rad)&(d<=rad),'whole':~t}
                assert all(x.sum()>=300 for x in [t,*contexts.values()])
                yield r,lin,t,contexts,rad

def summarize(df):
    cols=['C','chroma','AUC','IQR']; species=df.groupby(['group','species','scale','context'])[cols].mean().reset_index()
    result=[]
    for (g,sc,ct),f in species.groupby(['group','scale','context']):
        n=len(df[(df.group==g)&(df.scale==sc)&(df.context==ct)])
        result.append(dict(group=g,scale=float(sc),context=ct,n_images=n,n_species=len(f),**{k:float(f[k].mean()) for k in cols}))
    return result,species

def compare_centroids(species):
    """Distances in two unweighted camera-space metrics on common scales; descriptive."""
    out=[]
    for (scale,context),f in species.groupby(['scale','context']):
        cs=f.groupby('group')[['C','chroma']].mean(); foam=cs.loc['foam'].to_numpy()
        for g,row in cs.iterrows():
            if g=='foam':continue
            out.append(dict(scale=float(scale),context=context,reference=g,distance=float(np.linalg.norm(foam-row.to_numpy())),delta_C=float(foam[0]-row.C),delta_chroma=float(foam[1]-row.chroma)))
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('record');p.add_argument('old_zip');p.add_argument('new_zip');p.add_argument('--out',required=True);a=p.parse_args()
    rows=[];checks=[]
    for r,lin,t,contexts,rad in load(a.record,{'v2.4':a.old_zip,'v2.5':a.new_zip}):
        diam=2*rad
        for sc in SCALES:
            sigma=sc*diam/2.354820045
            # Blur in linear RGB, not gamma-encoded RGB. Reflect boundary is synthetic.
            blur=gaussian_filter(lin,sigma=(sigma,sigma,0),mode='reflect',truncate=3.) if sc else lin
            y=blur@W
            for name,bg in contexts.items():
                z=metrics(blur,y,t,bg)
                if sc==0:
                    assert abs(z['C']-r[name]['C'])<1e-10 and abs(z['chroma']-r[name]['chroma_spread'])<1e-10 and abs(z['AUC']-r[name]['rank_AUC'])<1e-10
                rows.append(dict(sample=r['sample'],id=r['id'],photo_id=r['photo_id'],group=r['group'],species=r['species'],scale=sc,context=name,diameter_px=diam,sigma_px=sigma,**z))
        checks.append({'sample':r['sample'],'id':r['id'],'photo_id':r['photo_id'],'image_sha256':r['sha256'],'roi_equivalent_diameter_px':diam})
        print('completed',r['sample'],r['id'],flush=True)
    df=pd.DataFrame(rows);assert len(df)==36*len(SCALES)*3
    groups,sp=summarize(df)
    sub=df[[ (s,i) not in EXCLUDE for s,i in zip(df['sample'],df.id) ]]
    sens,sps=summarize(sub)
    # Restrict reference groups to white flower and pale fungus, which both have >=2 species.
    report={'status':'executed_multiscale_camera_space_diagnostic','input_record_sha256':sha(Path(a.record).read_bytes()),'source_zip_sha256':ZIPS,'n_photos':36,'n_species':int(df.species.nunique()),'scales_FWHM_over_equivalent_ROI_diameter':SCALES,'zero_scale_reproduced':True,'n_zero_scale_metrics_verified':36*3*3,'checks':checks,'summary':groups,'species_summary':sp.to_dict('records'),'centroid_distances':compare_centroids(sp),'context_exclusion_sensitivity':sens,'sensitivity_centroid_distances':compare_centroids(sps),'limitations':['Same nonrandom 36 photos/12 species; no new independent images.','Gaussian FWHM divided by partial interior ROI equivalent diameter, not physical size, distance, visual angle or measured animal acuity. Larger scales mix target with neighbors and depend on image crop/boundary; reflected edge padding synthetic.','Fixed target/context masks intentionally track same locations under blur, not segmentation or detection by animals. Near/whole context unclassified; may include actual targets.','C and RGB spread are camera-space indices only; arbitrary equal-weight distance, no calibrated reflectance, UV, color vision, equivalence test, behavior, reproduction or fitness.','Photographer selection, source taxon, habitats, camera processing, lighting and scale remain confounded.']}
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/'photo_scale_metrics.csv',index=False)
    (out/'summary.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(pd.DataFrame(groups).query("context=='manual'").pivot(index='scale',columns='group',values='C').round(4))
    print(pd.DataFrame(groups).query("context=='manual'").pivot(index='scale',columns='group',values='chroma').round(4))
    print(pd.DataFrame(report['centroid_distances']).query("context=='manual'").pivot(index='scale',columns='reference',values='distance').round(4))
if __name__=='__main__':main()
