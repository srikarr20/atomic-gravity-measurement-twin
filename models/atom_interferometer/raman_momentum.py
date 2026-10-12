"""
Atomic Gravity Twin v3.1G
Physical-wavevector Raman interaction in a
reduced two-state momentum basis.

This is a local interaction propagator.
It does not implement Hannover's full sequence.
"""

import numpy as np

HBAR = 1.054571817e-34
M = 1.44316060e-25
K = 4*np.pi/780.24e-9

def blackman(u):
    if u < 0 or u > 1:
        return 0.0
    return (
        0.42
        -0.5*np.cos(2*np.pi*u)
        +0.08*np.cos(4*np.pi*u)
    )

def propagate_raman(
    duration=60e-6,
    area=np.pi,
    detuning=0.0,
    steps=600
):
    """
    Two-level momentum-coupled propagation.

    Basis:
        |1,p>
        |2,p+hbar*K>

    detuning is angular frequency in rad/s.
    """
    dt = duration/steps

    omega_recoil = HBAR*K*K/(2*M)

    # Two-level state
    psi = np.array([1+0j, 0+0j])

    for i in range(steps):
        t = (i+0.5)*dt
        u = t/duration

        omega = (
            area*blackman(u)/(0.42*duration)
        )

        # Effective detuning includes recoil.
        delta = detuning-omega_recoil

        R = np.sqrt(omega**2+delta**2)

        if R == 0:
            continue

        c = np.cos(R*dt/2)
        s = np.sin(R*dt/2)

        H = np.array([
            [-delta, omega],
            [omega, delta]
        ], dtype=complex)/R

        U = c*np.eye(2)-1j*s*H

        psi = U@psi

    return {
        "P1": abs(psi[0])**2,
        "P2": abs(psi[1])**2,
        "norm": np.vdot(psi, psi).real,
        "recoil_rad_s": omega_recoil
    }
