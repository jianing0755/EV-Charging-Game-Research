"""
Expected Cost and Congestion Model for Bayesian EV Charging Game.

This module implements the expected charging probability,
expected number of charging EVs, expected queueing time,
and expected queueing cost used in the Bayesian game.

The implementation follows the mathematical structure described
in:

    "Incorporating Bounded Rationality into Electric Vehicle
     Highway Charging Decisions: A Bayesian Game Analysis"

The module is designed to work with Stage 04:
    Paper Replication

and builds conceptually on Stage 03:
    EV Charging Model
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Mapping, Optional


# ============================================================
# 1. Basic Distribution Utilities
# ============================================================

def uniform_cdf(soc: float) -> float:
    """
    CDF of a Uniform[0, 1] State-of-Charge distribution.

    Parameters
    ----------
    soc : float
        State of charge in normalized form [0, 1].

    Returns
    -------
    float
        Probability that SoC <= soc.

    Notes
    -----
    The paper assumes a uniform SoC distribution:

        SoC ~ U(0, 1)

    Therefore:

        F(SoC) = SoC

    within the valid interval.
    """

    if soc <= 0.0:
        return 0.0

    if soc >= 1.0:
        return 1.0

    return soc


def charging_probability(
    decision_point: float,
    cdf: Callable[[float], float] = uniform_cdf,
) -> float:
    """
    Calculate the probability that another EV chooses to charge.

    The threshold strategy is:

        Charge if SoC < decision_point
        Do not charge otherwise

    Therefore:

        p_i = F(decision_point)

    Parameters
    ----------
    decision_point : float
        Charging decision threshold.

    cdf : callable, optional
        CDF of the private SoC distribution.

    Returns
    -------
    float
        Probability of charging.
    """

    if not 0.0 <= decision_point <= 1.0:
        raise ValueError(
            "decision_point must be between 0 and 1."
        )

    probability = cdf(decision_point)

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "CDF must return a probability between 0 and 1."
        )

    return probability


# ============================================================
# 2. Expected Number of Charging EVs
# ============================================================

def expected_charging_count(
    n_evs: int,
    charging_probability_value: float,
    focal_ev_included: bool = True,
) -> float:
    """
    Calculate the expected number of charging EVs.

    For Setting 1, the paper uses the self-referencing formulation:

        E[c(N)] = 1 + (N - 1) p_i

    where the focal EV is assumed to be charging.

    Parameters
    ----------
    n_evs : int
        Total number of EVs.

    charging_probability_value : float
        Probability that another EV chooses to charge.

    focal_ev_included : bool, default=True
        If True, the focal EV is counted as one charging EV.

    Returns
    -------
    float
        Expected number of charging EVs.

    Examples
    --------
    For N = 10 and p = 0.4:

        E[c(N)] = 1 + 9 * 0.4
                = 4.6
    """

    if n_evs < 1:
        raise ValueError("n_evs must be at least 1.")

    if not 0.0 <= charging_probability_value <= 1.0:
        raise ValueError(
            "charging_probability_value must be between 0 and 1."
        )

    if focal_ev_included:
        return 1.0 + (n_evs - 1) * charging_probability_value

    return n_evs * charging_probability_value


def expected_other_charging_count(
    n_evs: int,
    charging_probability_value: float,
) -> float:
    """
    Calculate the expected number of charging EVs other than
    the focal EV.

    Formula:

        E[c_others] = (N - 1) p_i
    """

    if n_evs < 1:
        raise ValueError("n_evs must be at least 1.")

    if not 0.0 <= charging_probability_value <= 1.0:
        raise ValueError(
            "charging_probability_value must be between 0 and 1."
        )

    return (n_evs - 1) * charging_probability_value


# ============================================================
# 3. Expected Charging Energy
# ============================================================

def expected_charging_energy(
    battery_capacity: float,
    target_soc: float,
    expected_soc: float,
) -> float:
    """
    Calculate expected charging energy for a representative EV.

    Formula:

        E[E_i] = V * (SoC_t - E[SoC])

    Parameters
    ----------
    battery_capacity : float
        Battery capacity in kWh.

    target_soc : float
        Target SoC.

    expected_soc : float
        Expected initial SoC.

    Returns
    -------
    float
        Expected charging energy in kWh.
    """

    if battery_capacity < 0:
        raise ValueError(
            "battery_capacity must be non-negative."
        )

    if not 0.0 <= target_soc <= 1.0:
        raise ValueError(
            "target_soc must be between 0 and 1."
        )

    if not 0.0 <= expected_soc <= 1.0:
        raise ValueError(
            "expected_soc must be between 0 and 1."
        )

    energy = battery_capacity * (
        target_soc - expected_soc
    )

    return max(0.0, energy)


def expected_charging_time(
    battery_capacity: float,
    target_soc: float,
    expected_soc: float,
    charging_power: float,
) -> float:
    """
    Calculate expected charging time.

    Formula:

        E[T]
        =
        V * (SoC_t - E[SoC]) / eta

    Parameters
    ----------
    battery_capacity : float
        Battery capacity in kWh.

    target_soc : float
        Target SoC.

    expected_soc : float
        Expected initial SoC.

    charging_power : float
        Charging power in kW.

    Returns
    -------
    float
        Expected charging time in hours.
    """

    if charging_power <= 0:
        raise ValueError(
            "charging_power must be greater than zero."
        )

    energy = expected_charging_energy(
        battery_capacity=battery_capacity,
        target_soc=target_soc,
        expected_soc=expected_soc,
    )

    return energy / charging_power


# ============================================================
# 4. Setting 1 — Self-Referencing Expected Queue
# ============================================================

def expected_queue_time_setting1(
    n_evs: int,
    decision_point: float,
    charging_piles: int,
    battery_capacity: float,
    target_soc: float,
    expected_soc: float,
    charging_power: float,
    existing_queue_time: float = 0.0,
) -> float:
    """
    Calculate expected queueing time for Setting 1.

    In Setting 1, EVs do not know the destination distribution
    of other EVs and use self-referencing.

    The paper's formulation is:

        E[c(N)]
        =
        1 + (N - 1)p_i

    and:

        E[t]
        =
        (E[c(N)] - 1)
        / (2k)
        *
        E[V(SoC_t - SoC)] / eta
        + t_0

    Parameters
    ----------
    n_evs : int
        Total number of EVs.

    decision_point : float
        Focal EV's charging threshold.

    charging_piles : int
        Number of charging piles.

    battery_capacity : float
        Battery capacity in kWh.

    target_soc : float
        Target SoC.

    expected_soc : float
        Expected SoC of other EVs.

    charging_power : float
        Charging power in kW.

    existing_queue_time : float, default=0.0
        Queueing time generated by EVs already waiting.

    Returns
    -------
    float
        Expected queueing time in hours.
    """

    if charging_piles < 1:
        raise ValueError(
            "charging_piles must be at least 1."
        )

    if existing_queue_time < 0:
        raise ValueError(
            "existing_queue_time cannot be negative."
        )

    probability = charging_probability(
        decision_point
    )

    expected_count = expected_charging_count(
        n_evs=n_evs,
        charging_probability_value=probability,
        focal_ev_included=True,
    )

    expected_time = expected_charging_time(
        battery_capacity=battery_capacity,
        target_soc=target_soc,
        expected_soc=expected_soc,
        charging_power=charging_power,
    )

    queue_time = (
        (expected_count - 1.0)
        / (2.0 * charging_piles)
        * expected_time
        + existing_queue_time
    )

    return max(0.0, queue_time)


# ============================================================
# 5. Setting 2 — Destination-Specific Expected Queue
# ============================================================

@dataclass(frozen=True)
class DestinationGroup:
    """
    Destination-specific EV group.

    Parameters
    ----------
    name : str
        Destination identifier.

    n_evs : int
        Number of EVs associated with this destination.

    decision_point : float
        Charging threshold for this destination.

    battery_capacity : float
        Representative battery capacity in kWh.

    expected_soc : float
        Expected SoC of EVs in this destination group.
    """

    name: str
    n_evs: int
    decision_point: float
    battery_capacity: float
    expected_soc: float


def expected_charging_count_setting2(
    destination_groups: Iterable[DestinationGroup],
    focal_destination: str,
) -> float:
    """
    Calculate expected charging count under Setting 2.

    For an EV traveling toward destination k':

        E[c(N)]
        =
        sum_{k != k'} N_k p_i^k
        +
        (N_{k'} - 1)p_i^{k'}
        +
        1

    The focal EV is assumed to be charging.

    Parameters
    ----------
    destination_groups : iterable of DestinationGroup
        Destination groups and their charging thresholds.

    focal_destination : str
        Destination of the focal EV.

    Returns
    -------
    float
        Expected total number of charging EVs.
    """

    groups = list(destination_groups)

    if not groups:
        raise ValueError(
            "destination_groups cannot be empty."
        )

    names = {group.name for group in groups}

    if focal_destination not in names:
        raise ValueError(
            "focal_destination is not present in destination_groups."
        )

    total_expected = 1.0

    for group in groups:
        probability = charging_probability(
            group.decision_point
        )

        if group.name == focal_destination:
            total_expected += (
                (group.n_evs - 1)
                * probability
            )
        else:
            total_expected += (
                group.n_evs
                * probability
            )

    return total_expected


def expected_queue_time_setting2(
    destination_groups: Iterable[DestinationGroup],
    focal_destination: str,
    charging_piles: int,
    target_soc: float,
    charging_power: float,
    existing_queue_time: float = 0.0,
) -> float:
    """
    Calculate expected queueing time under Setting 2.

    The expected number of charging EVs is destination-specific.

    The expected charging time is computed from the destination
    groups' representative battery capacities and expected SoCs.

    Parameters
    ----------
    destination_groups : iterable of DestinationGroup
        Destination-specific EV groups.

    focal_destination : str
        Destination of the focal EV.

    charging_piles : int
        Number of charging piles.

    target_soc : float
        Target SoC.

    charging_power : float
        Charging power in kW.

    existing_queue_time : float, default=0.0
        Existing queueing time in hours.

    Returns
    -------
    float
        Expected queueing time in hours.
    """

    if charging_piles < 1:
        raise ValueError(
            "charging_piles must be at least 1."
        )

    if charging_power <= 0:
        raise ValueError(
            "charging_power must be greater than zero."
        )

    if existing_queue_time < 0:
        raise ValueError(
            "existing_queue_time cannot be negative."
        )

    groups = list(destination_groups)

    expected_count = expected_charging_count_setting2(
        destination_groups=groups,
        focal_destination=focal_destination,
    )

    total_weight = 0.0
    weighted_charging_time = 0.0

    for group in groups:

        probability = charging_probability(
            group.decision_point
        )

        expected_time = expected_charging_time(
            battery_capacity=group.battery_capacity,
            target_soc=target_soc,
            expected_soc=group.expected_soc,
            charging_power=charging_power,
        )

        weight = group.n_evs * probability

        total_weight += weight
        weighted_charging_time += (
            weight * expected_time
        )

    if total_weight > 0:
        average_charging_time = (
            weighted_charging_time
            / total_weight
        )
    else:
        average_charging_time = 0.0

    queue_time = (
        (expected_count - 1.0)
        / (2.0 * charging_piles)
        * average_charging_time
        + existing_queue_time
    )

    return max(0.0, queue_time)


# ============================================================
# 6. Expected Queueing Cost
# ============================================================

def expected_queueing_cost(
    expected_queue_time: float,
    waiting_cost_per_hour: float,
) -> float:
    """
    Calculate expected queueing cost.

    Formula:

        C_q = mu_q * E[t]

    Parameters
    ----------
    expected_queue_time : float
        Expected queueing time in hours.

    waiting_cost_per_hour : float
        Driver's waiting cost in CNY/hour.

    Returns
    -------
    float
        Expected queueing cost in CNY.
    """

    if expected_queue_time < 0:
        raise ValueError(
            "expected_queue_time cannot be negative."
        )

    if waiting_cost_per_hour < 0:
        raise ValueError(
            "waiting_cost_per_hour cannot be negative."
        )

    return (
        waiting_cost_per_hour
        * expected_queue_time
    )


def expected_queueing_cost_setting1(
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
    Convenience function for Setting 1.

    Returns expected queueing cost directly.
    """

    queue_time = expected_queue_time_setting1(
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
        expected_queue_time=queue_time,
        waiting_cost_per_hour=waiting_cost_per_hour,
    )


def expected_queueing_cost_setting2(
    destination_groups: Iterable[DestinationGroup],
    focal_destination: str,
    charging_piles: int,
    target_soc: float,
    charging_power: float,
    waiting_cost_per_hour: float,
    existing_queue_time: float = 0.0,
) -> float:
    """
    Convenience function for Setting 2.

    Returns expected queueing cost directly.
    """

    queue_time = expected_queue_time_setting2(
        destination_groups=destination_groups,
        focal_destination=focal_destination,
        charging_piles=charging_piles,
        target_soc=target_soc,
        charging_power=charging_power,
        existing_queue_time=existing_queue_time,
    )

    return expected_queueing_cost(
        expected_queue_time=queue_time,
        waiting_cost_per_hour=waiting_cost_per_hour,
    )


# ============================================================
# 7. General Utility Functions
# ============================================================

def queue_time_to_minutes(
    queue_time_hours: float,
) -> float:
    """
    Convert queueing time from hours to minutes.
    """

    if queue_time_hours < 0:
        raise ValueError(
            "queue_time_hours cannot be negative."
        )

    return queue_time_hours * 60.0


def queue_minutes_to_hours(
    queue_minutes: float,
) -> float:
    """
    Convert queueing time from minutes to hours.
    """

    if queue_minutes < 0:
        raise ValueError(
            "queue_minutes cannot be negative."
        )

    return queue_minutes / 60.0


# ============================================================
# 8. Public API
# ============================================================

__all__ = [
    "DestinationGroup",
    "uniform_cdf",
    "charging_probability",
    "expected_charging_count",
    "expected_other_charging_count",
    "expected_charging_energy",
    "expected_charging_time",
    "expected_queue_time_setting1",
    "expected_charging_count_setting2",
    "expected_queue_time_setting2",
    "expected_queueing_cost",
    "expected_queueing_cost_setting1",
    "expected_queueing_cost_setting2",
    "queue_time_to_minutes",
    "queue_minutes_to_hours",
]


# ============================================================
# 9. Basic Standalone Check
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("EXPECTED COST MODULE CHECK")
    print("=" * 70)

    # Example parameters based on the paper's model.
    n_evs = 10
    decision_point = 0.40
    charging_piles = 4

    battery_capacity = 60.0
    target_soc = 1.0
    expected_soc = 0.60

    charging_power = 50.0
    waiting_cost = 30.0

    probability = charging_probability(
        decision_point
    )

    count = expected_charging_count(
        n_evs=n_evs,
        charging_probability_value=probability,
    )

    expected_time = expected_charging_time(
        battery_capacity=battery_capacity,
        target_soc=target_soc,
        expected_soc=expected_soc,
        charging_power=charging_power,
    )

    queue_time = expected_queue_time_setting1(
        n_evs=n_evs,
        decision_point=decision_point,
        charging_piles=charging_piles,
        battery_capacity=battery_capacity,
        target_soc=target_soc,
        expected_soc=expected_soc,
        charging_power=charging_power,
    )

    queue_cost = expected_queueing_cost(
        expected_queue_time=queue_time,
        waiting_cost_per_hour=waiting_cost,
    )

    print(f"Decision point:             {decision_point:.4f}")
    print(f"Charging probability:       {probability:.4f}")
    print(f"Expected charging EVs:      {count:.4f}")
    print(f"Expected charging time:     {expected_time:.4f} hours")
    print(f"Expected queueing time:     {queue_time:.4f} hours")
    print(
        f"Expected queueing time:     "
        f"{queue_time_to_minutes(queue_time):.2f} minutes"
    )
    print(f"Expected queueing cost:     {queue_cost:.4f} CNY")

    print("=" * 70)
