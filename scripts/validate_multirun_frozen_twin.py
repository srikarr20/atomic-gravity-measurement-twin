"""
Frozen multi-run validation of the Atomic Gravity Measurement-System Twin.

Development/calibration:
    Exail Run 11

Untouched validation:
    Exail Runs 12-20

NO per-run recalibration.

Tests:
1. TotalPhase -> inferred acceleration -> independent QA750 reference
2. Raw DetectData -> frozen detector transform/calibration -> reported Ratio
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd



from models.atom_interferometer.gravity_inference import infer_gravity
from models.atom_interferometer.atomic_detector import process_detection_file


BASE = Path(
    "data/raw/exail_bordeaux/extracted/Raw Data/"
    "Figure 3 & 5/20230317"
)

# Frozen Run-11 detector calibration
DETECTOR_GAIN = 1.270340537618991
DETECTOR_OFFSET = -0.14784050465880966

RUNS = range(12, 21)


def load_ratio(run, direction):

    path = (
        BASE
        / f"Raman/Run {run}"
        / f"Raman-Run{run}-Avg01-Ratios-{direction}.txt"
    )

    d = pd.read_csv(
        path,
        sep="\t",
        comment="#",
        header=None,
    )

    d.columns = [
        "Iteration",
        "Date",
        "Time",
        "Chirp",
        "Phase",
        "RamanAxis",
        "RTPhase",
        "NFringe",
        "Ratio",
    ]

    d["Direction"] = direction

    return d


def build_shots(run):

    ku = load_ratio(run, "kU")
    kd = load_ratio(run, "kD")

    d = (
        pd.concat([ku, kd])
        .sort_values("Iteration")
        .reset_index(drop=True)
    )

    d["TotalPhase"] = (
        2*np.pi*d["NFringe"]
        + d["RTPhase"]
    )

    d["direction_sign"] = (
        d["Direction"].map({
            "kU": +1.0,
            "kD": -1.0,
        })
    )

    return d


def build_stream(run):

    path = (
        BASE
        / "Streaming"
        / f"Run{run}_1.csv"
    )

    s = pd.read_csv(
        path,
        sep=";",
    )

    s["block"] = (
        s["NInterf"]
        .ne(s["NInterf"].shift())
        .cumsum()
    )

    blocks = (
        s[s["NInterf"] != 0]
        .groupby("block")
        .agg(
            NInterf=("NInterf", "first"),
            samples=("NInterf", "size"),
            accZ_mean=("acc Z", "mean"),
            accZ_std=("acc Z", "std"),
        )
        .reset_index(drop=True)
    )

    counts = (
        blocks["NInterf"]
        .value_counts()
    )

    blocks["block_count"] = (
        blocks["NInterf"]
        .map(counts)
    )

    # Same conservative acceptance rule used for Runs 11/12.
    clean = blocks[
        (blocks["block_count"] == 1)
        & (blocks["samples"] >= 100)
    ].copy()

    clean["Iteration"] = (
        clean["NInterf"].astype(int)
    )

    return blocks, clean


all_validation = []
summaries = []


for run in RUNS:

    print(f"Processing Run {run} ...")

    shots = build_shots(run)

    blocks, clean = build_stream(run)

    d = shots.merge(
        clean[
            [
                "Iteration",
                "samples",
                "accZ_mean",
                "accZ_std",
            ]
        ],
        on="Iteration",
        how="inner",
    )

    # =====================================================
    # PHASE / INFERENCE BRANCH
    # =====================================================

    g_est = []

    for _, row in d.iterrows():

        result = infer_gravity(
            total_phase=row["TotalPhase"],
            direction=row["direction_sign"],
            T=1.0e-2,
        )

        g_est.append(
            result["g_est"]
        )

    d["g_est"] = g_est

    d["g_reference"] = np.abs(
        d["accZ_mean"]
    )

    d["g_error"] = (
        d["g_est"]
        - d["g_reference"]
    )

    # =====================================================
    # DETECTOR BRANCH
    # =====================================================

    run_dir = (
        BASE
        / f"Raman/Run {run}"
    )

    ratio_pred = []
    ratio_raw = []

    for _, row in d.iterrows():

        iteration = int(
            row["Iteration"]
        )

        path = run_dir / (
            "Raman-DetectData-Avg01-"
            f"{iteration:04d}.txt"
        )

        detector = (
            process_detection_file(path)
        )

        raw = detector["ratio_raw"]

        pred = (
            DETECTOR_GAIN * raw
            + DETECTOR_OFFSET
        )

        ratio_raw.append(raw)
        ratio_pred.append(pred)

    d["ratio_raw"] = ratio_raw
    d["Ratio_pred"] = ratio_pred

    d["ratio_error"] = (
        d["Ratio"]
        - d["Ratio_pred"]
    )

    # =====================================================
    # METRICS
    # =====================================================

    acc_corr = (
        d["g_est"]
        .corr(d["g_reference"])
    )

    acc_mae = np.mean(
        np.abs(d["g_error"])
    )

    acc_rmse = np.sqrt(
        np.mean(d["g_error"]**2)
    )

    acc_bias = np.mean(
        d["g_error"]
    )

    ratio_corr = (
        d["Ratio"]
        .corr(d["Ratio_pred"])
    )

    ratio_mae = np.mean(
        np.abs(d["ratio_error"])
    )

    ratio_rmse = np.sqrt(
        np.mean(d["ratio_error"]**2)
    )

    ss_res = np.sum(
        d["ratio_error"]**2
    )

    ss_tot = np.sum(
        (
            d["Ratio"]
            - d["Ratio"].mean()
        )**2
    )

    detector_r2 = (
        1 - ss_res/ss_tot
    )

    summaries.append({
        "Run": run,
        "Raman_shots": len(shots),
        "Active_stream_blocks":
            len(blocks),
        "Usable_shots": len(d),

        "Acceleration_corr":
            acc_corr,

        "Acceleration_MAE":
            acc_mae,

        "Acceleration_RMSE":
            acc_rmse,

        "Acceleration_bias":
            acc_bias,

        "Detector_corr":
            ratio_corr,

        "Detector_R2":
            detector_r2,

        "Detector_MAE":
            ratio_mae,

        "Detector_RMSE":
            ratio_rmse,
    })

    d["Run"] = run

    all_validation.append(d)


summary = pd.DataFrame(
    summaries
)

combined = pd.concat(
    all_validation,
    ignore_index=True,
)


print()
print("=" * 110)
print("FROZEN RUN-11 TWIN — OUT-OF-SAMPLE RUNS 12-20")
print("=" * 110)

print()

display_cols = [
    "Run",
    "Usable_shots",
    "Acceleration_corr",
    "Acceleration_MAE",
    "Acceleration_bias",
    "Detector_R2",
    "Detector_MAE",
]

print(
    summary[display_cols]
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}",
    )
)


# ============================================================
# COMBINED VALIDATION
# ============================================================

combined_acc_corr = (
    combined["g_est"]
    .corr(
        combined["g_reference"]
    )
)

combined_acc_mae = np.mean(
    np.abs(
        combined["g_error"]
    )
)

combined_acc_rmse = np.sqrt(
    np.mean(
        combined["g_error"]**2
    )
)

combined_acc_bias = np.mean(
    combined["g_error"]
)


combined_detector_corr = (
    combined["Ratio"]
    .corr(
        combined["Ratio_pred"]
    )
)

combined_detector_mae = np.mean(
    np.abs(
        combined["ratio_error"]
    )
)

combined_detector_rmse = np.sqrt(
    np.mean(
        combined["ratio_error"]**2
    )
)

ss_res = np.sum(
    combined["ratio_error"]**2
)

ss_tot = np.sum(
    (
        combined["Ratio"]
        - combined["Ratio"].mean()
    )**2
)

combined_detector_r2 = (
    1 - ss_res/ss_tot
)


print()
print("=" * 70)
print("COMBINED OUT-OF-SAMPLE VALIDATION")
print("=" * 70)

print()
print(
    "Runs:",
    f"{min(RUNS)}-{max(RUNS)}"
)

print(
    "Total usable shots:",
    len(combined)
)

print()

print("PHASE / INFERENCE BRANCH")

print(
    "  correlation:",
    combined_acc_corr
)

print(
    "  MAE:",
    combined_acc_mae,
    "m/s^2"
)

print(
    "  RMSE:",
    combined_acc_rmse,
    "m/s^2"
)

print(
    "  bias:",
    combined_acc_bias,
    "m/s^2"
)

print()

print("DETECTOR / READOUT BRANCH")

print(
    "  correlation:",
    combined_detector_corr
)

print(
    "  R^2:",
    combined_detector_r2
)

print(
    "  MAE:",
    combined_detector_mae
)

print(
    "  RMSE:",
    combined_detector_rmse
)


summary.to_csv(
    "data/processed/"
    "exail_frozen_twin_multirun_summary.csv",
    index=False,
)

combined.to_csv(
    "data/processed/"
    "exail_frozen_twin_multirun_validation.csv",
    index=False,
)

print()
print("Saved:")
print(
    "  data/processed/"
    "exail_frozen_twin_multirun_summary.csv"
)
print(
    "  data/processed/"
    "exail_frozen_twin_multirun_validation.csv"
)
