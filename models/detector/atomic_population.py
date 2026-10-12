"""
Atomic Gravity Twin v1.2A
Independent two-channel atomic-population detector.

Forward response and inverse recovery.

This is a simplified calibrated observation model,
not a reconstruction of a particular instrument.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class DetectorCalibration:
    gain_1: float = 0.92
    gain_2: float = 0.87
    cross_12: float = 0.015
    cross_21: float = 0.020
    background_1: float = 20.0
    background_2: float = 25.0
    read_noise: float = 5.0

    def matrix(self):
        return np.array([
            [self.gain_1, self.cross_12],
            [self.cross_21, self.gain_2]
        ], dtype=float)

    def background(self):
        return np.array([
            self.background_1,
            self.background_2
        ], dtype=float)


class AtomicPopulationDetector:

    def __init__(self, calibration, seed=42):
        self.calibration = calibration
        self.rng = np.random.default_rng(seed)

        G = calibration.matrix()

        if np.linalg.det(G) == 0:
            raise ValueError("Detector matrix is singular")

    def forward(self, populations, atom_count=6000):
        """
        Convert underlying state populations into
        simulated two-channel detector observations.
        """

        p = np.asarray(populations, dtype=float)

        if p.shape != (2,):
            raise ValueError("Expected two populations")

        if np.any(p < 0) or not np.isclose(p.sum(), 1):
            raise ValueError("Invalid population probabilities")

        n1 = self.rng.binomial(atom_count, p[0])
        n = np.array([n1, atom_count - n1], dtype=float)

        G = self.calibration.matrix()
        b = self.calibration.background()

        mean_signal = G @ n + b

        if np.any(mean_signal < 0):
            raise ValueError("Negative detector signal mean")

        # Simplified independent counting and read noise.
        shot_noise = self.rng.normal(
            0.0,
            np.sqrt(mean_signal)
        )

        read_noise = self.rng.normal(
            0.0,
            self.calibration.read_noise,
            size=2
        )

        observed = (
            mean_signal + shot_noise + read_noise
        )

        return {
            "true_counts": n,
            "mean_signal": mean_signal,
            "observed": observed
        }

    def inverse(self, observed):
        """
        Recover state counts using known calibration.

        Negative estimates are retained for diagnostics;
        no silent clipping is performed.
        """

        y = np.asarray(observed, dtype=float)

        G = self.calibration.matrix()
        b = self.calibration.background()

        recovered = np.linalg.solve(G, y-b)

        total = recovered.sum()

        if total <= 0:
            raise ValueError("Non-positive recovered atom total")

        return {
            "recovered_counts": recovered,
            "recovered_populations": recovered / total
        }
