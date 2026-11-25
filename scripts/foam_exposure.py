#!/usr/bin/env python3
"""Published frog-only arithmetic and prospective monitoring calculations; no butterfly data."""
import argparse
import json
import math
from pathlib import Path


def upper_zero(n, detect, alpha=.05):
    """Independent sampling units; homogeneous use and known detection given use."""
    if n < 1 or not 0 < detect <= 1 or not 0 < alpha < 1:
        raise ValueError('invalid n, detection or alpha')
    return min(1., -math.expm1(math.log(alpha)/n)/detect)


def required_units(use, detect, alpha=.05):
    if not 0 < use < 1 or not 0 < detect <= 1 or not 0 < alpha < 1:
        raise ValueError('invalid use, detection or alpha')
    return math.ceil(math.log(alpha)/math.log1p(-use*detect))


def compute():
    n=134
    failed=44
    dry=40
    wind=4
    dry_single=33
    vmin,vmax=47.12,1319.47
    fstat,df=324.44,132
    rows=[dict(independent_units=k,conditional_detection=d,upper_use_given_zero=upper_zero(k,d))
          for k in (6,12,24,48,72) for d in (.25,.5,.8,1.)]
    requirements=[dict(target_use=p,conditional_detection=d,required_independent_units=required_units(p,d))
          for p in (.05,.1,.2) for d in (.25,.5,.8,1.)]
    for item in requirements:
        p,d,k=item['target_use'],item['conditional_detection'],item['required_independent_units']
        assert (1-p*d)**k <= .05+1e-12
        assert (1-p*d)**(k-1) > .05-1e-12
    assert failed==dry+wind
    assert math.isclose(upper_zero(1,1),.95)
    return dict(status='published_aggregate_and_prospective_design_only',
        source='https://doi.org/10.1093/evolut/qpag071',species='Chiromantis xerampelina',
        reported_nests=n,reported_failure_count=failed,overall_failure_fraction_recomputed=failed/n,
        published_overall_failure_percentage=30.55,discrepancy_percentage_points=100*failed/n-30.55,
        desiccation_count=dry,wind_failure_count=wind,desiccation_fraction_all=dry/n,
        desiccation_fraction_excluding_wind=dry/(n-wind),single_male_fraction_among_desiccated=dry_single/dry,
        min_volume_ml=vmin,max_volume_ml=vmax,volume_range_ratio=vmax/vmin,
        projected_area_range_ratio_if_geometrically_similar=(vmax/vmin)**(2/3),
        male_number_volume_simple_regression_r2_from_F=fstat/(fstat+df),
        monitoring_zero_detection_scenarios=rows,monitoring_sample_size_scenarios=requirements,
        caveats=['African frog results do not parameterize Japanese frog or butterfly attraction.',
                 'Failure count and printed percent disagree; use counts provisionally and seek raw data.',
                 'Projected area ratio is a geometric hypothetical, not measured visible area or effect on butterflies.',
                 'Zero-detection bounds assume independent units, common use probability and known conditional detection; repeated nest-hours or nests in one pond are not independent units.',
                 'Use means at least one target visit during a standardized observation window; not lifetime utilization or fertilization.'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('results/foam_exposure_v0.7.json'));a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(compute(),indent=2)+'\n')
    print(a.output)
