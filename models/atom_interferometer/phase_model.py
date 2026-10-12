import numpy as np

# Rb-87 D2 transition, approximately 780 nm
LAMBDA_RB87 = 780.24e-9

def effective_wavevector(wavelength=LAMBDA_RB87):
    """Counter-propagating Raman effective wavevector."""
    return 4.0 * np.pi / wavelength


def interferometer_phase(acceleration, chirp_hz_s, T, wavelength=LAMBDA_RB87):
    """
    Ideal 3-pulse Mach-Zehnder atom-interferometer phase.
    """
    k_eff = effective_wavevector(wavelength)

    # Hz/s -> rad/s^2
    alpha = 2.0 * np.pi * chirp_hz_s

    return (k_eff * acceleration - alpha) * T**2


if __name__ == "__main__":
    T = 1.0e-2

    cases = [
        ("+a, +chirp", +9.77985287, +1.472810000e7),
        ("-a, +chirp", -9.77985287, +1.472810000e7),
        ("+a, -chirp", +9.77985287, -1.472810000e7),
        ("-a, -chirp", -9.77985287, -1.472810000e7),
    ]

    for name, a, chirp in cases:
        phi = interferometer_phase(a, chirp, T)

        print(
            name,
            "| phase =", phi,
            "| wrapped =", np.mod(phi, 2*np.pi)
        )
