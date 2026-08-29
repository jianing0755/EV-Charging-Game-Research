"""
Tests for the utility model.

The utility model is based on:

    Charging cost:
        C_i = E_i P

    Charging utility:
        Pi_c,i = -E_i P

    Queueing utility:
        Pi_q,i = -mu_q,i t

    Total utility:
        Pi_i = Pi_a,i + Pi_c,i + Pi_q,i

    Charging decision:

        Charge if
        Pi_i^charge > Pi_i^no_charge
"""


import pytest

from utility import (
    charging_utility,
    queue_utility,
    total_utility,
    no_charging_utility,
    charging_decision_utility,
    should_charge
)


# ---------------------------------------------------------------------
# Test 1: Charging Utility
# ---------------------------------------------------------------------

def test_charging_utility():
    """
    Charging utility should equal:

        Pi_c,i = -E_i P

    Example:

        E_i = 32 kWh
        P   = 0.30

        Pi_c,i = -32 * 0.30
               = -9.60
    """

    utility = charging_utility(
        charging_energy=32.0,
        electricity_price=0.30
    )

    assert utility == pytest.approx(-9.60)


# ---------------------------------------------------------------------
# Test 2: Zero Charging Energy
# ---------------------------------------------------------------------

def test_zero_charging_energy():
    """
    If no charging energy is required, charging cost
    and charging utility should both be zero.
    """

    utility = charging_utility(
        charging_energy=0.0,
        electricity_price=0.30
    )

    assert utility == pytest.approx(0.0)


# ---------------------------------------------------------------------
# Test 3: Queueing Utility
# ---------------------------------------------------------------------

def test_queue_utility():
    """
    Queueing utility should equal:

        Pi_q,i = -mu_q,i t

    Example:

        Waiting time = 0.20 h
        Waiting cost = 20

        Pi_q,i = -20 * 0.20
               = -4.00
    """

    utility = queue_utility(
        waiting_time=0.20,
        waiting_cost=20.0
    )

    assert utility == pytest.approx(-4.00)


# ---------------------------------------------------------------------
# Test 4: Zero Waiting Time
# ---------------------------------------------------------------------

def test_zero_waiting_time():
    """
    If waiting time is zero, queueing utility should be zero.
    """

    utility = queue_utility(
        waiting_time=0.0,
        waiting_cost=20.0
    )

    assert utility == pytest.approx(0.0)


# ---------------------------------------------------------------------
# Test 5: Total Utility
# ---------------------------------------------------------------------

def test_total_utility():
    """
    Total utility should equal:

        Pi_i = Pi_a,i + Pi_c,i + Pi_q,i

    Example:

        Range anxiety = 0.414126
        Charging utility = -9.60
        Queue utility = -4.00

        Total utility
        = 0.414126 - 9.60 - 4.00
        = -13.185874
    """

    utility = total_utility(
        range_anxiety=0.414126,
        charging_utility_value=-9.60,
        queue_utility_value=-4.00
    )

    assert utility == pytest.approx(
        -13.185874
    )


# ---------------------------------------------------------------------
# Test 6: No-Charging Utility
# ---------------------------------------------------------------------

def test_no_charging_utility():
    """
    For an EV that does not charge:

        Pi_i^no_charge = Pi_a,i

    Therefore the no-charging utility should equal
    the range anxiety value.
    """

    anxiety = 0.414126

    utility = no_charging_utility(
        range_anxiety=anxiety
    )

    assert utility == pytest.approx(
        anxiety
    )


# ---------------------------------------------------------------------
# Test 7: Charging Decision Utility
# ---------------------------------------------------------------------

def test_charging_decision_utility():
    """
    Utility of charging should equal:

        Pi_i^charge
        = Pi_c,i + Pi_q,i
    """

    utility = charging_decision_utility(
        charging_energy=32.0,
        electricity_price=0.30,
        waiting_time=0.20,
        waiting_cost=20.0
    )

    expected = -9.60 - 4.00

    assert utility == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------
# Test 8: Charge Decision
# ---------------------------------------------------------------------

def test_should_charge():
    """
    The EV should charge when:

        Pi_i^charge > Pi_i^no_charge
    """

    result = should_charge(
        charge_utility=10.0,
        no_charge_utility=5.0
    )

    assert result is True


# ---------------------------------------------------------------------
# Test 9: Do Not Charge Decision
# ---------------------------------------------------------------------

def test_should_not_charge():
    """
    The EV should not charge when:

        Pi_i^charge <= Pi_i^no_charge
    """

    result = should_charge(
        charge_utility=5.0,
        no_charge_utility=10.0
    )

    assert result is False


# ---------------------------------------------------------------------
# Test 10: Equal Utilities
# ---------------------------------------------------------------------

def test_equal_utilities():
    """
    If charging and no-charging utilities are equal,
    the model should not strictly prefer charging.

    The decision rule is:

        Charge if
        Pi_i^charge > Pi_i^no_charge

    Therefore equality should result in False.
    """

    result = should_charge(
        charge_utility=10.0,
        no_charge_utility=10.0
    )

    assert result is False


# ---------------------------------------------------------------------
# Test 11: Higher Electricity Price
# ---------------------------------------------------------------------

def test_higher_electricity_price_reduces_charging_utility():
    """
    Higher electricity prices should make charging utility
    more negative.

    Since:

        Pi_c,i = -E_i P

    increasing P decreases utility.
    """

    low_price_utility = charging_utility(
        charging_energy=40.0,
        electricity_price=0.20
    )

    high_price_utility = charging_utility(
        charging_energy=40.0,
        electricity_price=0.40
    )

    assert high_price_utility < low_price_utility


# ---------------------------------------------------------------------
# Test 12: Higher Waiting Cost
# ---------------------------------------------------------------------

def test_higher_waiting_cost_reduces_queue_utility():
    """
    Higher waiting costs should make queueing utility
    more negative.

    Since:

        Pi_q,i = -mu_q,i t

    increasing mu_q,i decreases utility.
    """

    low_cost_utility = queue_utility(
        waiting_time=0.50,
        waiting_cost=10.0
    )

    high_cost_utility = queue_utility(
        waiting_time=0.50,
        waiting_cost=30.0
    )

    assert high_cost_utility < low_cost_utility


# ---------------------------------------------------------------------
# Test 13: Negative Charging Energy
# ---------------------------------------------------------------------

def test_negative_charging_energy():
    """
    Charging energy cannot be negative.
    """

    with pytest.raises(ValueError):

        charging_utility(
            charging_energy=-10.0,
            electricity_price=0.30
        )


# ---------------------------------------------------------------------
# Test 14: Negative Electricity Price
# ---------------------------------------------------------------------

def test_negative_electricity_price():
    """
    Electricity price cannot be negative.
    """

    with pytest.raises(ValueError):

        charging_utility(
            charging_energy=20.0,
            electricity_price=-0.30
        )


# ---------------------------------------------------------------------
# Test 15: Negative Waiting Time
# ---------------------------------------------------------------------

def test_negative_waiting_time():
    """
    Waiting time cannot be negative.
    """

    with pytest.raises(ValueError):

        queue_utility(
            waiting_time=-0.20,
            waiting_cost=20.0
        )


# ---------------------------------------------------------------------
# Test 16: Negative Waiting Cost
# ---------------------------------------------------------------------

def test_negative_waiting_cost():
    """
    Waiting cost cannot be negative.
    """

    with pytest.raises(ValueError):

        queue_utility(
            waiting_time=0.20,
            waiting_cost=-20.0
        )
