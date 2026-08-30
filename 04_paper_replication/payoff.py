"""
Payoff Functions for the Bayesian EV Charging Game.

This module implements the payoff structure used in:

    "Incorporating Bounded Rationality into Electric Vehicle
     Highway Charging Decisions: A Bayesian Game Analysis"

The module connects the EV charging environment developed in
Stage 03 with the Bayesian game developed in Stage 04.

Main components
---------------
1. Range anxiety payoff
2. Charging energy cost
3. Charging payoff
4. Expected queueing cost
5. No-charging payoff
6. Total payoff
7. Payoff difference
8. Threshold decision

The payoff structure is:

    Charge:
        Π_C = - charging_cost - expected_queueing_cost

    Do not charge:
        Π_NC = - range_anxiety_cost

The EV chooses Charge when:

    Π_C > Π_NC
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Optional

try:
    from range_anxiety import calculate_range_anxiety
except ImportError:
    from ..03_ev_charging_model.range_anxiety import (
        calculate_range_anxiety
    )

try:
    from expected_cost import (
        expected_queue_time_setting1,
        expected_queueing_cost,
    )
except ImportError:
    from .expected_cost import (
        expected_queue_time_setting1,
        expected_queueing_cost,
    )


# ============================================================
# 1. Payoff Parameters
# ============================================================

@dataclass(frozen=True)
class PayoffParameters:
    """
    Parameters required to calculate EV payoffs.

    Parameters
    ----------
    electricity_price : float
        Electricity price in CNY/kWh.

    waiting_cost_per_hour : float
        Driver-specific cost of waiting in CNY/hour.

    charging_power : float
        Charging power in kW.

    charging_piles : int
        Number of charging piles at the station.

    target_soc : float
        Target SoC after charging.

    n_evs : int
        Number of EVs participating in the charging game.

    existing_queue_time : float
        Existing queueing time in hours.

    safe_range : float
        Safe driving range in km.

    maximum_range : float
        Theoretical maximum driving range in km.

    anxiety_lambda : float
        Range-anxiety intensity parameter.

    anxiety_alpha : float
        Range-anxiety curvature parameter.
    """

    electricity_price: float
    waiting_cost_per_hour: float
    charging_power: float
    charging_piles: int
    target_soc: float
    n_evs: int
    existing_queue_time: float
    safe_range: float
    maximum_range: float
    anxiety_lambda: float
    anxiety_alpha: float

    def __post_init__(self) -> None:
        """Validate payoff parameters."""

        if self.electricity_price < 0:
            raise ValueError(
                "electricity_price cannot be negative."
            )

        if self.waiting_cost_per_hour < 0:
            raise ValueError(
                "waiting_cost_per_hour cannot be negative."
            )

        if self.charging_power <= 0:
            raise ValueError(
                "charging_power must be positive."
            )

        if self.charging_piles < 1:
            raise ValueError(
                "charging_piles must be at least 1."
            )

        if not 0.0 <= self.target_soc <= 1.0:
            raise ValueError(
                "target_soc must be between 0 and 1."
            )

        if self.n_evs < 1:
            raise ValueError(
                "n_evs must be at least 1."
            )

        if self.existing_queue_time < 0:
            raise ValueError(
                "existing_queue_time cannot be negative."
            )

        if self.safe_range <= 0:
            raise ValueError(
                "safe_range must be positive."
            )

        if self.maximum_range <= 0:
            raise ValueError(
                "maximum_range must be positive."
            )

        if self.anxiety_lambda < 0:
            raise ValueError(
                "anxiety_lambda cannot be negative."
            )

        if self.anxiety_alpha <= 0:
            raise ValueError(
                "anxiety_alpha must be positive."
            )


# ============================================================
# 2. State-of-Charge Thresholds
# ============================================================

def calculate_safe_soc(
    distance_to_station: float,
    safe_range: float,
) -> float:
    """
    Calculate the safe SoC threshold.

    Formula:

        SoC_s = d / d_s,      if d < d_s
        SoC_s = 1,            if d >= d_s

    Parameters
    ----------
    distance_to_station : float
        Distance to the next charging station in km.

    safe_range : float
        Safe driving range in km.

    Returns
    -------
    float
        Safe SoC threshold.
    """

    if distance_to_station < 0:
        raise ValueError(
            "distance_to_station cannot be negative."
        )

    if safe_range <= 0:
        raise ValueError(
            "safe_range must be positive."
        )

    if distance_to_station < safe_range:
        return distance_to_station / safe_range

    return 1.0


def calculate_danger_soc(
    distance_to_station: float,
    maximum_range: float,
) -> float:
    """
    Calculate the danger SoC threshold.

    Formula:

        SoC_d = d / d_0,      if d < d_0
        SoC_d = 1,            if d >= d_0

    Parameters
    ----------
    distance_to_station : float
        Distance to the next charging station in km.

    maximum_range : float
        Theoretical maximum driving range in km.

    Returns
    -------
    float
        Danger SoC threshold.
    """

    if distance_to_station < 0:
        raise ValueError(
            "distance_to_station cannot be negative."
        )

    if maximum_range <= 0:
        raise ValueError(
            "maximum_range must be positive."
        )

    if distance_to_station < maximum_range:
        return distance_to_station / maximum_range

    return 1.0


# ============================================================
# 3. Range Anxiety
# ============================================================

def range_anxiety_cost(
    soc: float,
    distance_to_station: float,
    safe_range: float,
    maximum_range: float,
    lambda_risk: float,
    alpha: float,
) -> float:
    """
    Calculate range anxiety cost.

    The model is:

        A_i = 0

            if SoC >= SoC_s

        A_i = lambda *
              (SoC_s - SoC)^alpha

            if SoC_d <= SoC < SoC_s

        A_i = infinity

            if SoC < SoC_d

    This function provides the payoff penalty associated with
    choosing not to charge.

    Parameters
    ----------
    soc : float
        Current SoC.

    distance_to_station : float
        Distance to next charging station.

    safe_range : float
        Safe driving range.

    maximum_range : float
        Maximum driving range.

    lambda_risk : float
        Range-anxiety intensity.

    alpha : float
        Curvature parameter.

    Returns
    -------
    float
        Range anxiety cost.
    """

    safe_soc = calculate_safe_soc(
        distance_to_station=distance_to_station,
        safe_range=safe_range,
    )

    danger_soc = calculate_danger_soc(
        distance_to_station=distance_to_station,
        maximum_range=maximum_range,
    )

    return calculate_range_anxiety(
        soc=soc,
        safe_soc=safe_soc,
        danger_soc=danger_soc,
        lambda_risk=lambda_risk,
        alpha=alpha,
    )


# ============================================================
# 4. Charging Energy
# ============================================================

def charging_energy(
    battery_capacity: float,
    soc: float,
    target_soc: float,
) -> float:
    """
    Calculate charging energy.

    Formula:

        E_i = V_i (SoC_t - SoC_i)

    with:

        E_i = 0

    if current SoC is already above target SoC.
    """

    if battery_capacity <= 0:
        raise ValueError(
            "battery_capacity must be positive."
        )

    if not 0.0 <= soc <= 1.0:
        raise ValueError(
            "soc must be between 0 and 1."
        )

    if not 0.0 <= target_soc <= 1.0:
        raise ValueError(
            "target_soc must be between 0 and 1."
        )

    return max(
        0.0,
        battery_capacity * (target_soc - soc),
    )


# ============================================================
# 5. Charging Cost
# ============================================================

def charging_cost(
    battery_capacity: float,
    soc: float,
    target_soc: float,
    electricity_price: float,
) -> float:
    """
    Calculate direct electricity cost.

    Formula:

        C_i = E_i P
    """

    if electricity_price < 0:
        raise ValueError(
            "electricity_price cannot be negative."
        )

    energy = charging_energy(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
    )

    return energy * electricity_price


# ============================================================
# 6. Charging Time
# ============================================================

def charging_time(
    battery_capacity: float,
    soc: float,
    target_soc: float,
    charging_power: float,
) -> float:
    """
    Calculate charging time.

    Formula:

        T_i = E_i / eta
    """

    if charging_power <= 0:
        raise ValueError(
            "charging_power must be positive."
        )

    energy = charging_energy(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
    )

    return energy / charging_power


# ============================================================
# 7. Expected Queueing Cost
# ============================================================

def queueing_cost(
    n_evs: int,
    decision_point: float,
    charging_piles: int,
    battery_capacity: float,
    target_soc: float,
    expected_soc: float,
    charging_power: float,
    waiting_cost_per_hour: float,
    existing_queue_time: float = 0.0,
) -> float:
    """
    Calculate expected queueing cost.

    This function connects payoff.py with expected_cost.py.

    Formula:

        E[t]
        =
        (E[c(N)] - 1)
        /
        (2k)
        *
        E[T]
        +
        t_0

    and:

        C_q = mu_q E[t]
    """

    expected_time = expected_queue_time_setting1(
        n_evs=n_evs,
        decision_point=decision_point,
        charging_piles=charging_piles,
        battery_capacity=battery_capacity,
        target_soc=target_soc,
        expected_soc=expected_soc,
        charging_power=charging_power,
        existing_queue_time=existing_queue_time,
    )

    return expected_queueing_cost(
        expected_queue_time=expected_time,
        waiting_cost_per_hour=waiting_cost_per_hour,
    )


# ============================================================
# 8. Charging Payoff
# ============================================================

def charging_payoff(
    battery_capacity: float,
    soc: float,
    target_soc: float,
    electricity_price: float,
    n_evs: int,
    decision_point: float,
    charging_piles: int,
    expected_soc: float,
    charging_power: float,
    waiting_cost_per_hour: float,
    existing_queue_time: float = 0.0,
) -> float:
    """
    Calculate payoff from choosing to charge.

    Formula:

        Pi_C
        =
        - C_i
        - E[C_q]

    where:

        C_i = charging cost

        E[C_q] = expected queueing cost
    """

    direct_cost = charging_cost(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
        electricity_price=electricity_price,
    )

    expected_waiting_cost = queueing_cost(
        n_evs=n_evs,
        decision_point=decision_point,
        charging_piles=charging_piles,
        battery_capacity=battery_capacity,
        target_soc=target_soc,
        expected_soc=expected_soc,
        charging_power=charging_power,
        waiting_cost_per_hour=waiting_cost_per_hour,
        existing_queue_time=existing_queue_time,
    )

    return (
        -direct_cost
        - expected_waiting_cost
    )


# ============================================================
# 9. No-Charging Payoff
# ============================================================

def no_charging_payoff(
    soc: float,
    distance_to_station: float,
    safe_range: float,
    maximum_range: float,
    lambda_risk: float,
    alpha: float,
) -> float:
    """
    Calculate payoff from choosing not to charge.

    Formula:

        Pi_NC = - A_i

    where A_i is range anxiety cost.

    If SoC is below the danger threshold:

        A_i = infinity

    and therefore:

        Pi_NC = -infinity
    """

    anxiety = range_anxiety_cost(
        soc=soc,
        distance_to_station=distance_to_station,
        safe_range=safe_range,
        maximum_range=maximum_range,
        lambda_risk=lambda_risk,
        alpha=alpha,
    )

    if anxiety == inf:
        return -inf

    return -anxiety


# ============================================================
# 10. Total Payoff
# ============================================================

def total_payoff(
    action: str,
    battery_capacity: float,
    soc: float,
    target_soc: float,
    electricity_price: float,
    distance_to_station: float,
    safe_range: float,
    maximum_range: float,
    lambda_risk: float,
    alpha: float,
    n_evs: int,
    decision_point: float,
    charging_piles: int,
    expected_soc: float,
    charging_power: float,
    waiting_cost_per_hour: float,
    existing_queue_time: float = 0.0,
) -> float:
    """
    Calculate payoff for a specified action.

    Accepted actions:

        "charge"
        "no_charge"

    Returns
    -------
    float
        Corresponding payoff.
    """

    normalized_action = action.lower().strip()

    if normalized_action in {
        "charge",
        "charging",
        "c",
    }:

        return charging_payoff(
            battery_capacity=battery_capacity,
            soc=soc,
            target_soc=target_soc,
            electricity_price=electricity_price,
            n_evs=n_evs,
            decision_point=decision_point,
            charging_piles=charging_piles,
            expected_soc=expected_soc,
            charging_power=charging_power,
            waiting_cost_per_hour=waiting_cost_per_hour,
            existing_queue_time=existing_queue_time,
        )

    if normalized_action in {
        "no_charge",
        "no charging",
        "do_not_charge",
        "do not charge",
        "nc",
    }:

        return no_charging_payoff(
            soc=soc,
            distance_to_station=distance_to_station,
            safe_range=safe_range,
            maximum_range=maximum_range,
            lambda_risk=lambda_risk,
            alpha=alpha,
        )

    raise ValueError(
        "action must be 'charge' or 'no_charge'."
    )


# ============================================================
# 11. Payoff Difference
# ============================================================

def payoff_difference(
    battery_capacity: float,
    soc: float,
    target_soc: float,
    electricity_price: float,
    distance_to_station: float,
    safe_range: float,
    maximum_range: float,
    lambda_risk: float,
    alpha: float,
    n_evs: int,
    decision_point: float,
    charging_piles: int,
    expected_soc: float,
    charging_power: float,
    waiting_cost_per_hour: float,
    existing_queue_time: float = 0.0,
) -> float:
    """
    Calculate the payoff advantage of charging.

    Formula:

        Delta Pi
        =
        Pi_C - Pi_NC

    Interpretation:

        Delta Pi > 0
            Charge is preferred.

        Delta Pi < 0
            Do not charge is preferred.

        Delta Pi = 0
            The EV is indifferent.
    """

    charge = charging_payoff(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
        electricity_price=electricity_price,
        n_evs=n_evs,
        decision_point=decision_point,
        charging_piles=charging_piles,
        expected_soc=expected_soc,
        charging_power=charging_power,
        waiting_cost_per_hour=waiting_cost_per_hour,
        existing_queue_time=existing_queue_time,
    )

    no_charge = no_charging_payoff(
        soc=soc,
        distance_to_station=distance_to_station,
        safe_range=safe_range,
        maximum_range=maximum_range,
        lambda_risk=lambda_risk,
        alpha=alpha,
    )

    if no_charge == -inf:
        return inf

    return charge - no_charge


# ============================================================
# 12. Best Response
# ============================================================

def best_response(
    **kwargs,
) -> str:
    """
    Determine the EV's preferred action.

    Returns
    -------
    str
        "charge" or "no_charge".
    """

    difference = payoff_difference(
        **kwargs
    )

    if difference > 0:
        return "charge"

    return "no_charge"


# ============================================================
# 13. Threshold Condition
# ============================================================

def is_charging_optimal(
    **kwargs,
) -> bool:
    """
    Return True if charging gives strictly higher payoff.
    """

    return (
        payoff_difference(**kwargs) > 0
    )


# ============================================================
# 14. Public API
# ============================================================

__all__ = [
    "PayoffParameters",
    "calculate_safe_soc",
    "calculate_danger_soc",
    "range_anxiety_cost",
    "charging_energy",
    "charging_cost",
    "charging_time",
    "queueing_cost",
    "charging_payoff",
    "no_charging_payoff",
    "total_payoff",
    "payoff_difference",
    "best_response",
    "is_charging_optimal",
]


# ============================================================
# 15. Standalone Module Check
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("BAYESIAN EV GAME — PAYOFF MODULE CHECK")
    print("=" * 70)

    # --------------------------------------------------------
    # Example parameters
    # --------------------------------------------------------

    battery_capacity = 80.0
    soc = 0.40
    target_soc = 0.80

    electricity_price = 0.30

    distance_to_station = 120.0

    safe_range = 160.0
    maximum_range = 400.0

    lambda_risk = 1.5
    alpha = 2.0

    n_evs = 10
    decision_point = 0.40

    charging_piles = 4
    expected_soc = 0.60

    charging_power = 50.0
    waiting_cost_per_hour = 20.0

    existing_queue_time = 0.0

    # --------------------------------------------------------
    # Thresholds
    # --------------------------------------------------------

    safe_soc = calculate_safe_soc(
        distance_to_station=distance_to_station,
        safe_range=safe_range,
    )

    danger_soc = calculate_danger_soc(
        distance_to_station=distance_to_station,
        maximum_range=maximum_range,
    )

    print("\n[SoC Thresholds]")

    print(
        f"Safe SoC:                 "
        f"{safe_soc:.4f}"
    )

    print(
        f"Danger SoC:               "
        f"{danger_soc:.4f}"
    )

    # --------------------------------------------------------
    # Range anxiety
    # --------------------------------------------------------

    anxiety = range_anxiety_cost(
        soc=soc,
        distance_to_station=distance_to_station,
        safe_range=safe_range,
        maximum_range=maximum_range,
        lambda_risk=lambda_risk,
        alpha=alpha,
    )

    print("\n[Range Anxiety]")

    print(
        f"Range anxiety cost:       "
        f"{anxiety:.6f}"
    )

    # --------------------------------------------------------
    # Charging
    # --------------------------------------------------------

    energy = charging_energy(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
    )

    time = charging_time(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
        charging_power=charging_power,
    )

    direct_cost = charging_cost(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
        electricity_price=electricity_price,
    )

    print("\n[Charging]")

    print(
        f"Charging energy:         "
        f"{energy:.2f} kWh"
    )

    print(
        f"Charging time:           "
        f"{time:.2f} hours"
    )

    print(
        f"Charging cost:           "
        f"{direct_cost:.4f} CNY"
    )

    # --------------------------------------------------------
    # Queue
    # --------------------------------------------------------

    expected_queue_cost = queueing_cost(
        n_evs=n_evs,
        decision_point=decision_point,
        charging_piles=charging_piles,
        battery_capacity=battery_capacity,
        target_soc=target_soc,
        expected_soc=expected_soc,
        charging_power=charging_power,
        waiting_cost_per_hour=waiting_cost_per_hour,
        existing_queue_time=existing_queue_time,
    )

    print("\n[Expected Queue]")

    print(
        f"Expected queueing cost:  "
        f"{expected_queue_cost:.4f} CNY"
    )

    # --------------------------------------------------------
    # Payoffs
    # --------------------------------------------------------

    charge_payoff = charging_payoff(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
        electricity_price=electricity_price,
        n_evs=n_evs,
        decision_point=decision_point,
        charging_piles=charging_piles,
        expected_soc=expected_soc,
        charging_power=charging_power,
        waiting_cost_per_hour=waiting_cost_per_hour,
        existing_queue_time=existing_queue_time,
    )

    no_charge_payoff_value = no_charging_payoff(
        soc=soc,
        distance_to_station=distance_to_station,
        safe_range=safe_range,
        maximum_range=maximum_range,
        lambda_risk=lambda_risk,
        alpha=alpha,
    )

    difference = (
        charge_payoff
        - no_charge_payoff_value
    )

    print("\n[Payoff]")

    print(
        f"Utility of charging:     "
        f"{charge_payoff:.6f}"
    )

    print(
        f"Utility of no charging:  "
        f"{no_charge_payoff_value:.6f}"
    )

    print(
        f"Payoff difference:        "
        f"{difference:.6f}"
    )

    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    decision = best_response(
        battery_capacity=battery_capacity,
        soc=soc,
        target_soc=target_soc,
        electricity_price=electricity_price,
        distance_to_station=distance_to_station,
        safe_range=safe_range,
        maximum_range=maximum_range,
        lambda_risk=lambda_risk,
        alpha=alpha,
        n_evs=n_evs,
        decision_point=decision_point,
        charging_piles=charging_piles,
        expected_soc=expected_soc,
        charging_power=charging_power,
        waiting_cost_per_hour=waiting_cost_per_hour,
        existing_queue_time=existing_queue_time,
    )

    print("\n[Decision]")

    if decision == "charge":
        print(
            "Preferred decision:     CHARGE"
        )
    else:
        print(
            "Preferred decision:     DO NOT CHARGE"
        )

    print("=" * 70)
