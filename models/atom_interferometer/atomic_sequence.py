"""
Atomic-interferometer adaptation of the modelling sequence used in
srikarr20/detector-plane-imaging.

DPI:
    field -> interaction -> propagation -> interference -> detector observable

Atomic adaptation:
    atomic state -> pi/2 -> evolution -> pi -> evolution -> pi/2
    -> output-state populations

This is the first ideal two-state model.
Detector response/noise is deliberately NOT included yet.
"""

import numpy as np
from .phase_model import interferometer_phase


def output_populations(phi):
    """
    Ideal two-output-port Mach-Zehnder atom interferometer.

    Returns normalized populations:
        P_F1 + P_F2 = 1
    """

    p_f2 = 0.5 * (1.0 + np.cos(phi))
    p_f1 = 1.0 - p_f2

    return p_f1, p_f2


def run_atomic_sequence(
    acceleration,
    chirp_hz_s,
    T,
    direction=1.0,
):
    """
    Atomic equivalent of the DPI forward-measurement sequence.

    Parameters
    ----------
    acceleration : float
        Acceleration magnitude in m/s^2.

    chirp_hz_s : float
        Raman chirp rate in Hz/s.

    T : float
        Pulse separation in seconds.

    direction : float
        +1 for kU
        -1 for kD
    """

    # --------------------------------
    # PHYSICAL EVOLUTION / PHASE LAYER
    # --------------------------------

    phi = interferometer_phase(
        acceleration=direction * acceleration,
        chirp_hz_s=direction * chirp_hz_s,
        T=T,
    )

    # --------------------------------
    # INTERFERENCE / MEASUREMENT LAYER
    # --------------------------------

    p_f1, p_f2 = output_populations(phi)

    return {
        "phase": phi,
        "phase_wrapped": np.mod(phi, 2*np.pi),
        "P_F1": p_f1,
        "P_F2": p_f2,
    }


if __name__ == "__main__":

    T = 1.0e-2
    acceleration = 9.77985287
    chirp = 1.472810000e7

    for name, direction in [
        ("kU", +1.0),
        ("kD", -1.0),
    ]:

        result = run_atomic_sequence(
            acceleration=acceleration,
            chirp_hz_s=chirp,
            T=T,
            direction=direction,
        )

        print()
        print(name)
        print("phase:", result["phase"])
        print("wrapped:", result["phase_wrapped"])
        print("P_F1:", result["P_F1"])
        print("P_F2:", result["P_F2"])
