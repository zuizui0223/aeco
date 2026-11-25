#!/usr/bin/env python3
"""AECO v0.4 illustrative competing-risk model, not empirical calibration."""
import csv
import math
from pathlib import Path

def gain(x):
    return -math.expm1(-x)

def evaluate(d, f, m=.6, h=.5, k=10, q=.8):
    if not (d >= 0 and 0 <= f <= 1 and 1/k < m < 1 and h > 0 and 0 < q <= 1):
        raise ValueError("invalid scenario")
    a,b=k*m*h,k*(1-m)*h/(k-1)
    hotspot=q*a/(a+d)*gain(a+d)
    outside=q*gain(b)
    base=q*gain(h)
    p=f*hotspot+(1-f)*outside
    threshold=(base-outside)/(hotspot-outside) if hotspot>base else None
    return dict(extra_loss_hazard=d,female_hotspot_share=f,male_hotspot_share=m,
                baseline_hazard=h,conditional_success=q,hotspot_success=hotspot,
                outside_success=outside,baseline_success=base,coverage=p,
                coverage_ratio=p/base,female_threshold_strict_gain=threshold,
                strict_gain_possible=threshold is not None)

def main():
    rows=[evaluate(d,f) for d in (0,.1,.5,1,2,4,8) for f in (.1,.2,.4,.6,1.)]
    assert math.isclose(evaluate(0,.2)["coverage_ratio"],.8881318776648809)
    for f in (.1,.2,.4,.6,1.):
        p=[evaluate(d,f)["coverage"] for d in (0,.1,.5,1,2,4,8)]
        assert all(a>=b for a,b in zip(p,p[1:]))
    assert evaluate(8,1)["strict_gain_possible"] is False
    out=Path("results/frog_competing_risk_v0.4.csv")
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

if __name__=="__main__":
    main()
