#!/usr/bin/env python3
"""AECO v0.3: finite-horizon encounter-to-fertilization coverage.
Analytic model and sensitivity analysis; no empirical frog or butterfly data.
"""
import csv
import math
from pathlib import Path

K = 10
Q = 0.8

def rates(m, h, k=K):
    if not (k >= 2 and 1/k < m < 1 and h > 0):
        raise ValueError("Require k>=2, hotspot male fraction above uniform and below one, h>0")
    return h*k*m, h*k*(1-m)/(k-1)

def gain(x):
    return -math.expm1(-x)

def threshold_static(m, h, k=K):
    a, b = rates(m, h, k)
    return (gain(h)-gain(b))/(gain(a)-gain(b))

def coverage(m, f, h, r, q=Q, k=K):
    """Stationary initial location; r is relaxation rate over horizon T=1.
    First completed mating is absorbing; q is success conditional on it.
    Outside patches are exchangeable; female switching independent of mating."""
    if not (0 <= f <= 1 and r >= 0 and 0 <= q <= 1):
        raise ValueError("Invalid fraction, relaxation rate or q")
    a, b = rates(m, h, k)
    if r == 0:
        return q*(f*gain(a)+(1-f)*gain(b))
    if f == 0:
        return q*gain(b)
    if f == 1:
        return q*gain(a)
    alpha, beta = r*(1-f), r*f
    trace = -(a+b+r)
    disc = math.hypot(a+alpha-b-beta, 2*math.sqrt(alpha*beta))
    fast = (trace-disc)/2
    slow = (a*b+a*beta+b*alpha)/fast
    mean = f*a+(1-f)*b
    w = (-mean-fast)/(slow-fast)
    return q*(w*gain(-slow)+(1-w)*gain(-fast))

def threshold(m, h, r, k=K):
    if r == 0:
        return threshold_static(m,h,k)
    lo,hi = 0.0,1.0
    for _ in range(70):
        mid=(lo+hi)/2
        if coverage(m,mid,h,r,k=k)>Q*gain(h):
            hi=mid
        else:
            lo=mid
    return (lo+hi)/2

def rows():
    for m in (.2,.4,.6,.8,.9):
        for h in (.05,.2,.5,2.0):
            for r in (0,.1,1,10,100):
                t=threshold(m,h,r)
                base=Q*gain(h)
                yield dict(K=K,male_hotspot_fraction=m,baseline_hazard=h,
                           female_switching_relaxation_rate=r,female_break_even=t,
                           potential_encounter_break_even=1/K,
                           gap=t-1/K,coverage_ratio_at_female_share_0_2=coverage(m,.2,h,r)/base)

def checks():
    for row in rows():
        m,h,r,t=(row[k] for k in ("male_hotspot_fraction","baseline_hazard","female_switching_relaxation_rate","female_break_even"))
        assert 1/K-1e-12 <= t <= 1
        assert abs(coverage(m,t,h,r)-Q*gain(h)) < 1e-9
        for f in (.05,.1,.2,.5,.95):
            a,b=rates(m,h)
            assert coverage(m,f,h,r) <= Q*gain(f*a+(1-f)*b)+1e-10
    assert abs(threshold(.6,.5,0)-.25861463)<1e-8
    assert abs(threshold(.6,.5,10)-.12253910)<1e-8
    assert abs(coverage(.6,.2,.5,1)/(Q*gain(.5))-.99166515)<1e-8

if __name__=="__main__":
    checks()
    data=list(rows())
    out=Path("results/fertilization_thresholds_v0.3.csv")
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    print("Theoretical rows:",len(data))
