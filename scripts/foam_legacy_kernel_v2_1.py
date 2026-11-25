#!/usr/bin/env python3
"""Persistence-window sensitivity on frozen V1.8 observations; NOT actual foam availability.
Usage: python foam_legacy_kernel_v2_1.py path/to/v18.zip --out output.json
The input ZIP is the verified Actions artifact, not a new independent sample.
"""
import argparse, hashlib, json, zipfile
from collections import Counter
from pathlib import Path
import numpy as np

ZIP_SHA='a94a670b44b0eb6dc99a4b2998dc099d619456fa0f7e21b54a0f77851345ecf7'
DAYS=np.array([31,28,31,30,31,30,31,31,30,31,30,31])
START=np.r_[0,np.cumsum(DAYS)]
# Ages are elapsed days since formation, not calendar months. Upper endpoint excluded.
WINDOWS={'instant':(0,1),'occupied_7d':(0,7),'occupied_10d':(0,10),
         'total_21d':(0,21),'total_31d':(0,31),
         'residue_14d_after_7d':(7,21),'residue_21d_after_10d':(10,31)}

def normalize(a):
    a=np.asarray(a,dtype=float)
    assert a.shape==(12,) and np.all(a>=0) and a.sum()>0
    return a/a.sum()

def daily_profile(p,placement):
    p=normalize(p);d=np.zeros(365)
    for m in range(12):
        i,j=START[m:m+2]
        if placement=='uniform':d[i:j]=p[m]/DAYS[m]
        elif placement=='first_day':d[i]=p[m]
        elif placement=='last_day':d[j-1]=p[m]
        else:raise ValueError(placement)
    assert np.isclose(d.sum(),1)
    return d

def transform(p,window,placement,direction=1):
    a,b=window;assert 0<=a<b<=365 and direction in (-1,1)
    daily=daily_profile(p,placement)
    # Convolution of hypothetical supply dates with a constant accessibility window.
    # Normalize separately: timing only, no modeled total amount of resource.
    y=np.mean([np.roll(daily,direction*k) for k in range(a,b)],axis=0)
    z=np.array([y[i:j].sum() for i,j in zip(START[:-1],START[1:])])
    assert np.isclose(z.sum(),1) and np.all(z>=0)
    return z

def overlap(a,b):return 1-float(np.abs(a-b).sum())/2

def contrast(e,s,p,b):return overlap(e,p)-overlap(e,b)-overlap(s,p)+overlap(s,b)

def block_summary(rows,key):
    blocks=sorted({r['block'] for r in rows})
    a=np.array([np.mean([r[key] for r in rows if r['block']==b]) for b in blocks]);mu=float(a.mean())
    return {'n':len(rows),'blocks':len(blocks),'block_balanced_mean':mu,'cell_mean':float(np.mean([r[key] for r in rows])),
        'positive_blocks':int((a>1e-12).sum()),'negative_blocks':int((a< -1e-12).sum()),
        'block_means':{k:float(v) for k,v in zip(blocks,a)},
        'leave_one_block_out_range':[float((a.sum()-a).min()/(len(a)-1)),float((a.sum()-a).max()/(len(a)-1))] if len(a)>1 else None}

def main(path,out):
    raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==ZIP_SHA,'Input digest mismatch'
    with zipfile.ZipFile(path) as z:
        rows=[json.loads(x) for i in range(3) for x in z.read(f'shard_{i}.jsonl').splitlines() if x]
        prev=json.loads(z.read('summary.json'))
    assert len(rows)==25 and len({(r['ix'],r['iy']) for r in rows})==25
    assert Counter(r['block'] for r in rows)==Counter({'3_4':4,'3_5':2,'4_2':2,'4_3':13,'4_4':4})
    assert all(r['all_retrieved'] and r['matches_coverage_counts'] and r['butterfly_partition_ok'] and r['dated_partition_ok'] for r in rows)
    # Check original v1.8 monthly-roll contrast, independent of new daily scenarios.
    for r in rows:
        for k in ('E','S','P','B'):
            assert sum(r[k]['months'])==r[k]['hits']==r['expected'][k]
        r['p']={k:normalize(r[k]['months']) for k in ('E','S','P','B')}
        e,s,p,b=[r['p'][k] for k in ('E','S','P','B')]
        r['original']=contrast(np.roll(e,1),np.roll(s,1),p,b)-contrast(np.roll(e,-1),np.roll(s,-1),p,b)
        r['D0']=contrast(e,s,p,b)
    orig=block_summary(rows,'original');assert abs(orig['block_balanced_mean']-prev['primary']['block_balanced_mean'])<1e-12
    d0=block_summary(rows,'D0')
    for p in [np.ones(12),np.arange(12)+1]:
        for placement in ('uniform','first_day','last_day'):
            assert np.allclose(transform(p,(0,1),placement),normalize(p))
    results=[]
    for placement in ('uniform','first_day','last_day'):
      for mode in ('exposed_only','both_equal'):
        for name,window in WINDOWS.items():
          result=[]
          for r in rows:
            e,s,p,b=[r['p'][k] for k in ('E','S','P','B')]
            ef,er=[transform(e,window,placement,d) for d in (1,-1)]
            sf,sr=[transform(s,window,placement,d) for d in (1,-1)] if mode=='both_equal' else (s,s)
            f=contrast(ef,sf,p,b);rev=contrast(er,sr,p,b)
            result.append({'block':r['block'],'directional':f-rev,'forward_minus_zero':f-r['D0'],'reverse_minus_zero':rev-r['D0'],'forward':f,'reverse':rev,
              'min50':min(r[k]['hits'] for k in ('E','S','P','B'))>=50})
          results.append({'within_month_placement':placement,'transformation':mode,'window':name,'age_days_inclusive':[window[0],window[1]-1],
            'directional':block_summary(result,'directional'),'forward_minus_zero':block_summary(result,'forward_minus_zero'),'reverse_minus_zero':block_summary(result,'reverse_minus_zero'),
            'forward':block_summary(result,'forward'),'reverse':block_summary(result,'reverse'),
            'min50_directional':block_summary([r for r in result if r['min50']],'directional')})
    report={'status':'scenario_analysis_not_independent_evidence','input_zip_sha256':ZIP_SHA,'input_n':25,'blocks':5,'previous_primary_reproduced':orig,'previous_zero_lag':d0,'scenarios':results,
        'assumptions':['Adult observation month profiles are used only as hypothetical formation timing, not observed nests.','Nonleap circular calendar, equal weight across accessible days; no data-driven lifetime fitting.','Local Japanese 7–10 day occupied and 14–21 day postdeparture residue anchors are not transferable South American lifespan estimates.','First/last-day placement is extreme sensitivity, not an uncertainty interval or bound over every possible daily profile.','Exposed-only vs equal timing convolution of both classes separates a differential persistence assumption from generic temporal smoothing.','Both curve transformations are normalized; no nest abundance, volume, production rate, survival, climate, effort or actual recipient exposure estimate.','No new butterfly mating or fertility observations; no inference of cross-species facilitation.']}
    Path(out).write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('previous',orig['block_balanced_mean'],'D0',d0['block_balanced_mean'])
    for r in results:
      if r['within_month_placement']=='uniform':
        print(r['transformation'],r['window'],*[round(r[k]['block_balanced_mean'],6) for k in ('directional','forward_minus_zero','reverse_minus_zero')],r['directional']['positive_blocks'])
    for mode in ('exposed_only','both_equal'):
      for name in ('residue_14d_after_7d','residue_21d_after_10d'):
        print('sensitivity',mode,name,[(r['within_month_placement'],round(r['directional']['block_balanced_mean'],6)) for r in results if r['transformation']==mode and r['window']==name])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('zip');p.add_argument('--out',default='foam_legacy_kernel_v2.1.json');a=p.parse_args();main(a.zip,a.out)
