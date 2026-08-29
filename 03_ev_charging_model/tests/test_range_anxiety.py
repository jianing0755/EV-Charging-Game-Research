```python
"""
Tests for the range anxiety model.

The tests verify the mathematical formulation:

    A_i =
        0,
        if SoC_i >= SoC_s,i

        lambda_i (SoC_s,i - SoC_i)^alpha_i,
        if SoC_d,i <= SoC_i < SoC_s,i

        infinity,
        if SoC_i < SoC_d,i
"""

from math import isinf

import pytest

from ev_model import EV
from range_anxiety import calculate_range_anxiety


# ---------------------------------------------------------------------
# Test Case 1: No Range Anxiety
# ---------------------------------------------------------------------

def test_no_range_anxiety():
    """
    If current SoC is above the safe SoC threshold,
    range anxiety should be zero.

    Example:

        Distance to station = 80 km
        Safe range = 160 km

        Safe SoC = 80 / 160 = 0.50

        Current SoC = 0.80

        Since:

            0.80 >= 0.50

        range anxiety = 0
    """

    ev = EV(
        battery_capacity=80.0,
        soc=0.80,
        target_soc=0.90,
        safe_range=160.0,
        max_range=400.0
    )

    anxiety = calculate_range_anxiety(
        ev=ev,
        distance_to_next_station=80.0,
        lambda_i=2.0,
        alpha_i=1.5
    )

    assert anxiety == pytest.approx(0.0)


# ---------------------------------------------------------------------
# Test Case 2: Range Anxiety Region
# ---------------------------------------------------------------------

def test_range_anxiety_region():
    """
    If:

        SoC_d <= SoC < SoC_s

    range anxiety should be:

        A_i =
        lambda_i (SoC_s - SoC)^alpha_i
    """

    ev = EV(
        battery_capacity=80.0,
        soc=0.40,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    distance = 120.0

    # Safe SoC:
    #
    # 120 / 160 = 0.75
    #
    # Danger SoC:
    #
    # 120 / 400 = 0.30

    lambda_i = 2.0
    alpha_i = 1.5

    expected_anxiety = (
        lambda_i
        * (0.75 - 0.40) ** alpha_i
    )

    anxiety = calculate_range_anxiety(
        ev=ev,
        distance_to_next_station=distance,
        lambda_i=lambda_i,
        alpha_i=alpha_i
    )

    assert anxiety == pytest.approx(
        expected_anxiety
    )


# ---------------------------------------------------------------------
# Test Case 3: Danger Region
# ---------------------------------------------------------------------

def test_danger_region():
    """
    If current SoC is below the danger SoC threshold,
    range anxiety should be infinity.

    This represents an infeasible no-charging decision.
    """

    ev = EV(
        battery_capacity=80.0,
        soc=0.20,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    anxiety = calculate_range_anxiety(
        ev=ev,
        distance_to_next_station=120.0,
        lambda_i=2.0,
        alpha_i=1.5
    )

    assert isinf(anxiety)


# ---------------------------------------------------------------------
# Test Case 4: Anxiety Increases as SoC Falls
# ---------------------------------------------------------------------

def test_range_anxiety_increases_when_soc_decreases():
    """
    Within the range-anxiety region, lower SoC should
    generate higher range anxiety.

    This verifies:

        SoC_i ↓
        =>
        A_i ↑
    """

    ev_high = EV(
        battery_capacity=80.0,
        soc=0.60,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    ev_low = EV(
        battery_capacity=80.0,
        soc=0.40,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    distance = 120.0

    anxiety_high_soc = calculate_range_anxiety(
        ev=ev_high,
        distance_to_next_station=distance,
        lambda_i=2.0,
        alpha_i=1.5
    )

    anxiety_low_soc = calculate_range_anxiety(
        ev=ev_low,
        distance_to_next_station=distance,
        lambda_i=2.0,
        alpha_i=1.5
    )

    assert anxiety_low_soc > anxiety_high_soc


# ---------------------------------------------------------------------
# Test Case 5: Invalid Parameters
# ---------------------------------------------------------------------

def test_invalid_lambda():
    """
    Lambda must be non-negative.
    """

    ev = EV(
        battery_capacity=80.0,
        soc=0.40,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    with pytest.raises(ValueError):

        calculate_range_anxiety(
            ev=ev,
            distance_to_next_station=120.0,
            lambda_i=-1.0,
            alpha_i=1.5
        )


def test_invalid_alpha():
    """
    Alpha must be positive.
    """

    ev = EV(
        battery_capacity=80.0,
        soc=0.40,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    with pytest.raises(ValueError):

        calculate_range_anxiety(
            ev=ev,
            distance_to_next_station=120.0,
            lambda_i=2.0,
            alpha_i=0.0
        )
```
