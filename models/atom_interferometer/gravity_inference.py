"""
Atomic-gravity adaptation of the continuous parameter-recovery
pattern used in srkarr20/qms-platform Pyxel detector twin.

QMS/Pyxel:
    unknown parameter
      -> forward model
      -> compare prediction with observation
      -> minimize residual
      -> recovered parameter

Atomic adaptation:
    unknown g
      -> interferometer phase model
      -> compare with measured TotalPhase
      -> minimize residual
      -> recovered g
"""

import numpy as np
from scipy.optimize import minimize_scalar


LAMBDA_RB87 = 780.24e-9
K_EFF = 4.0 * np.pi / LAMBDA_RB87


def predict_phase(g, direction, T):
    """
    Simplified inertial-phase forward model.

    direction:
        +1 = kU
        -1 = kD
    """
    return direction * K_EFF * g * T**2


def infer_gravity(total_phase, direction, T=1.0e-2):
    """
    Blind continuous recovery of g from one measured phase.

    The optimizer receives TotalPhase, direction and T.
    It does NOT receive the QA750 acceleration measurement.
    """

    def objective(g):
        predicted = predict_phase(
            g=g,
            direction=direction,
            T=T,
        )

        return (predicted - total_phase) ** 2

    result = minimize_scalar(
        objective,
        bounds=(9.0, 10.5),
        method="bounded",
        options={
            "xatol": 1e-12
        },
    )

    return {
        "g_est": result.x,
        "objective": result.fun,
        "success": result.success,
        "evaluations": result.nfev,
    }
