import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("data/processed")
EXPECTED = json.loads(
    Path("results/expected_metrics.json").read_text()
)

validation = pd.read_csv(
    BASE / "exail_frozen_twin_multirun_validation.csv"
)

ablation = pd.read_csv(
    BASE / "atomic_gravity_ablation/ablation_summary.csv"
)

checks = []

def check(name, actual, expected, tolerance=1e-6):
    passed = bool(np.isclose(
        actual, expected, atol=tolerance, rtol=0
    ))
    checks.append(passed)
    print(
        f"{'PASS' if passed else 'FAIL'} | {name}: "
        f"actual={actual}, expected={expected}"
    )

check("Total measurements", len(validation),
      EXPECTED["total_shots"], 0)

train = validation[validation.Run.between(12, 16)]
test = validation[validation.Run.between(17, 20)]

check("Training measurements", len(train),
      EXPECTED["training_shots"], 0)

check("Test measurements", len(test),
      EXPECTED["test_shots"], 0)

check(
    "Acceleration MAE",
    validation.g_error.abs().mean(),
    EXPECTED["acceleration_mae_m_s2"]
)

check(
    "Detector MAE",
    validation.ratio_error.abs().mean(),
    EXPECTED["detector_mae"]
)

actual_r2 = 1 - (
    np.sum(validation.ratio_error**2)
    / np.sum(
        (validation.Ratio - validation.Ratio.mean())**2
    )
)

check("Detector R2", actual_r2,
      EXPECTED["detector_r2"])

rows = ablation.set_index("model")

a = rows.loc["A_UNIVERSAL"]
b = rows.loc["B_CONDITIONED"]
c = rows.loc["C_QMS"]

check(
    "Universal interval score",
    a.mean_interval_score,
    EXPECTED["universal_interval_score"]
)

check(
    "Conditioned interval score",
    b.mean_interval_score,
    EXPECTED["conditioned_interval_score"]
)

improvement = (
    100 * (a.mean_interval_score - b.mean_interval_score)
    / a.mean_interval_score
)

check(
    "Interval-score improvement %",
    improvement,
    EXPECTED["interval_score_improvement_pct"]
)

check(
    "Conditioned discrepancy count",
    b.outside_count,
    EXPECTED["conditioned_outside_count"], 0
)

check(
    "QMS score equivalence",
    c.mean_interval_score,
    b.mean_interval_score
)

print("\n" + "=" * 55)
print("EXAIL REPRODUCIBILITY VERIFICATION")
print("=" * 55)

if all(checks):
    print("PASS — All frozen numerical checks reproduced.")
else:
    print("FAIL — Results differ from frozen reference.")
    raise SystemExit(1)
