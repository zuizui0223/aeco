#!/usr/bin/env python3
"""Camera-space robustness of six previously selected foam photos, not animal perception."""
import argparse, hashlib, io, json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata

W=np.array([.2126,.7152,.0722])

def mask(im, polys):
    m=Image.new('1',im.size,0);d=ImageDraw.Draw(m)
    for p in polys:d.polygon([tuple(v) for v in p],fill=1)
    return np.asarray(m,dtype=bool)

def lin(p):return np.where(p<=.04045,p/12.92,((p+.055)/1.055)**2.4)
def c(a,b):return (a-b)/(a+b) if a+b>0 else None

def auc(x,y):
    n,m=len(x),len(y)
    r=rankdata(np.r_[x,y],method='average')
    return float((r[:n].sum()-n*(n+1)/2)/(n*m))

def compare(p,q):
    a=p@W;b=q@W
    am,bm=float(np.median(a)),float(np.median(b))
    pa,pb=p.mean(0),q.mean(0)
    # Channel-wise dominance of linearized RGB means implies the same sign for
    # any nonnegative RGB weights, NOT for unknown animal spectral sensitivities.
    out={'target_pixels':len(p),'comparison_pixels':len(q),'contrast_medians':c(am,bm),
         'rank_AUC':auc(a,b),'all_channels_mean_higher':bool(np.all(pa>pb)),
         'mean_RGB_contrasts':[c(x,y) for x,y in zip(pa,pb)],
         'comparison_median_Y':bm,'comparison_q90_Y':float(np.quantile(b,.9)),
         'target_q10_Y':float(np.quantile(a,.1)),
         'target_median_above_comparison_q90':bool(am>np.quantile(b,.9)),
         'target_q10_above_comparison_q90':bool(np.quantile(a,.1)>np.quantile(b,.9)),
         'target_clipped_fraction':float((p>=lin(np.array([250/255]))[0]).any(1).mean())}
    # Synthetic whole-image linear gain and clipping; not a real camera model.
    out['gain_sensitivity']={str(g):c(float(np.median(np.minimum(1,g*p)@W)),float(np.median(np.minimum(1,g*q)@W))) for g in [.25,.5,1,2,4]}
    # Different arbitrary RGB response curves to test a broad camera-space sign sensitivity.
    out['channel_gamma_sensitivity']={str(g):c(float(np.median((p**g)@W)),float(np.median((q**g)@W))) for g in [.6,1,1.6]}
    return out

def main(zippath,record,out):
    r=json.loads(Path(record).read_text()); rows=[]
    assert hashlib.sha256(Path(zippath).read_bytes()).hexdigest()==r['source_zip_sha256']
    with ZipFile(zippath) as z:
        for v in r['rows']:
            raw=z.read(f'candidate_{v["id"]:02d}.png'); assert hashlib.sha256(raw).hexdigest()==v['image_sha256']
            im=Image.open(io.BytesIO(raw)).convert('RGB');p=lin(np.asarray(im)/255.)
            fo=mask(im,v['polygons']['foam']); bg=mask(im,v['polygons']['background'])
            assert not np.any(fo&bg)
            d=distance_transform_edt(~fo)
            # Radius is based on annotated interior area, not actual size. Ring pixels
            # are unclassified neighborhood (may include actual foam, frog, water etc.).
            rad=np.sqrt(fo.sum()/np.pi)
            patches={'manual_background':bg,'ring_near':(d>=.35*rad)&(d<=1.0*rad),'ring_far':(d>1.0*rad)&(d<=2.0*rad),'whole_nonROI':~fo}
            rr={'id':v['id'],'interior_equivalent_radius_px':float(rad),'comparisons':{k:compare(p[fo],p[m]) for k,m in patches.items() if m.sum()>=100}}
            assert abs(rr['comparisons']['manual_background']['contrast_medians']-v['contrast'])<1e-12
            rows.append(rr)
    groups={}
    for k in ['manual_background','ring_near','ring_far','whole_nonROI']:
        g=[r['comparisons'][k] for r in rows if k in r['comparisons']]
        groups[k]={'n_images':len(g),'positive_median_contrast':sum(x['contrast_medians']>0 for x in g),
          'median_contrast':float(np.median([x['contrast_medians'] for x in g])),
          'median_rank_AUC':float(np.median([x['rank_AUC'] for x in g])),
          'AUC_above_half':sum(x['rank_AUC']>.5 for x in g),
          'all_RGB_channel_means_higher':sum(x['all_channels_mean_higher'] for x in g),
          'target_median_above_bg_q90':sum(x['target_median_above_comparison_q90'] for x in g),
          'target_q10_above_bg_q90':sum(x['target_q10_above_comparison_q90'] for x in g),
          'all_gain_scenarios_positive':sum(all(v>0 for v in x['gain_sensitivity'].values()) for x in g),
          'all_gamma_scenarios_positive':sum(all(v>0 for v in x['channel_gamma_sensitivity'].values()) for x in g)}
    report={'status':'local_camera_space_robustness_not_independent_replication','zip_sha256':r['source_zip_sha256'],'groups':groups,'rows':rows,'limitations':['Same six nonrandom photographs, same hand-drawn interior ROIs; no independent replicate.','Rings and full non-ROI region are unclassified image neighborhoods and may contain unmasked foam, adults, eggs, artificial substrate, or other objects. Not certified backgrounds.','AUC is a descriptive pixel ranking metric; pixels are spatially correlated; no pixel-level inference or animal detection probability.','Synthetic uniform gain/clipping and channel-gamma transformations cannot reconstruct camera processing, illumination differences, flash or reflectance.','No calibrated spectrum, UV, physical scale, visual acuity, receiver spectral sensitivities or behavior. No shape estimate from partial interior ROIs.']}
    Path(out).write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(groups,indent=2));print([(r['id'],{k:round(v['contrast_medians'],3) for k,v in r['comparisons'].items()}) for r in rows])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('zip');p.add_argument('record');p.add_argument('out');a=p.parse_args();main(a.zip,a.record,a.out)
