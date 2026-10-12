"""
Atomic Gravity Twin — Prototype 09B

Operating-state-conditioned uncertainty.

Calibration: Runs 12-16.
Held-out: Runs 17-20.

Compares universal and state-conditioned
symmetric 90% residual prediction intervals.

No residual correction.
No adaptive measurement policy.
"""

from pathlib import Path
import numpy as np
import pandas as pd

SOURCE = Path(
    "data/processed/exail_waveform_residual_diagnostics.csv"
)

OUT = Path(
    "data/processed/atomic_gravity_uncertainty"
)
OUT.mkdir(parents=True, exist_ok=True)

Q1 = 0.019083246267433563
Q2 = 0.03014219126267755

K = 4*np.pi/780.24e-9
T = 0.010
ALPHA = 0.10

d = pd.read_csv(SOURCE)
d = d[d.Run.between(12, 20)].copy()

required = [
    "Run", "Direction", "g_reference",
    "TotalPhase", "wave_std"
]
d = d.dropna(subset=required)

sign = d.Direction.map({
    "kU": 1.0,
    "kD": -1.0
})

if sign.isna().any():
    raise ValueError("Unknown Raman direction")

d["residual"] = (
    d.TotalPhase
    - sign*K*d.g_reference*T*T
)

d["abs_residual"] = d.residual.abs()

d["state"] = np.where(
    d.wave_std <= Q1,
    "LOW",
    np.where(
        d.wave_std <= Q2,
        "MEDIUM",
        "HIGH"
    )
)

train = d[d.Run.between(12, 16)].copy()
test = d[d.Run.between(17, 20)].copy()

universal_q = train.abs_residual.quantile(
    1-ALPHA
)

state_q = (
    train.groupby("state")
    .abs_residual
    .quantile(1-ALPHA)
    .to_dict()
)

def interval_score(error, q):
    """
    Central symmetric interval [-q, q].
    Standard interval score at miscoverage alpha.
    """
    lower = -q
    upper = q

    return (
        upper-lower
        + (2/ALPHA)*np.maximum(lower-error, 0)
        + (2/ALPHA)*np.maximum(error-upper, 0)
    )

def evaluate(x, model):
    if model == "UNIVERSAL":
        q = np.full(len(x), universal_q)
    else:
        q = x.state.map(state_q).to_numpy()

    e = x.residual.to_numpy()

    return {
        "coverage": np.mean(np.abs(e) <= q),
        "mean_width": np.mean(2*q),
        "mean_interval_score": np.mean(
            interval_score(e, q)
        )
    }

rows = []

for group_name, x in [
    ("ALL", test),
    *list(test.groupby("state"))
]:
    for model in ["UNIVERSAL", "CONDITIONED"]:
        rows.append({
            "group": group_name,
            "model": model,
            "shots": len(x),
            **evaluate(x, model)
        })

result = pd.DataFrame(rows)

print("="*78)
print("ATOMIC GRAVITY TWIN — PROTOTYPE 09B")
print("="*78)

print("\n=== FROZEN TRAINING QUANTILES ===")
print("Universal:", universal_q)

for state in ["LOW", "MEDIUM", "HIGH"]:
    print(state, state_q[state])

print("\n=== HELD-OUT PERFORMANCE ===")
print(result.to_string(
    index=False,
    float_format=lambda x: f"{x:.6f}"
))

print("\n=== OVERALL INTERVAL SCORE IMPROVEMENT ===")

a = result[
    (result.group == "ALL")
    & (result.model == "UNIVERSAL")
].iloc[0]

b = result[
    (result.group == "ALL")
    & (result.model == "CONDITIONED")
].iloc[0]

improvement = (
    100 * (
        a.mean_interval_score
        - b.mean_interval_score
    ) / a.mean_interval_score
)

print(f"Conditioned vs universal: {improvement:.3f}%")

result.to_csv(
    OUT/"uncertainty_comparison.csv",
    index=False
)

print("\nSaved:", OUT)
print("Intervals are empirical, not guaranteed.")
print("Shot-level observations may be dependent.")
