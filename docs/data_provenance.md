# Exail Recorded-Data Benchmark — Provenance

## Data source

Exail Bordeaux atomic-interferometer experimental records.

Source release:
https://zenodo.org/records/11543715

The raw data is not redistributed in this repository.

## Expected source structure

data/raw/exail_bordeaux/extracted/Raw Data/
Figure 3 & 5/20230317/

Required:
- Raman/Run 12 through Run 20
- Streaming/Run12_1.csv through Run20_1.csv

Run 11 was used to establish frozen empirical detector
calibration constants.

## Processing

1. validate_multirun_frozen_twin.py
   - Reads Raman phase and population-ratio records
   - Reconstructs TotalPhase
   - Infers acceleration using a simplified phase model
   - Compares against QA750-derived acceleration magnitude
   - Reconstructs detector ratios using frozen Run-11 calibration

2. analyze_waveform_residual_structure.py
   - Extracts acceleration-waveform features
   - Joins records by Run and Iteration

3. prototype_12.py
   - Calibrates uncertainty on Runs 12-16
   - Evaluates on Runs 17-20
   - Compares universal and operating-state-conditioned intervals

## Scientific limitations

The phase model omits explicit Raman chirp and
other instrument-specific phase contributions.

The QA750-derived reference is a classical acceleration
measurement, not an independently established
absolute gravity truth.

The detector normalization is empirically reconstructed,
not Exail's documented proprietary calibration.

The benchmark does not establish complete
first-principles gravity-to-detector validation.

The 21.1% improvement concerns the implemented
phase-residual interval score, not gravity accuracy.

The reported reproducibility was checked in the
original local Exail data environment.
