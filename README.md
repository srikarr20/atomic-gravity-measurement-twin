# Atomic Gravity Measurement-System Twin

A research software prototype for physics-informed modelling,
detector-response prediction, and uncertainty assessment in
atomic gravimetry.

## Objective

Develop a forward measurement model connecting:

Experimental controls
→ Atomic interferometer physics
→ Predicted atomic populations
→ Detector response
→ Recorded measurements
→ Residual and uncertainty assessment

The objective is to validate this complete chain against
measurements from a single atomic gravimeter.

## Implemented Components

### 1. Atomic Interferometer Physics
- Gravity-dependent interferometer phase model
- Raman pulse-sequence modelling
- Raman momentum propagation utilities
- Predicted atomic-state populations

### 2. Detector Modelling
- Atomic population detector model
- Detection-window integration
- Population observable reconstruction

### 3. Evidence and Uncertainty
- Layer-specific residual evaluation
- Operating-state-conditioned uncertainty
- Explicit unresolved-model limitations

## Experimental Evidence

Analysis of recorded Exail atomic-gravimeter data:

Calibration: Runs 12–16
Held-out evaluation: Runs 17–20

Results:

| Metric | Universal | State-conditioned |
|---|---:|---:|
| 90% interval coverage | 93.39% | 93.94% |
| Mean interval width (rad) | 122.29 | 106.43 |
| Mean interval score | 148.50 | 117.16 |

State conditioning improved the held-out interval score
by 21.1% relative to the universal baseline.

This is an improvement in residual uncertainty
characterization, not demonstrated gravity accuracy.

## Validation Status

- Physics models: implemented and simulation-tested
- Detector models: implemented and partially tested
- Exail uncertainty analysis: evaluated on held-out runs
- Complete forward-model-to-detector validation:
  not yet established on a single instrument
- Live hardware validation: not performed

## Data Requirements

A limited experimental sequence containing:

1. Documented Raman pulse timing, chirp and phase settings
2. Calibrated F1/F2 populations or detector ratios
3. Corresponding gravity or acceleration reference
4. Shot identifiers and relevant uncertainty information

Proprietary source code and raw hardware internals
are not required for the proposed initial validation.

## Reproducibility

Python dependencies:

    pip install -r requirements.txt

The included Exail validation scripts expect:

    data/processed/exail_waveform_residual_diagnostics.csv

The processed input is not distributed here.
The numerical results above are reported from prior
local experiments and are not independently reproducible
from this repository alone.

## Scientific Boundaries

This is a research prototype, not a validated
commercial gravimeter digital twin.

No new quantum-physics claims are made.

No instrument-specific adaptive control performance
or independent fault-diagnosis accuracy is claimed.
