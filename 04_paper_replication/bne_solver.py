"""
Bayesian Nash Equilibrium Solver for the EV Charging Game.

Paper
-----
"Incorporating Bounded Rationality into Electric Vehicle
Highway Charging Decisions: A Bayesian Game Analysis"

This module implements the threshold-based Bayesian Nash
equilibrium calculation for the EV charging game.

The solver connects:

    type_distribution.py
            ↓
    expected_cost.py
            ↓
    payoff.py
            ↓
    Bayesian best response
            ↓
    equilibrium threshold

The basic strategy is:

    Charge if SoC < theta
    Do not charge if SoC >= theta

where theta is the equilibrium charging threshold.

The equilibrium condition is:

    theta = BR(theta)

where BR(theta) is the best-response threshold generated
by the beliefs induced by theta.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from type_distribution import (
    PAPER_SOC_MIN,
    PAPER_SOC_MAX,
    expected_soc,
    charging_probability_from_threshold,
)

from payoff import (
    charging_payoff,
    no_charging_payoff,
    payoff_difference,
)


# ============================================================
# 1. Bayesian Game Parameters
# ============================================================

@dataclass(frozen=True)
class BNEParameters:
    """
    Parameters used by the Bayesian game solver.

    Parameters
    ----------
    n_evs : int
        Number of EVs participating in the game.

    battery_capacity : float
        EV battery capacity in kWh.

    target_soc : float
        Target SoC after charging.

    electricity_price : float
        Electricity price in CNY/kWh.

    distance_to_station : float
        Distance to the next charging station in km.

    safe_range : float
        Safe driving range in km.

    maximum_range : float
        Maximum driving range in km.

    lambda_risk : float
        Range-anxiety intensity parameter.

    alpha : float
        Range-anxiety curvature parameter.

    charging_piles : int
        Number of charging piles.

    charging_power : float
        Charging power in kW.

    waiting_cost_per_hour : float
        Driver waiting cost in CNY/hour.

    existing_queue_time : float
        Existing queueing time in hours.

    soc_min : float
        Lower bound of the initial SoC distribution.

    soc_max : float
        Upper bound of the initial SoC distribution.

    """

    n_evs: int
    battery_capacity: float
    target_soc: float
    electricity_price: float
    distance_to_station: float
    safe_range: float
    maximum_range: float
    lambda_risk: float
    alpha: float
    charging_piles: int
    charging_power: float
    waiting_cost_per_hour: float
    existing_queue_time: float = 0.0
    soc_min: float = PAPER_SOC_MIN
    soc_max: float = PAPER_SOC_MAX

    def __post_init__(self) -> None:
        """Validate model parameters."""

        if self.n_evs < 1:
            raise ValueError(
                "n_evs must be at least 1."
            )

        if self.battery_capacity <= 0:
            raise ValueError(
                "battery_capacity must be positive."
            )

        if not 0.0 <= self.target_soc <= 1.0:
            raise ValueError(
                "target_soc must be between 0 and 1."
            )

        if self.electricity_price < 0:
            raise ValueError(
                "electricity_price cannot be negative."
            )

        if self.distance_to_station < 0:
            raise ValueError(
                "distance_to_station cannot be negative."
            )

        if self.safe_range <= 0:
            raise ValueError(
                "safe_range must be positive."
            )

        if self.maximum_range <= 0:
            raise ValueError(
                "maximum_range must be positive."
            )

        if self.lambda_risk < 0:
            raise ValueError(
                "lambda_risk cannot be negative."
            )

        if self.alpha <= 0:
            raise ValueError(
                "alpha must be positive."
            )

        if self.charging_piles < 1:
            raise ValueError(
                "charging_piles must be at least 1."
            )

        if self.charging_power <= 0:
            raise ValueError(
                "charging_power must be positive."
            )

        if self.waiting_cost_per_hour < 0:
            raise ValueError(
                "waiting_cost_per_hour cannot be negative."
            )

        if self.existing_queue_time < 0:
            raise ValueError(
                "existing_queue_time cannot be negative."
            )

        if not 0.0 <= self.soc_min < self.soc_max <= 1.0:
            raise ValueError(
                "soc_min and soc_max must satisfy "
                "0 <= soc_min < soc_max <= 1."
            )


# ============================================================
# 2. BNE Result
# ============================================================

@dataclass(frozen=True)
class BNEResult:
    """
    Result returned by the Bayesian Nash equilibrium solver.

    Attributes
    ----------
    threshold : float
        Equilibrium SoC threshold.

    charging_probability : float
        Probability that a randomly selected EV charges.

    expected_charging_evs : float
        Expected number of charging EVs.

    converged : bool
        Whether the numerical search converged.

    iterations : int
        Number of iterations used.

    residual : float
        Absolute difference between the final threshold and
        the best-response threshold.
    """

    threshold: float
    charging_probability: float
    expected_charging_evs: float
    converged: bool
    iterations: int
    residual: float


# ============================================================
# 3. Strategy Probability
# ============================================================

def charging_probability(
    threshold: float,
    soc_min: float = PAPER_SOC_MIN,
    soc_max: float = PAPER_SOC_MAX,
) -> float:
    """
    Calculate the probability of charging under a threshold
    strategy.

    Strategy:

        Charge if SoC < threshold.

    For:

        SoC ~ U(soc_min, soc_max)

    the charging probability is:

        P(C)
        =
        (theta - soc_min)
        /
        (soc_max - soc_min)

    with clipping to [0, 1].
    """

    return charging_probability_from_threshold(
        decision_point=threshold,
        lower_soc=soc_min,
        upper_soc=soc_max,
    )


# ============================================================
# 4. Expected Number of Charging EVs
# ============================================================

def expected_charging_evs(
    n_evs: int,
    threshold: float,
    soc_min: float = PAPER_SOC_MIN,
    soc_max: float = PAPER_SOC_MAX,
) -> float:
    """
    Calculate expected number of charging EVs.

    Formula:

        E[c(N)] = N * P(C)

    """

    if n_evs < 1:
        raise ValueError(
            "n_evs must be at least 1."
        )

    probability = charging_probability(
        threshold=threshold,
        soc_min=soc_min,
        soc_max=soc_max,
    )

    return n_evs * probability


# ============================================================
# 5. Expected Type of Other EVs
# ============================================================

def expected_other_soc(
    threshold: float,
    soc_min: float = PAPER_SOC_MIN,
    soc_max: float = PAPER_SOC_MAX,
) -> float:
    """
    Calculate the expected SoC of the EV population.

    For a uniform distribution:

        E[SoC]
        =
        (soc_min + soc_max) / 2

    This represents the baseline expectation used by the
    numerical replication.

    The threshold determines the charging probability, while
    the unconditional distribution determines the expected
    private type.
    """

    if not soc_min <= threshold <= soc_max:
        threshold = max(
            soc_min,
            min(threshold, soc_max),
        )

    return expected_soc(
        lower=soc_min,
        upper=soc_max,
    )


# ============================================================
# 6. Expected Payoff of a Type
# ============================================================

def type_payoffs(
    soc: float,
    threshold: float,
    parameters: BNEParameters,
) -> tuple[float, float]:
    """
    Calculate the two action payoffs for a specific private
    type.

    Returns
    -------
    charge_payoff : float
        Payoff from charging.

    no_charge_payoff : float
        Payoff from not charging.
    """

    expected_n = expected_charging_evs(
        n_evs=parameters.n_evs,
        threshold=threshold,
        soc_min=parameters.soc_min,
        soc_max=parameters.soc_max,
    )

    # The expected number is used to construct the expected
    # congestion level faced by the representative EV.
    #
    # Since the EV itself is making the decision, remove one
    # expected player from the congestion calculation.

    expected_other_chargers = max(
        0.0,
        expected_n - charging_probability(
            threshold=threshold,
            soc_min=parameters.soc_min,
            soc_max=parameters.soc_max,
        ),
    )

    # Convert expected other chargers back into an effective
    # population size for the queue model.
    effective_n_evs = max(
        1,
        round(
            expected_other_chargers
            + 1.0
        ),
    )

    # Expected SoC used by expected_cost.py.
    mean_soc = expected_other_soc(
        threshold=threshold,
        soc_min=parameters.soc_min,
        soc_max=parameters.soc_max,
    )

    charge = charging_payoff(
        battery_capacity=parameters.battery_capacity,
        soc=soc,
        target_soc=parameters.target_soc,
        electricity_price=parameters.electricity_price,
        n_evs=effective_n_evs,
        decision_point=threshold,
        charging_piles=parameters.charging_piles,
        expected_soc=mean_soc,
        charging_power=parameters.charging_power,
        waiting_cost_per_hour=parameters.waiting_cost_per_hour,
        existing_queue_time=parameters.existing_queue_time,
    )

    no_charge = no_charging_payoff(
        soc=soc,
        distance_to_station=parameters.distance_to_station,
        safe_range=parameters.safe_range,
        maximum_range=parameters.maximum_range,
        lambda_risk=parameters.lambda_risk,
        alpha=parameters.alpha,
    )

    return charge, no_charge


# ============================================================
# 7. Best Response at a Given Type
# ============================================================

def best_response_at_type(
    soc: float,
    threshold: float,
    parameters: BNEParameters,
) -> str:
    """
    Calculate the best response of an EV with a given SoC.

    Returns:

        "charge"

    or:

        "no_charge"
    """

    charge, no_charge = type_payoffs(
        soc=soc,
        threshold=threshold,
        parameters=parameters,
    )

    if charge > no_charge:
        return "charge"

    return "no_charge"


# ============================================================
# 8. Find Best-Response Threshold
# ============================================================

def find_best_response_threshold(
    threshold: float,
    parameters: BNEParameters,
    grid_size: int = 1001,
) -> float:
    """
    Search for the SoC at which the EV becomes indifferent
    between charging and not charging.

    The threshold solves approximately:

        Pi_C(theta, SoC)
        =
        Pi_NC(SoC)

    The search is performed on a dense SoC grid.

    Parameters
    ----------
    threshold : float
        Current population strategy threshold.

    parameters : BNEParameters
        Bayesian game parameters.

    grid_size : int
        Number of SoC points used in the search.

    Returns
    -------
    float
        Best-response threshold.
    """

    if grid_size < 10:
        raise ValueError(
            "grid_size must be at least 10."
        )

    step = (
        parameters.soc_max
        - parameters.soc_min
    ) / (grid_size - 1)

    best_soc = parameters.soc_min

    smallest_gap = float("inf")

    for i in range(grid_size):

        soc = (
            parameters.soc_min
            + i * step
        )

        charge, no_charge = type_payoffs(
            soc=soc,
            threshold=threshold,
            parameters=parameters,
        )

        if no_charge == float("-inf"):
            gap = float("inf")
        else:
            gap = abs(
                charge - no_charge
            )

        if gap < smallest_gap:

            smallest_gap = gap
            best_soc = soc

    return best_soc


# ============================================================
# 9. Fixed-Point Iteration
# ============================================================

def solve_bne(
    parameters: BNEParameters,
    initial_threshold: float = 0.50,
    tolerance: float = 1e-4,
    max_iterations: int = 100,
    grid_size: int = 1001,
) -> BNEResult:
    """
    Solve for the Bayesian Nash equilibrium threshold.

    The solver uses the fixed-point condition:

        theta* = BR(theta*)

    Algorithm
    ---------
    1. Start from an initial threshold.
    2. Calculate the best-response threshold.
    3. Compare old and new thresholds.
    4. Update the threshold.
    5. Repeat until convergence.

    Parameters
    ----------
    parameters : BNEParameters
        Bayesian game parameters.

    initial_threshold : float
        Initial threshold guess.

    tolerance : float
        Convergence tolerance.

    max_iterations : int
        Maximum number of iterations.

    grid_size : int
        Grid resolution for best-response search.

    Returns
    -------
    BNEResult
        Equilibrium result.
    """

    if not (
        parameters.soc_min
        <= initial_threshold
        <= parameters.soc_max
    ):
        raise ValueError(
            "initial_threshold must lie within "
            "[soc_min, soc_max]."
        )

    if tolerance <= 0:
        raise ValueError(
            "tolerance must be positive."
        )

    if max_iterations < 1:
        raise ValueError(
            "max_iterations must be at least 1."
        )

    threshold = initial_threshold

    residual = float("inf")

    for iteration in range(
        1,
        max_iterations + 1,
    ):

        new_threshold = find_best_response_threshold(
            threshold=threshold,
            parameters=parameters,
            grid_size=grid_size,
        )

        residual = abs(
            new_threshold - threshold
        )

        threshold = new_threshold

        if residual <= tolerance:

            probability = charging_probability(
                threshold=threshold,
                soc_min=parameters.soc_min,
                soc_max=parameters.soc_max,
            )

            expected_n = (
                parameters.n_evs
                * probability
            )

            return BNEResult(
                threshold=threshold,
                charging_probability=probability,
                expected_charging_evs=expected_n,
                converged=True,
                iterations=iteration,
                residual=residual,
            )

    probability = charging_probability(
        threshold=threshold,
        soc_min=parameters.soc_min,
        soc_max=parameters.soc_max,
    )

    expected_n = (
        parameters.n_evs
        * probability
    )

    return BNEResult(
        threshold=threshold,
        charging_probability=probability,
        expected_charging_evs=expected_n,
        converged=False,
        iterations=max_iterations,
        residual=residual,
    )


# ============================================================
# 10. Multiple Initial Conditions
# ============================================================

def solve_from_multiple_initial_thresholds(
    parameters: BNEParameters,
    initial_thresholds: Optional[List[float]] = None,
    tolerance: float = 1e-4,
    max_iterations: int = 100,
    grid_size: int = 1001,
) -> List[BNEResult]:
    """
    Solve the equilibrium from multiple initial thresholds.

    This is useful for checking whether the numerical solution
    is robust to the initial guess.

    If no initial thresholds are supplied, the default values
    are:

        0.20
        0.40
        0.60
        0.80

    """

    if initial_thresholds is None:

        initial_thresholds = [
            0.20,
            0.40,
            0.60,
            0.80,
        ]

    results = []

    for initial_threshold in initial_thresholds:

        result = solve_bne(
            parameters=parameters,
            initial_threshold=initial_threshold,
            tolerance=tolerance,
            max_iterations=max_iterations,
            grid_size=grid_size,
        )

        results.append(result)

    return results


# ============================================================
# 11. Equilibrium Verification
# ============================================================

def verify_equilibrium(
    result: BNEResult,
    parameters: BNEParameters,
    tolerance: float = 1e-3,
) -> bool:
    """
    Verify that the reported threshold approximately satisfies
    the fixed-point condition.

    The equilibrium condition is:

        |BR(theta*) - theta*| < tolerance
    """

    best_response = find_best_response_threshold(
        threshold=result.threshold,
        parameters=parameters,
    )

    return (
        abs(
            best_response
            - result.threshold
        )
        <= tolerance
    )


# ============================================================
# 12. Public API
# ============================================================

__all__ = [
    "BNEParameters",
    "BNEResult",
    "charging_probability",
    "expected_charging_evs",
    "expected_other_soc",
    "type_payoffs",
    "best_response_at_type",
    "find_best_response_threshold",
    "solve_bne",
    "solve_from_multiple_initial_thresholds",
    "verify_equilibrium",
]


# ============================================================
# 13. Standalone Solver
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("BAYESIAN NASH EQUILIBRIUM SOLVER")
    print("=" * 70)

    # --------------------------------------------------------
    # Paper-style baseline parameters
    # --------------------------------------------------------

    parameters = BNEParameters(
        n_evs=10,
        battery_capacity=80.0,
        target_soc=0.80,
        electricity_price=0.30,
        distance_to_station=120.0,
        safe_range=160.0,
        maximum_range=400.0,
        lambda_risk=1.5,
        alpha=2.0,
        charging_piles=4,
        charging_power=50.0,
        waiting_cost_per_hour=20.0,
        existing_queue_time=0.0,
    )

    print("\n[Game Parameters]")

    print(
        f"Number of EVs:             "
        f"{parameters.n_evs}"
    )

    print(
        f"Battery capacity:          "
        f"{parameters.battery_capacity:.2f} kWh"
    )

    print(
        f"Target SoC:                "
        f"{parameters.target_soc:.2f}"
    )

    print(
        f"Electricity price:         "
        f"{parameters.electricity_price:.2f} CNY/kWh"
    )

    print(
        f"Charging piles:             "
        f"{parameters.charging_piles}"
    )

    print(
        f"Charging power:             "
        f"{parameters.charging_power:.2f} kW"
    )

    print(
        f"SoC distribution:           "
        f"U({parameters.soc_min:.2f}, "
        f"{parameters.soc_max:.2f})"
    )

    # --------------------------------------------------------
    # Initial threshold
    # --------------------------------------------------------

    initial_threshold = 0.50

    print("\n[Initial Strategy]")

    print(
        f"Initial threshold:          "
        f"{initial_threshold:.4f}"
    )

    initial_probability = charging_probability(
        threshold=initial_threshold,
        soc_min=parameters.soc_min,
        soc_max=parameters.soc_max,
    )

    print(
        f"Initial charging probability: "
        f"{initial_probability:.4f}"
    )

    print(
    f"Initial expected chargers: "
    f"{expected_charging_evs(parameters.n_evs, initial_threshold, parameters.soc_min, parameters.soc_max):.4f}"
)
    # --------------------------------------------------------
    # BNE solution
    # --------------------------------------------------------

    print("\n[Equilibrium Search]")

    result = solve_bne(
        parameters=parameters,
        initial_threshold=initial_threshold,
        tolerance=1e-3,
        max_iterations=50,
        grid_size=501,
    )

    print(
        f"Equilibrium threshold:     "
        f"{result.threshold:.4f}"
    )

    print(
        f"Charging probability:       "
        f"{result.charging_probability:.4f}"
    )

    print(
        f"Expected charging EVs:      "
        f"{result.expected_charging_evs:.4f}"
    )

    print(
        f"Iterations:                 "
        f"{result.iterations}"
    )

    print(
        f"Residual:                   "
        f"{result.residual:.6f}"
    )

    print(
        f"Converged:                  "
        f"{result.converged}"
    )

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    verified = verify_equilibrium(
        result=result,
        parameters=parameters,
        tolerance=1e-2,
    )

    print("\n[Equilibrium Verification]")

    if verified:
        print(
            "BNE verification:           PASS"
        )
    else:
        print(
            "BNE verification:           FAIL"
        )

    # --------------------------------------------------------
    # Multiple starting points
    # --------------------------------------------------------

    print("\n[Robustness Check]")

    results = solve_from_multiple_initial_thresholds(
        parameters=parameters,
        initial_thresholds=[
            0.20,
            0.40,
            0.60,
            0.80,
        ],
        tolerance=1e-3,
        max_iterations=50,
        grid_size=501,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"Initial condition {index}: "
            f"threshold={result.threshold:.4f}, "
            f"probability="
            f"{result.charging_probability:.4f}, "
            f"converged="
            f"{result.converged}"
        )

    print("=" * 70)

