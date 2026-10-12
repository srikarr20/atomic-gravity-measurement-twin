"""
Determine whether temporal structure inside the marked QA750
acceleration blocks explains phase-model residual magnitude.

NO new physical model is imposed yet.

Frozen validation runs: 12-20.
"""

from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(
    "data/raw/exail_bordeaux/extracted/Raw Data/"
    "Figure 3 & 5/20230317"
)

VALIDATION = pd.read_csv(
    "data/processed/"
    "exail_frozen_twin_multirun_validation.csv"
)

records = []


for run in range(12, 21):

    print("Processing Run", run)

    stream_path = (
        BASE
        / "Streaming"
        / f"Run{run}_1.csv"
    )

    s = pd.read_csv(
        stream_path,
        sep=";"
    )

    s["block"] = (
        s["NInterf"]
        .ne(s["NInterf"].shift())
        .cumsum()
    )

    active = s[
        s["NInterf"] != 0
    ].copy()

    # Identify unique contiguous blocks
    block_info = (
        active.groupby("block")
        .agg(
            NInterf=("NInterf", "first"),
            samples=("NInterf", "size"),
        )
        .reset_index()
    )

    counts = (
        block_info["NInterf"]
        .value_counts()
    )

    block_info["count"] = (
        block_info["NInterf"]
        .map(counts)
    )

    good = block_info[
        (block_info["count"] == 1)
        & (block_info["samples"] >= 100)
    ]

    for _, b in good.iterrows():

        block_id = b["block"]

        x = (
            active[
                active["block"] == block_id
            ]["acc Z"]
            .to_numpy()
        )

        iteration = int(
            b["NInterf"]
        )

        # Normalize block length conceptually
        # by splitting into quarters.
        sections = np.array_split(
            x,
            4
        )

        means = [
            np.mean(q)
            for q in sections
        ]

        stds = [
            np.std(q)
            for q in sections
        ]

        # Temporal shape descriptors
        first_half = np.mean(
            x[:len(x)//2]
        )

        second_half = np.mean(
            x[len(x)//2:]
        )

        slope = np.polyfit(
            np.arange(len(x)),
            x,
            1
        )[0]

        records.append({
            "Run": run,
            "Iteration": iteration,

            "wave_mean":
                np.mean(x),

            "wave_std":
                np.std(x),

            "q1_mean": means[0],
            "q2_mean": means[1],
            "q3_mean": means[2],
            "q4_mean": means[3],

            "q1_std": stds[0],
            "q2_std": stds[1],
            "q3_std": stds[2],
            "q4_std": stds[3],

            "half_difference":
                second_half-first_half,

            "wave_slope":
                slope,

            "wave_range":
                np.max(x)-np.min(x),
        })


wave = pd.DataFrame(records)

d = VALIDATION.merge(
    wave,
    on=["Run", "Iteration"],
    how="inner"
)

d["abs_error"] = np.abs(
    d["g_error"]
)


print()
print("=" * 76)
print("WAVEFORM / RESIDUAL DIAGNOSTICS")
print("=" * 76)

print("Shots:", len(d))


features = [
    "wave_std",
    "q1_std",
    "q2_std",
    "q3_std",
    "q4_std",
    "half_difference",
    "wave_slope",
    "wave_range",
]


print()
print("=== CORRELATION WITH |ERROR| ===")

results = []

for feature in features:

    corr = d[feature].corr(
        d["abs_error"]
    )

    results.append(
        (feature, corr)
    )

for name, corr in sorted(
    results,
    key=lambda x: abs(x[1]),
    reverse=True
):

    print(
        f"{name:20s}",
        f"{corr: .6f}"
    )


print()
print("=== HIGH vs LOW VIBRATION ===")

median_std = d["wave_std"].median()

low = d[
    d["wave_std"] <= median_std
]

high = d[
    d["wave_std"] > median_std
]

print(
    "Median waveform std:",
    median_std
)

print(
    "Low-vibration shots:",
    len(low),
    "MAE =",
    low["abs_error"].mean()
)

print(
    "High-vibration shots:",
    len(high),
    "MAE =",
    high["abs_error"].mean()
)


print()
print("=== QUARTILE EXTREMES ===")

q25 = d["wave_std"].quantile(0.25)
q75 = d["wave_std"].quantile(0.75)

lowest = d[
    d["wave_std"] <= q25
]

highest = d[
    d["wave_std"] >= q75
]

print(
    "Lowest 25% vibration MAE:",
    lowest["abs_error"].mean()
)

print(
    "Highest 25% vibration MAE:",
    highest["abs_error"].mean()
)

print(
    "Error amplification:",
    highest["abs_error"].mean()
    / lowest["abs_error"].mean()
)


OUT = (
    "data/processed/"
    "exail_waveform_residual_diagnostics.csv"
)

d.to_csv(
    OUT,
    index=False
)

print()
print("Saved:", OUT)
