```python
"""
Private Type and Distribution Model for the Bayesian EV Charging Game.

This module defines the private-information distributions used in
the paper replication.

Paper:
    "Incorporating Bounded Rationality into Electric Vehicle
     Highway Charging Decisions: A Bayesian Game Analysis"

The main private information considered in the Bayesian game is
the EV's State of Charge (SoC).

The module also provides destination-group structures required by
Setting 2, where EVs know the destination distribution of other EVs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

import random


# ============================================================
# 1. Basic Distribution Functions
# ============================================================

def soc_pdf(soc: float) -> float:
    """
    Probability density function of the paper's SoC distribution.

    The paper assumes:

        SoC ~ U(0, 1)

    Therefore:

        f(SoC) = 1,    0 <= SoC <= 1
        f(SoC) = 0,    otherwise

    Parameters
    ----------
    soc : float
        Normalized state of charge.

    Returns
    -------
    float
        Probability density.
    """

    if 0.0 <= soc <= 1.0:
        return 1.0

    return 0.0


def soc_cdf(soc: float) -> float:
    """
    Cumulative distribution function of SoC ~ U(0, 1).

    Formula:

        F(soc) = soc

    for 0 <= soc <= 1.

    Parameters
    ----------
    soc : float
        Normalized state of charge.

    Returns
    -------
    float
        Probability that SoC <= soc.
    """

    if soc <= 0.0:
        return 0.0

    if soc >= 1.0:
        return 1.0

    return soc


def soc_probability(
    lower: float,
    upper: float,
) -> float:
    """
    Calculate:

        P(lower <= SoC <= upper)

    under:

        SoC ~ U(0, 1)

    Formula:

        P = upper - lower
    """

    if not 0.0 <= lower <= 1.0:
        raise ValueError(
            "lower must be between 0 and 1."
        )

    if not 0.0 <= upper <= 1.0:
        raise ValueError(
            "upper must be between 0 and 1."
        )

    if lower > upper:
        raise ValueError(
            "lower cannot be greater than upper."
        )

    return soc_cdf(upper) - soc_cdf(lower)


# ============================================================
# 2. Expected SoC
# ============================================================

def expected_soc(
    lower: float = 0.0,
    upper: float = 1.0,
) -> float:
    """
    Calculate the expected SoC under a uniform distribution.

    For:

        SoC ~ U(lower, upper)

    the expectation is:

        E[SoC] = (lower + upper) / 2

    Parameters
    ----------
    lower : float
        Lower bound.

    upper : float
        Upper bound.

    Returns
    -------
    float
        Expected normalized SoC.
    """

    if not 0.0 <= lower <= 1.0:
        raise ValueError(
            "lower must be between 0 and 1."
        )

    if not 0.0 <= upper <= 1.0:
        raise ValueError(
            "upper must be between 0 and 1."
        )

    if lower > upper:
        raise ValueError(
            "lower cannot be greater than upper."
        )

    return (lower + upper) / 2.0


# ============================================================
# 3. Private EV Type
# ============================================================

@dataclass(frozen=True)
class EVType:
    """
    Private type of an EV driver.

    The private type contains the EV and driver characteristics
    needed by the Bayesian charging model.

    Parameters
    ----------
    soc : float
        Current State of Charge.

    battery_capacity : float
        Battery capacity in kWh.

    lambda_risk : float
        Range-anxiety / loss-aversion parameter.

    alpha : float
        Curvature parameter of the range-anxiety function.

    mu_a : float
        Range-anxiety cost coefficient.

    mu_q : float
        Queueing / waiting cost coefficient in CNY/hour.

    target_soc : float
        Target SoC after charging.

    distance_to_station : float
        Distance to the next charging station in km.

    safe_range : float
        Absolutely safe driving range in km.

    maximum_range : float
        Theoretical maximum driving range in km.
    """

    soc: float
    battery_capacity: float
    lambda_risk: float
    alpha: float
    mu_a: float
    mu_q: float
    target_soc: float
    distance_to_station: float
    safe_range: float
    maximum_range: float

    def __post_init__(self) -> None:
        """Validate private-type parameters."""

        if not 0.0 <= self.soc <= 1.0:
            raise ValueError(
                "soc must be between 0 and 1."
            )

        if self.battery_capacity <= 0:
            raise ValueError(
                "battery_capacity must be positive."
            )

        if self.lambda_risk < 0:
            raise ValueError(
                "lambda_risk cannot be negative."
            )

        if self.alpha <= 0:
            raise ValueError(
                "alpha must be positive."
            )

        if self.mu_a < 0:
            raise ValueError(
                "mu_a cannot be negative."
            )

        if self.mu_q < 0:
            raise ValueError(
                "mu_q cannot be negative."
            )

        if not 0.0 <= self.target_soc <= 1.0:
            raise ValueError(
                "target_soc must be between 0 and 1."
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


# ============================================================
# 4. Paper Parameter Defaults
# ============================================================

PAPER_ALPHA = 2.0

PAPER_LAMBDA = 1.5

PAPER_MU_Q = 30.0

PAPER_MU_A = 3000.0

PAPER_TARGET_SOC = 1.0

PAPER_BATTERY_CAPACITIES = (
    40.0,
    60.0,
    80.0,
    100.0,
)

PAPER_SOC_MIN = 0.20

PAPER_SOC_MAX = 1.00

PAPER_MAX_RANGE_MEAN = 600.0

PAPER_MAX_RANGE_STD = 50.0

PAPER_SAFE_RANGE_MEAN = 400.0

PAPER_SAFE_RANGE_STD = 50.0


# ============================================================
# 5. Random Sampling Utilities
# ============================================================

def sample_soc(
    rng: Optional[random.Random] = None,
    lower: float = PAPER_SOC_MIN,
    upper: float = PAPER_SOC_MAX,
) -> float:
    """
    Sample an EV's initial SoC.

    The paper's simulation uses:

        SoC ~ U(20%, 100%)

    Parameters
    ----------
    rng : random.Random, optional
        Random number generator.

    lower : float
        Lower SoC bound.

    upper : float
        Upper SoC bound.

    Returns
    -------
    float
        Sampled SoC.
    """

    if not 0.0 <= lower <= 1.0:
        raise ValueError(
            "lower must be between 0 and 1."
        )

    if not 0.0 <= upper <= 1.0:
        raise ValueError(
            "upper must be between 0 and 1."
        )

    if lower > upper:
        raise ValueError(
            "lower cannot be greater than upper."
        )

    generator = rng if rng is not None else random

    return generator.uniform(lower, upper)


def sample_battery_capacity(
    rng: Optional[random.Random] = None,
) -> float:
    """
    Sample an EV battery capacity.

    The paper considers:

        V_i ∈ {40, 60, 80, 100} kWh.

    A discrete uniform distribution is used for simulation
    unless a different empirical distribution is specified.
    """

    generator = rng if rng is not None else random

    return generator.choice(
        PAPER_BATTERY_CAPACITIES
    )


def sample_normal_positive(
    mean: float,
    std: float,
    rng: Optional[random.Random] = None,
) -> float:
    """
    Sample a positive value from a normal distribution.

    Used for:

        d_0 ~ N(600, 50)
        d_s ~ N(400, 50)

    Negative values are rejected and resampled.
    """

    if mean <= 0:
        raise ValueError(
            "mean must be positive."
        )

    if std <= 0:
        raise ValueError(
            "std must be positive."
        )

    generator = rng if rng is not None else random

    while True:

        value = generator.gauss(
            mean,
            std,
        )

        if value > 0:
            return value


def sample_maximum_range(
    rng: Optional[random.Random] = None,
) -> float:
    """
    Sample theoretical maximum driving range.

    Paper assumption:

        d_0 ~ N(600 km, 50 km)
    """

    return sample_normal_positive(
        mean=PAPER_MAX_RANGE_MEAN,
        std=PAPER_MAX_RANGE_STD,
        rng=rng,
    )


def sample_safe_range(
    rng: Optional[random.Random] = None,
) -> float:
    """
    Sample absolutely safe driving range.

    Paper assumption:

        d_s ~ N(400 km, 50 km)
    """

    return sample_normal_positive(
        mean=PAPER_SAFE_RANGE_MEAN,
        std=PAPER_SAFE_RANGE_STD,
        rng=rng,
    )


# ============================================================
# 6. EV Type Generator
# ============================================================

def generate_ev_type(
    distance_to_station: float,
    rng: Optional[random.Random] = None,
    alpha: float = PAPER_ALPHA,
    lambda_risk: float = PAPER_LAMBDA,
    mu_a: float = PAPER_MU_A,
    mu_q: float = PAPER_MU_Q,
    target_soc: float = PAPER_TARGET_SOC,
) -> EVType:
    """
    Generate one EV private type using the paper's parameter
    distributions.

    Parameters
    ----------
    distance_to_station : float
        Distance to the next charging station in km.

    rng : random.Random, optional
        Random number generator.

    Returns
    -------
    EVType
        Generated private type.
    """

    if distance_to_station < 0:
        raise ValueError(
            "distance_to_station cannot be negative."
        )

    return EVType(
        soc=sample_soc(rng),
        battery_capacity=sample_battery_capacity(rng),
        lambda_risk=lambda_risk,
        alpha=alpha,
        mu_a=mu_a,
        mu_q=mu_q,
        target_soc=target_soc,
        distance_to_station=distance_to_station,
        safe_range=sample_safe_range(rng),
        maximum_range=sample_maximum_range(rng),
    )


def generate_ev_population(
    n_evs: int,
    distance_to_station: float,
    seed: Optional[int] = None,
    alpha: float = PAPER_ALPHA,
    lambda_risk: float = PAPER_LAMBDA,
    mu_a: float = PAPER_MU_A,
    mu_q: float = PAPER_MU_Q,
    target_soc: float = PAPER_TARGET_SOC,
) -> List[EVType]:
    """
    Generate a population of EV private types.

    Parameters
    ----------
    n_evs : int
        Number of EVs.

    distance_to_station : float
        Distance to the next charging station.

    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    list of EVType
        Generated EV population.
    """

    if n_evs < 1:
        raise ValueError(
            "n_evs must be at least 1."
        )

    rng = random.Random(seed)

    return [
        generate_ev_type(
            distance_to_station=distance_to_station,
            rng=rng,
            alpha=alpha,
            lambda_risk=lambda_risk,
            mu_a=mu_a,
            mu_q=mu_q,
            target_soc=target_soc,
        )
        for _ in range(n_evs)
    ]


# ============================================================
# 7. Destination Distribution
# ============================================================

@dataclass(frozen=True)
class DestinationGroup:
    """
    Destination group for Setting 2.

    Parameters
    ----------
    name : str
        Destination identifier.

    n_evs : int
        Number of EVs traveling toward this destination.

    distance_to_station : float
        Distance to the next charging station.

    """

    name: str
    n_evs: int
    distance_to_station: float

    def __post_init__(self) -> None:

        if not self.name:
            raise ValueError(
                "Destination name cannot be empty."
            )

        if self.n_evs < 1:
            raise ValueError(
                "n_evs must be at least 1."
            )

        if self.distance_to_station < 0:
            raise ValueError(
                "distance_to_station cannot be negative."
            )


def destination_probabilities(
    groups: Sequence[DestinationGroup],
) -> Dict[str, float]:
    """
    Calculate destination probabilities.

    Formula:

        q_k = N_k / N

    Parameters
    ----------
    groups : sequence of DestinationGroup
        Destination groups.

    Returns
    -------
    dict
        Destination probabilities.
    """

    if not groups:
        raise ValueError(
            "groups cannot be empty."
        )

    total_evs = sum(
        group.n_evs
        for group in groups
    )

    if total_evs <= 0:
        raise ValueError(
            "Total number of EVs must be positive."
        )

    return {
        group.name:
        group.n_evs / total_evs
        for group in groups
    }


def destination_distribution(
    groups: Sequence[DestinationGroup],
) -> Dict[str, int]:
    """
    Return destination population counts.

    This function is intentionally simple because Setting 2
    uses the actual destination-group counts N_k.
    """

    if not groups:
        raise ValueError(
            "groups cannot be empty."
        )

    return {
        group.name: group.n_evs
        for group in groups
    }


# ============================================================
# 8. Conditional SoC Probability
# ============================================================

def charging_probability_from_threshold(
    decision_point: float,
    lower_soc: float = 0.0,
    upper_soc: float = 1.0,
) -> float:
    """
    Calculate charging probability for a threshold strategy.

    The strategy is:

        Charge if SoC < decision_point.

    For a uniform distribution on [lower_soc, upper_soc]:

        P(Charge)
        =
        (decision_point - lower_soc)
        /
        (upper_soc - lower_soc)

    with the result clipped to [0, 1].

    This function is useful when the simulation uses the
    paper's SoC ~ U(20%, 100%) initialization.
    """

    if not 0.0 <= lower_soc <= 1.0:
        raise ValueError(
            "lower_soc must be between 0 and 1."
        )

    if not 0.0 <= upper_soc <= 1.0:
        raise ValueError(
            "upper_soc must be between 0 and 1."
        )

    if lower_soc >= upper_soc:
        raise ValueError(
            "lower_soc must be smaller than upper_soc."
        )

    if decision_point <= lower_soc:
        return 0.0

    if decision_point >= upper_soc:
        return 1.0

    return (
        decision_point - lower_soc
    ) / (
        upper_soc - lower_soc
    )


# ============================================================
# 9. Distribution Summary
# ============================================================

def summarize_population(
    population: Sequence[EVType],
) -> Dict[str, float]:
    """
    Calculate basic statistics for an EV population.

    Returns
    -------
    dict
        Population summary.
    """

    if not population:
        raise ValueError(
            "population cannot be empty."
        )

    mean_soc = sum(
        ev.soc
        for ev in population
    ) / len(population)

    mean_battery = sum(
        ev.battery_capacity
        for ev in population
    ) / len(population)

    mean_safe_range = sum(
        ev.safe_range
        for ev in population
    ) / len(population)

    mean_max_range = sum(
        ev.maximum_range
        for ev in population
    ) / len(population)

    return {
        "n_evs": float(len(population)),
        "mean_soc": mean_soc,
        "mean_battery_capacity": mean_battery,
        "mean_safe_range": mean_safe_range,
        "mean_maximum_range": mean_max_range,
    }


# ============================================================
# 10. Public API
# ============================================================

__all__ = [
    "EVType",
    "DestinationGroup",
    "PAPER_ALPHA",
    "PAPER_LAMBDA",
    "PAPER_MU_Q",
    "PAPER_MU_A",
    "PAPER_TARGET_SOC",
    "PAPER_BATTERY_CAPACITIES",
    "PAPER_SOC_MIN",
    "PAPER_SOC_MAX",
    "PAPER_MAX_RANGE_MEAN",
    "PAPER_MAX_RANGE_STD",
    "PAPER_SAFE_RANGE_MEAN",
    "PAPER_SAFE_RANGE_STD",
    "soc_pdf",
    "soc_cdf",
    "soc_probability",
    "expected_soc",
    "sample_soc",
    "sample_battery_capacity",
    "sample_normal_positive",
    "sample_maximum_range",
    "sample_safe_range",
    "generate_ev_type",
    "generate_ev_population",
    "destination_probabilities",
    "destination_distribution",
    "charging_probability_from_threshold",
    "summarize_population",
]


# ============================================================
# 11. Standalone Module Check
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("TYPE DISTRIBUTION MODULE CHECK")
    print("=" * 70)

    print("\n[SoC Distribution]")

    print(
        f"SoC PDF at 0.50:       "
        f"{soc_pdf(0.50):.4f}"
    )

    print(
        f"SoC CDF at 0.50:       "
        f"{soc_cdf(0.50):.4f}"
    )

    print(
        f"P(0.20 <= SoC <= 0.50): "
        f"{soc_probability(0.20, 0.50):.4f}"
    )

    print(
        f"Expected SoC U(0,1):    "
        f"{expected_soc():.4f}"
    )

    print(
        f"Expected SoC U(0.2,1):  "
        f"{expected_soc(0.20, 1.00):.4f}"
    )

    print("\n[Paper Parameters]")

    print(
        f"alpha:                  "
        f"{PAPER_ALPHA:.2f}"
    )

    print(
        f"lambda:                 "
        f"{PAPER_LAMBDA:.2f}"
    )

    print(
        f"mu_a:                   "
        f"{PAPER_MU_A:.2f} CNY"
    )

    print(
        f"mu_q:                   "
        f"{PAPER_MU_Q:.2f} CNY/hour"
    )

    print(
        f"Target SoC:             "
        f"{PAPER_TARGET_SOC:.2f}"
    )

    print("\n[Generated EV Population]")

    population = generate_ev_population(
        n_evs=10,
        distance_to_station=120.0,
        seed=42,
    )

    summary = summarize_population(
        population
    )

    for key, value in summary.items():

        if key == "n_evs":
            print(
                f"{key}: "
                f"{int(value)}"
            )
        elif "soc" in key:
            print(
                f"{key}: "
                f"{value:.4f}"
            )
        else:
            print(
                f"{key}: "
                f"{value:.2f}"
            )

    print("\n[Destination Distribution]")

    destinations = [
        DestinationGroup(
            name="Destination_A",
            n_evs=6,
            distance_to_station=120.0,
        ),
        DestinationGroup(
            name="Destination_B",
            n_evs=4,
            distance_to_station=180.0,
        ),
    ]

    probabilities = destination_probabilities(
        destinations
    )

    for name, probability in probabilities.items():

        print(
            f"{name}: "
            f"{probability:.4f}"
        )

    print("\n[Threshold Probability]")

    probability = charging_probability_from_threshold(
        decision_point=0.40,
        lower_soc=0.20,
        upper_soc=1.00,
    )

    print(
        f"P(Charge | threshold=0.40, "
        f"SoC~U(0.2,1.0)): "
        f"{probability:.4f}"
    )

    print("=" * 70)
```
