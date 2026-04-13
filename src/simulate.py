"""Run full-model orchard simulations and save plots."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

from model import OrchardParams, orchard_system


def constant_func(value: float) -> Callable[[float], float]:
    """Return a constant forcing function."""
    return lambda t: value


def freeze_event_temperature(t: float, baseline: float = 70.0, freeze_temp: float = 25.0) -> float:
    """Temperature with a short freeze event during days 40-42."""
    if 40 <= t <= 42:
        return freeze_temp
    return baseline


def solve_scenario(
    params: OrchardParams,
    T_func: Callable[[float], float],
    R_func: Callable[[float], float],
    I_func: Callable[[float], float],
    L_func: Callable[[float], float],
    P_func: Callable[[float], float],
    y0: tuple[float, float] = (0.30, 0.60),
    t_span: tuple[float, float] = (0.0, 120.0),
    n_points: int = 1000,
):
    """Solve the full orchard model for a given scenario."""
    t_eval = np.linspace(t_span[0], t_span[1], n_points)
    sol = solve_ivp(
        fun=lambda t, y: orchard_system(t, y, params, T_func, R_func, I_func, L_func, P_func),
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(f"Solver failed: {sol.message}")
    return sol


def plot_solution(sol, title: str, output_path: Path) -> None:
    """Plot fruit and moisture trajectories."""
    plt.figure(figsize=(10, 5))
    plt.plot(sol.t, sol.y[0], label="Fruit load F(t)")
    plt.plot(sol.t, sol.y[1], label="Soil moisture M(t)")
    plt.xlabel("Time (days)")
    plt.ylabel("Relative fruit/moisture level")
    plt.title(title)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)

    # Baseline scenario
    baseline_params = OrchardParams(
        r=0.10,
        K_M=0.40,
        alpha=0.04,
        beta=0.03,
        K_L=0.50,
        gamma=0.08,
        a=0.08,
        b=0.002,
        c=0.03,
        T_min=55.0,
        T_max=85.0,
        T_f=28.0,
        m1=0.01,
        m2=0.01,
    )
    baseline_sol = solve_scenario(
        params=baseline_params,
        T_func=constant_func(70.0),
        R_func=constant_func(0.05),
        I_func=constant_func(0.03),
        L_func=constant_func(0.80),
        P_func=constant_func(0.10),
    )
    plot_solution(
        baseline_sol,
        "Baseline Orchard Dynamics",
        output_dir / "baseline_simulation.png",
    )

    # Freeze scenario
    freeze_sol = solve_scenario(
        params=baseline_params,
        T_func=lambda t: freeze_event_temperature(t, baseline=70.0, freeze_temp=25.0),
        R_func=constant_func(0.05),
        I_func=constant_func(0.03),
        L_func=constant_func(0.80),
        P_func=constant_func(0.10),
    )
    plot_solution(
        freeze_sol,
        "Orchard Dynamics Under a Short Freeze Event",
        output_dir / "freeze_simulation.png",
    )

    # Severe labor shortage scenario
    labor_params = OrchardParams(
        r=0.10,
        K_M=0.40,
        alpha=0.04,
        beta=0.10,  # stronger labor penalty during a critical season stage
        K_L=0.50,
        gamma=0.08,
        a=0.10,
        b=0.002,
        c=0.003,
        T_min=55.0,
        T_max=85.0,
        T_f=28.0,
        m1=0.01,
        m2=0.01,
    )
    labor_sol = solve_scenario(
        params=labor_params,
        T_func=constant_func(70.0),
        R_func=constant_func(0.10),
        I_func=constant_func(0.10),
        L_func=constant_func(0.01),
        P_func=constant_func(0.10),
    )
    plot_solution(
        labor_sol,
        "Orchard Dynamics Under Severe Labor Shortage",
        output_dir / "labor_shortage_simulation.png",
    )

    print(f"Saved simulation figures to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
