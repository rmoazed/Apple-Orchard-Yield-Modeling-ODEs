"""Core orchard model functions.

This module defines the full apple orchard model used for time-dependent simulations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

Number = float


@dataclass(frozen=True)
class OrchardParams:
    """Parameters for the full orchard model."""

    # Fruit equation
    r: Number = 0.10
    K_M: Number = 0.40
    alpha: Number = 0.04
    beta: Number = 0.03
    K_L: Number = 0.50
    gamma: Number = 0.08

    # Moisture equation
    a: Number = 0.08
    b: Number = 0.002
    c: Number = 0.03

    # Temperature thresholds
    T_min: Number = 55.0
    T_max: Number = 85.0
    T_f: Number = 28.0

    # Temperature penalty slopes
    m1: Number = 0.01
    m2: Number = 0.01


def moisture_support(M: Number, K_M: Number) -> Number:
    """Saturating normalized moisture effect: M / (K_M + M)."""
    return M / (K_M + M)


def labor_penalty(L: Number, K_L: Number) -> Number:
    """Labor shortage penalty, high when labor is low."""
    return K_L / (K_L + L)


def temp_support(T: Number, T_min: Number, T_max: Number, m1: Number, m2: Number) -> Number:
    """Temperature support function.

    Returns 1 in the ideal temperature range and decreases linearly outside it.
    """
    if T < T_min:
        val = 1 - m1 * (T_min - T)
    elif T <= T_max:
        val = 1.0
    else:
        val = 1 - m2 * (T - T_max)
    return max(val, 0.0)


def freeze_penalty(T: Number, T_f: Number) -> Number:
    """Freeze penalty: zero above the threshold, positive below it."""
    if T >= T_f:
        return 0.0
    return T_f - T


def orchard_system(
    t: Number,
    y: Sequence[Number],
    params: OrchardParams,
    T_func: Callable[[Number], Number],
    R_func: Callable[[Number], Number],
    I_func: Callable[[Number], Number],
    L_func: Callable[[Number], Number],
    P_func: Callable[[Number], Number],
) -> list[Number]:
    """Full orchard model.

    Parameters
    ----------
    t : float
        Time.
    y : sequence[float]
        Current state [F, M].
    params : OrchardParams
        Model parameters.
    T_func, R_func, I_func, L_func, P_func : callables
        External forcing functions.
    """
    F, M = y

    # Keep the system numerically well-behaved.
    F = max(F, 0.0)
    M = max(M, 0.0)

    T = T_func(t)
    R = R_func(t)
    I = I_func(t)
    L = L_func(t)
    P = P_func(t)

    phi_M = moisture_support(M, params.K_M)
    psi_T = temp_support(T, params.T_min, params.T_max, params.m1, params.m2)
    ell_L = labor_penalty(L, params.K_L)
    s_T = freeze_penalty(T, params.T_f)

    dFdt = (
        params.r * phi_M * psi_T * F
        - params.alpha * P * F
        - params.beta * ell_L * F
        - params.gamma * s_T * F
    )

    dMdt = (
        R + I
        - params.a * F * M
        - params.b * T * M
        - params.c * M
    )

    return [dFdt, dMdt]
