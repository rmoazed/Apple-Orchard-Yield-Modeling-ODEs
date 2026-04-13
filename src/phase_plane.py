"""Generate the phase plane for the reduced orchard model."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


def reduced_system(t: float, y, A: float, B: float, K_M: float, U: float, a: float, d: float):
    """Reduced autonomous orchard system."""
    F, M = y
    dFdt = ((A * M / (K_M + M)) - B) * F
    dMdt = U - a * F * M - d * M
    return [dFdt, dMdt]


def main() -> None:
    # Reduced-model parameters from the paper
    A = 0.08
    B = 0.03
    K_M = 0.40
    U = 0.04
    a = 0.06
    d = 0.05

    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)

    # Vector field grid
    F_vals = np.linspace(0, 2.0, 20)
    M_vals = np.linspace(0, 2.0, 20)
    F_grid, M_grid = np.meshgrid(F_vals, M_vals)

    dF = ((A * M_grid / (K_M + M_grid)) - B) * F_grid
    dM = U - a * F_grid * M_grid - d * M_grid

    speed = np.sqrt(dF**2 + dM**2)
    speed[speed == 0] = 1
    dF_norm = dF / speed
    dM_norm = dM / speed

    # Equilibria
    F1 = 0
    M1 = U / d

    M2 = (B * K_M) / (A - B)
    F2 = (U * (A - B) - d * B * K_M) / (a * B * K_M)

    plt.figure(figsize=(8, 6))
    plt.quiver(F_grid, M_grid, dF_norm, dM_norm, angles="xy")

    plt.plot(F1, M1, "ro", label="E1")
    if F2 > 0 and M2 > 0:
        plt.plot(F2, M2, "bo", label="E2")

    # Representative trajectories
    initial_conditions = [
        [0.1, 0.2],
        [0.2, 1.2],
        [1.0, 0.3],
        [1.5, 1.5],
        [0.5, 0.8],
    ]

    t_span = (0, 200)
    t_eval = np.linspace(t_span[0], t_span[1], 1000)

    for i, y0 in enumerate(initial_conditions):
        sol = solve_ivp(
            lambda t, y: reduced_system(t, y, A=A, B=B, K_M=K_M, U=U, a=a, d=d),
            t_span,
            y0,
            t_eval=t_eval,
        )
        if i == 0:
            plt.plot(sol.y[0], sol.y[1], linewidth=1.5, label="Trajectories")
        else:
            plt.plot(sol.y[0], sol.y[1], linewidth=1.5)

    # Nullclines
    plt.axvline(0, color="green", linestyle="--", label="F-nullcline: F=0")

    if A > B:
        M_null = (B * K_M) / (A - B)
        plt.axhline(M_null, color="purple", linestyle="--", label=r"F-nullcline: M = BK_M/(A-B)")

    F_curve = np.linspace(0, 2.0, 400)
    M_curve = U / (a * F_curve + d)
    plt.plot(F_curve, M_curve, color="orange", linestyle="--", label="M-nullcline = U/(aF+d)")

    plt.xlabel("Fruit load F")
    plt.ylabel("Soil moisture M")
    plt.title("Phase Plane for Reduced Orchard Model")
    plt.xlim(0, 2.0)
    plt.ylim(0, 2.0)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(output_dir / "phase_plane.png", dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved phase plane to: {(output_dir / 'phase_plane.png').resolve()}")


if __name__ == "__main__":
    main()
