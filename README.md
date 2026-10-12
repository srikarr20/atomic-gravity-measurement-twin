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

The Exail recorded-data benchmark can be reproduced using
the original publicly released experimental files.

**Dataset:** https://zenodo.org/records/11543715

The original data is not redistributed in this repository.

### Setup

Install dependencies:

    pip install -r requirements.txt

Extract the original data under:

    data/raw/exail_bordeaux/extracted/Raw Data/Figure 3 & 5/20230317/

Required subdirectories:

- Raman/
- Streaming/

### Run the complete benchmark

    ./scripts/reproduce_exail.sh

The pipeline performs:

1. Frozen Run-11 calibration evaluation on Runs 12-20.
2. Acceleration waveform feature extraction.
3. Uncertainty calibration on Runs 12-16.
4. Held-out evaluation on Runs 17-20.
5. Automated verification against frozen reference metrics.

### Expected results

| Metric | Result |
|---|---:|
| Total measurements | 2,108 |
| Training measurements | 1,200 |
| Held-out measurements | 908 |
| Detector reconstruction R² | 0.994206 |
| Universal interval score | 148.500747 |
| Conditioned interval score | 117.156474 |
| Interval-score improvement | 21.1071% |

All 11 numerical verification checks passed in the
original local Exail data environment.

Independent reproduction requires downloading the
source dataset and running the pipeline.

See [Data Provenance](docs/data_provenance.md)
for experimental assumptions and limitations.

## Scientific Boundaries

This is a research prototype, not a validated
commercial gravimeter digital twin.

No new quantum-physics claims are made.

No instrument-specific adaptive control performance
or independent fault-diagnosis accuracy is claimed.
