"""
ATOMIC GRAVITY MEASUREMENT-SYSTEM TWIN
======================================

Adapted from modelling patterns already implemented across
srikarr20 repositories.

Current hierarchy:

PHYSICAL SYSTEM
    acceleration / gravity
        |
        v
[1] INERTIAL FORWARD MODEL
    acceleration -> interferometer phase
        |
        |  STATUS: VALIDATED
        |  DATA: Exail Run 11
        v
[2] ATOMIC INTERFERENCE MODEL
    phase / chirp -> atomic populations
        |
        |  STATUS: PARTIALLY ESTABLISHED
        |  DATA: Hannover fringes
        |  NOTE: generic T^2 model insufficient;
        |        published finite-pulse scale factors required
        v
[3] DETECTOR / READOUT MODEL
    fluorescence waveform -> population observable
        |
        |  STATUS: EMPIRICALLY VALIDATED
        |  DATA: Exail Run 11
        |  NOTE: detector normalization reconstructed empirically
        v
[4] INFERENCE MODEL
    measured phase/population -> acceleration/gravity
        |
        |  STATUS:
        |    Exail: validated against QA750 reference
        |    Hannover: publication-calibrated differential inference
        v
    inferred physical parameter

TWIN LOOP
    measurement
        -> inverse model
        -> inferred physical state
        -> forward model
        -> predicted measurement
        -> residual
        -> adaptation

This structure follows existing QMS/DPI closed-loop twin patterns.
"""


from dataclasses import dataclass
from enum import Enum


class EvidenceLevel(Enum):
    VALIDATED = "validated"
    PUBLICATION_CALIBRATED = "publication_calibrated"
    EMPIRICALLY_RECONSTRUCTED = "empirically_reconstructed"
    PARTIAL = "partial"
    UNRESOLVED = "unresolved"


@dataclass
class TwinLayer:
    name: str
    input_quantity: str
    output_quantity: str
    evidence: EvidenceLevel
    dataset: str
    notes: str


LAYERS = [

    TwinLayer(
        name="inertial_forward_model",
        input_quantity="acceleration",
        output_quantity="interferometer_phase",
        evidence=EvidenceLevel.VALIDATED,
        dataset="Exail Run 11",
        notes=(
            "237 clean shots; acceleration-to-phase "
            "relationship validated against experimental phase."
        ),
    ),

    TwinLayer(
        name="atomic_interference_model",
        input_quantity="phase/chirp",
        output_quantity="atomic_population",
        evidence=EvidenceLevel.PARTIAL,
        dataset="Hannover gravimeter fringes",
        notes=(
            "Population fringes experimentally present at "
            "T=155, 305, 455 us. Simple common T^2 model "
            "was inadequate. Published finite-pulse scale "
            "factor treatment required."
        ),
    ),

    TwinLayer(
        name="detector_readout_model",
        input_quantity="fluorescence_waveform",
        output_quantity="population_ratio",
        evidence=EvidenceLevel.EMPIRICALLY_RECONSTRUCTED,
        dataset="Exail Run 11",
        notes=(
            "Four-window detector transformation reconstructed "
            "from 242 raw detection records; R^2 ~0.9925 "
            "against reported Ratio."
        ),
    ),

    TwinLayer(
        name="physical_parameter_inference",
        input_quantity="measured_phase_or_population",
        output_quantity="acceleration_or_gravity",
        evidence=EvidenceLevel.VALIDATED,
        dataset="Exail + Hannover",
        notes=(
            "Exail blind phase-to-acceleration recovery validated "
            "against independent QA750 reference. Hannover "
            "differential population estimator implemented using "
            "publication scale factors."
        ),
    ),
]


def print_hierarchy():

    print()
    print("=" * 72)
    print("ATOMIC GRAVITY MEASUREMENT-SYSTEM TWIN")
    print("=" * 72)

    for i, layer in enumerate(LAYERS, start=1):

        print()
        print(f"[{i}] {layer.name}")
        print(
            "    ",
            layer.input_quantity,
            "->",
            layer.output_quantity,
        )
        print(
            "     evidence:",
            layer.evidence.value,
        )
        print(
            "     dataset:",
            layer.dataset,
        )
        print(
            "     notes:",
            layer.notes,
        )

    print()
    print("=" * 72)


if __name__ == "__main__":
    print_hierarchy()
