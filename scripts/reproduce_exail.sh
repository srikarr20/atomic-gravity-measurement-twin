#!/bin/bash
set -euo pipefail

mkdir -p data/processed

PYTHONPATH=. python3 scripts/validate_multirun_frozen_twin.py

PYTHONPATH=. python3 scripts/analyze_waveform_residual_structure.py

PYTHONPATH=. python3 experiments/prototype_12.py

PYTHONPATH=. python3 scripts/verify_exail_results.py
