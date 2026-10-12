"""
Atomic Gravity Twin — Prototype 10A

Real-data evidence-to-decision integration.

Exail Runs 17–20.
Frozen operating-state thresholds from 09B.

Does not infer fault cause.
Does not claim validated adaptive control.
"""

from pathlib import Path
import numpy as np
import pandas as pd

SOURCE = Path(
    "data/processed/exail_waveform_residual_diagnostics.csv"
)

OUT = Path(
    "data/processed/atomic_gravity_evidence"
)
OUT.mkdir(parents=True, exist_ok=True)

K = 4*np.pi/780.24e-9
T = 0.010

Q1 = 0.019083246267433563
Q2 = 0.03014219126267755

THRESHOLDS = {
    "LOW": 32.830983894464225,
    "MEDIUM": 50.09491819754385,
    "HIGH": 92.70385349428726
}

d = pd.read_csv(SOURCE)
d = d[d.Run.between(17, 20)].copy()

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

d["predicted_phase"] = (
    direction*K*d.g_reference*T*T
)

d["phase_residual"] = (
    d.TotalPhase-d.predicted_phase
)

d["operating_state"] = np.where(
    d.wave_std <= Q1,
    "LOW",
    np.where(
        d.wave_std <= Q2,
        "MEDIUM",
        "HIGH"
    )
)

d["uncertainty_threshold"] = (
    d.operating_state.map(THRESHOLDS)
)

d["outside_interval"] = (
    d.phase_residual.abs()
    > d.uncertainty_threshold
)

def decide(row):
    if row.outside_interval:
        return "INVESTIGATE_MODEL_DISCREPANCY"

    return "NO_DISCREPANCY_FLAG"

d["evidence_decision"] = d.apply(
    decide, axis=1
)

# Explicitly abstain from unsupported actions.
d["fault_cause"] = "UNRESOLVED"
d["adaptive_action"] = "NOT_VALIDATED"
d["action_reason"] = (
    "No Exail-calibrated action-response model"
)

print("="*78)
print("ATOMIC GRAVITY TWIN — PROTOTYPE 10A")
print("="*78)

print("\n=== EVIDENCE DECISIONS ===")
print(d.evidence_decision.value_counts())

print("\n=== BY OPERATING STATE ===")

summary = pd.crosstab(
    d.operating_state,
    d.evidence_decision
)

print(summary.to_string())

print("\n=== ACTION VALIDATION STATUS ===")
print(d.adaptive_action.value_counts())

print("\n=== FIRST 10 RECORDS ===")
print(
    d[
        [
            "Run", "Iteration",
            "operating_state",
            "phase_residual",
            "uncertainty_threshold",
            "evidence_decision",
            "fault_cause",
            "adaptive_action"
        ]
    ].head(10).to_string(index=False)
)

d.to_csv(
    OUT/"evidence_decision_history.csv",
    index=False
)

summary.to_csv(
    OUT/"evidence_decision_summary.csv"
)

print("\nSaved:", OUT)

print("\nSCIENTIFIC BOUNDARIES")
print("No independently verified fault labels.")
print("No Exail-calibrated adaptive action model.")
print("No causal attribution from residual alone.")
print("No live hardware validation.")
