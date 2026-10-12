"""
Atomic detector/readout adaptation of the detector-processing concept
used in srikarr20/detector-plane-imaging.

DPI:
    physical signal -> detector sampling -> noise/background -> observable

Atomic adaptation:
    fluorescence waveform -> cursor integration -> background subtraction
    -> normalization -> population observable

IMPORTANT:
The normalization below is empirically reconstructed from Exail Run 11.
It is not claimed to be Exail's documented proprietary implementation.
"""

import numpy as np


# Detection windows from Exail Run 11 Parameters.txt
CURSORS = [
    (8, 56),       # W1
    (160, 212),    # W2
    (985, 1029),   # W3
    (1137, 1183),  # W4
]


def integrate_windows(data, channel=1):
    """
    Integrate one detector channel over the four configured windows.

    channel=1 corresponds to C2 in our previous analysis
    because NumPy indexing starts at zero.
    """

    values = []

    for start, end in CURSORS:
        values.append(
            np.sum(data[start:end, channel])
        )

    return np.asarray(values)


def population_observable(window_sums):
    """
    Empirically reconstructed population observable.

    Best Run-11 candidate:

        (W1 - W3) / (W2 - W4)

    This reproduced the experimental Ratio with
    correlation ~0.996 in exploratory validation.
    """

    W1, W2, W3, W4 = window_sums

    denominator = W2 - W4

    if np.isclose(denominator, 0):
        return np.nan

    return (W1 - W3) / denominator


def process_detection_file(path):
    """
    Raw Exail DetectData file -> reconstructed population observable.
    """

    data = np.loadtxt(path, comments="#")

    windows = integrate_windows(
        data,
        channel=1
    )

    ratio_raw = population_observable(windows)

    return {
        "W1": windows[0],
        "W2": windows[1],
        "W3": windows[2],
        "W4": windows[3],
        "ratio_raw": ratio_raw,
    }
