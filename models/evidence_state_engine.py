"""
Atomic Gravity Twin v0.6
Evidence & Observability State Engine

Converts layer residuals, operating state, validation evidence,
and known scientific boundaries into an explicit diagnostic state.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class LayerStatus(Enum):
    CONSISTENT = "consistent"
    MISMATCH = "mismatch"
    LOW_OBSERVABILITY = "low_observability"
    UNRESOLVED = "unresolved"


@dataclass
class LayerEvidence:
    layer: str
    status: LayerStatus
    residual: Optional[float]
    threshold: Optional[float]
    operating_state: Optional[str]
    observability_floor_pct: Optional[float]
    evidence: str
    limitation: Optional[str]


# Frozen from v0.5
FORWARD_THRESHOLDS = {
    "LOW": 38.81592951865241,
    "MEDIUM": 62.488722871610435,
    "HIGH": 120.77490631227845,
}

FORWARD_OBSERVABILITY = {
    "LOW": 0.25,
    "MEDIUM": 0.50,
    "HIGH": 1.00,
}

# Frozen Run-11 detector threshold
DETECTOR_THRESHOLD = 0.030161711316181006


def evaluate_forward(
    residual_rad,
    operating_state,
):
    threshold = FORWARD_THRESHOLDS[
        operating_state
    ]

    floor = FORWARD_OBSERVABILITY[
        operating_state
    ]

    mismatch = (
        abs(residual_rad)
        > threshold
    )

    status = (
        LayerStatus.MISMATCH
        if mismatch
        else LayerStatus.CONSISTENT
    )

    return LayerEvidence(
        layer="inertial_forward_model",
        status=status,
        residual=float(residual_rad),
        threshold=float(threshold),
        operating_state=operating_state,
        observability_floor_pct=float(floor),
        evidence=(
            "Run-11-calibrated state-conditioned residual "
            "evaluated prospectively against Runs 12-20."
        ),
        limitation=(
            "No mismatch detected does not imply arbitrary "
            "forward-model accuracy. >=90% empirical detection "
            f"was demonstrated only for tested T perturbations "
            f"of approximately {floor:.2f}% or larger in this "
            "operating state."
        ),
    )


def evaluate_detector(
    residual,
):
    mismatch = (
        abs(residual)
        > DETECTOR_THRESHOLD
    )

    status = (
        LayerStatus.MISMATCH
        if mismatch
        else LayerStatus.CONSISTENT
    )

    return LayerEvidence(
        layer="detector_readout_model",
        status=status,
        residual=float(residual),
        threshold=float(
            DETECTOR_THRESHOLD
        ),
        operating_state=None,
        observability_floor_pct=None,
        evidence=(
            "Detector transformation calibrated on Run 11 "
            "and transferred without recalibration across "
            "2,108 measurements from Runs 12-20 "
            "(R^2 approximately 0.9942)."
        ),
        limitation=(
            "Detector transformation was empirically "
            "reconstructed and is not claimed to be "
            "Exail's documented proprietary equation."
        ),
    )


def evaluate_interference():
    return LayerEvidence(
        layer="atomic_interference_model",
        status=LayerStatus.UNRESOLVED,
        residual=None,
        threshold=None,
        operating_state=None,
        observability_floor_pct=None,
        evidence=(
            "Hannover data demonstrates atomic population "
            "fringes, but Exail Total Phase 3 does not "
            "directly predict Ratio under the tested "
            "closed-loop protocol."
        ),
        limitation=(
            "Instrument-specific residual/compensation phase "
            "between reported Exail phase variables and "
            "atomic population remains unresolved."
        ),
    )


def evaluate_twin(
    *,
    forward_residual_rad,
    detector_residual,
    operating_state,
):
    layers = [
        evaluate_forward(
            forward_residual_rad,
            operating_state,
        ),
        evaluate_interference(),
        evaluate_detector(
            detector_residual,
        ),
    ]

    mismatch_layers = [
        x.layer
        for x in layers
        if x.status == LayerStatus.MISMATCH
    ]

    unresolved_layers = [
        x.layer
        for x in layers
        if x.status == LayerStatus.UNRESOLVED
    ]

    return {
        "operating_state":
            operating_state,

        "mismatch_detected":
            bool(mismatch_layers),

        "mismatch_layers":
            mismatch_layers,

        "unresolved_layers":
            unresolved_layers,

        "layers": [
            {
                **asdict(x),
                "status": x.status.value,
            }
            for x in layers
        ],
    }
