"""
Atomic Gravity Twin — Prototype 12
Real-data evidence-layer ablation.

Calibration: Runs 12-16
Evaluation: Runs 17-20

Compares:
A: Universal uncertainty
B: Operating-state-conditioned uncertainty
C: Conditioned uncertainty + QMS decision semantics

No fault labels, no adaptive control validation.
"""

from pathlib import Path
import numpy as np
import pandas as pd

SOURCE = Path(
    "data/processed/exail_waveform_residual_diagnostics.csv"
)

OUT = Path(
    "data/processed/atomic_gravity_ablation"
)
OUT.mkdir(parents=True, exist_ok=True)

K = 4*np.pi/780.24e-9
T = 0.010
ALPHA = 0.10

Q1 = 0.019083246267433563
Q2 = 0.03014219126267755

d = pd.read_csv(SOURCE)
d = d[d.Run.between(12,20)].copy()

required = [
    "Run", "Iteration", "Direction",
    "g_reference", "TotalPhase", "wave_std"
]
d = d.dropna(subset=required)

direction = d.Direction.map({
    "kU": 1.0,
    "kD": -1.0
})

if direction.isna().any():
    raise ValueError("Unexpected Raman direction")

d["residual"] = (
    d.TotalPhase
    - direction*K*d.g_reference*T*T
)

d["state"] = np.where(
    d.wave_std <= Q1,
    "LOW",
    np.where(
        d.wave_std <= Q2,
        "MEDIUM",
        "HIGH"
    )
)

train = d[d.Run.between(12,16)].copy()
test = d[d.Run.between(17,20)].copy()

universal_q = train.residual.abs().quantile(
    1-ALPHA
)

state_q = (
    train.assign(abs_error=train.residual.abs())
    .groupby("state")["abs_error"]
    .quantile(1-ALPHA)
    .to_dict()
)

def interval_score(error, q):
    lower = -q
    upper = q

    return (
        2*q
        + (2/ALPHA)*np.maximum(lower-error,0)
        + (2/ALPHA)*np.maximum(error-upper,0)
    )

records = []

for model in ["A_UNIVERSAL", "B_CONDITIONED", "C_QMS"]:

    x = test.copy()

    if model == "A_UNIVERSAL":
        x["threshold"] = universal_q
    else:
        x["threshold"] = x.state.map(state_q)

    x["outside"] = (
        x.residual.abs() > x.threshold
    )

    x["interval_score"] = interval_score(
        x.residual.to_numpy(),
        x.threshold.to_numpy()
    )

    if model == "C_QMS":
        x["decision"] = np.where(
            x.outside,
            "INVESTIGATE_MODEL_DISCREPANCY",
            "NO_DISCREPANCY_FLAG"
        )
        x["fault_cause"] = "UNRESOLVED"
        x["adaptive_action"] = "NOT_VALIDATED"
    else:
        x["decision"] = "NOT_EVALUATED"
        x["fault_cause"] = "NOT_EVALUATED"
        x["adaptive_action"] = "NOT_EVALUATED"

    records.append({
        "model": model,
        "shots": len(x),
        "coverage": (~x.outside).mean(),
        "mean_interval_width": (2*x.threshold).mean(),
        "mean_interval_score": x.interval_score.mean(),
        "outside_count": int(x.outside.sum()),
        "explicit_abstention_count": (
            len(x) if model == "C_QMS" else 0
        )
    })

    x.to_csv(
        OUT/f"{model.lower()}_history.csv",
        index=False
    )

summary = pd.DataFrame(records)

print("="*76)
print("ATOMIC GRAVITY TWIN — PROTOTYPE 12")
print("="*76)

print("\n=== EVIDENCE ABLATION ===")
print(summary.to_string(
    index=False,
    float_format=lambda v: f"{v:.6f}"
))

a = summary[summary.model=="A_UNIVERSAL"].iloc[0]
b = summary[summary.model=="B_CONDITIONED"].iloc[0]
c = summary[summary.model=="C_QMS"].iloc[0]

print("\n=== CONTRIBUTION OF OPERATING STATE ===")
print(
    "Interval score improvement:",
    100*(a.mean_interval_score-b.mean_interval_score)
    /a.mean_interval_score,
    "%"
)

print("\n=== CONTRIBUTION OF QMS SEMANTICS ===")
print(
    "B and C interval scores identical:",
    np.isclose(
        b.mean_interval_score,
        c.mean_interval_score
    )
)

print(
    "QMS explicit abstentions:",
    int(c.explicit_abstention_count)
)

summary.to_csv(
    OUT/"ablation_summary.csv",
    index=False
)

print("\nSaved:", OUT)
print("No independent fault labels.")
print("No causal attribution.")
print("No validated adaptive measurement actions.")
