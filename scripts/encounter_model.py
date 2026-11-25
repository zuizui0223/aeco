#!/usr/bin/env python3
"""Analytic toy model, not empirical evidence. Equal patches, fixed adult abundance."""
import json
import math
from pathlib import Path

K = 10
Q = 0.8
BASELINE_HAZARDS = (0.05, 0.5, 2.0)

def fractions(share):
    assert 0 <= share <= 1
    return [share] + [(1-share)/(K-1)]*(K-1)

def evaluate(male_share, female_share, baseline_hazard, q=Q):
    m, f = fractions(male_share), fractions(female_share)
    # hazard integrated over a fixed time horizon; constant local hazard
    relative_encounters = K * sum(mi*fi for mi,fi in zip(m,f))
    first_fertilization = sum(fi*q*(-math.expm1(-baseline_hazard*K*mi)) for mi,fi in zip(m,f))
    uniform = q*(-math.expm1(-baseline_hazard))
    return dict(male_share=male_share, female_share=female_share,
                uniform_hazard=baseline_hazard, q=q, encounter_ratio=relative_encounters,
                fertilization_probability=first_fertilization,
                uniform_fertilization_probability=uniform,
                fertilization_ratio=first_fertilization/uniform)

def main():
    cases = [evaluate(m,f,h) for m,f in [(0.1,0.1),(0.6,0.05),(0.6,0.1),(0.6,0.2),(0.6,0.4)] for h in BASELINE_HAZARDS]
    assert math.isclose(evaluate(0.6,0.1,0.5)["encounter_ratio"],1.0)
    assert evaluate(0.6,0.1,0.5)["fertilization_ratio"] < 1.0
    assert evaluate(0.6,0.05,0.5)["encounter_ratio"] < 1.0
    assert evaluate(0.6,0.2,0.5)["encounter_ratio"] > 1.0
    assert all(0 <= x["fertilization_probability"] <= Q for x in cases)
    out = Path("results/encounter_scenarios.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"status":"theoretical_scenarios_not_empirical","K":K,
        "conditional_fertilization_probability":Q,
        "assumptions":"equal patches, no migration, fixed abundance, local random mixing, first completed mating only, constant hazard and q",
        "cases":cases}, indent=2)+"\n")
    print("Wrote",out)

if __name__=="__main__":
    main()
