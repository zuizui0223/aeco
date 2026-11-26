#!/usr/bin/env python3
"""Leave-one-species-out diagnostic; no independent resampling or hypothesis test."""
import argparse,json
from pathlib import Path
import pandas as pd

def main():
    p=argparse.ArgumentParser();p.add_argument('summary');a=p.parse_args()
    path=Path(a.summary);r=json.loads(path.read_text())
    sp=pd.DataFrame(r['species_summary']);out=[]
    for (sc,ct),f in sp.groupby(['scale','context']):
        for s in sorted(f.species.unique()):
            x=f[f.species!=s];g=x.groupby('group')[['C','chroma']].mean()
            if len(g)!=6:continue
            dist=((g-g.loc['foam'])**2).sum(axis=1)**.5;dist=dist.drop('foam')
            out.append({'scale':float(sc),'context':ct,'excluded_species':s,'nearest':dist.idxmin(),'distance':float(dist.min()),'both_white_pale_closer_than_all_others':float(dist[['white_flower','pale_fungus']].max())<float(dist.drop(['white_flower','pale_fungus']).min())})
    q=pd.DataFrame(out)
    r['leave_one_species_out']={'n_cases':len(q),'excluded_single_species_group':'colored_fungus (cannot remove sole species and retain all six groups)','nearest_counts':q.nearest.value_counts().to_dict(),'both_white_pale_closer_cases':int(q.both_white_pale_closer_than_all_others.sum()),'rows':out}
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(r['leave_one_species_out']['n_cases'],r['leave_one_species_out']['nearest_counts'])
if __name__=='__main__':main()
