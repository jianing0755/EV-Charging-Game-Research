```python
"""
Utility Model for EV Charging.

This module implements the utility functions in the
EV charging decision model.

The model contains three utility components:

1. Range anxiety utility
2. Charging cost utility
3. Queueing cost utility

The mathematical formulation is:

    Pi_i = Pi_a,i + Pi_c,i + Pi_q,i

For a charging EV:

    Pi_i^charge = Pi_c,i + Pi_q,i

For an EV that does not charge:

    Pi_i^no_charge = Pi_a,i

The charging decision is:

    Charge if

        Pi_i^charge > Pi_i^no_charge

The individual utility components are:

Range anxiety:

    A_i =
        0,
        if SoC_i >= SoC_s,i

        lambda_i (SoC_s,i - SoC_i)^alpha_i,
        if SoC_d,i <= SoC_i < SoC_s,i

        infinity,
        if SoC_i < SoC_d,i

Charging utility:

    Pi_c,i = -E_i P

Queueing utility:

    Pi_q,i = -mu_q,i t

This module combines the components implemented in:

- ev_model.py
- range_anxiety.py
- charging_station.py
- queue_model.py
"""


from math import inf

from ev_model import EV
from range_anxiety import calculate_range_anxiety
from charging_station import ChargingStation
from queue_model import calculate_queue_time


# ---------------------------------------------------------------------
# Charging Utility
# ---------------------------------------------------------------------

def charging_utility(
    charging_energy: float,
    electricity_price: float
) -> float:
    """
    Calculate charging utility.

    The charging cost is:

        C_i = E_i P

    The corresponding utility is:

        Pi_c,i = -C_i

    Therefore:

        Pi_c,i = -E_i P

    Parameters
    ----------
    charging_energy : float
        Required charging energy in kWh.

    electricity_price : float
        Electricity price per kWh.

    Returns
    -------
    float
        Charging utility.
    """

    if charging_energy < 0:
        raise ValueError(
            "Charging energy cannot be negative."
        )

    if electricity_price < 0:
        raise ValueError(
            "Electricity price cannot be negative."
        )

    charging_cost = (
        charging_energy
        * electricity_price
    )

    return -charging_cost


# ---------------------------------------------------------------------
# Queueing Utility
# ---------------------------------------------------------------------

def queue_utility(
    waiting_time: float,
    waiting_cost: float
) -> float:
    """
    Calculate queueing utility.

    The queueing utility is:

        Pi_q,i = -mu_q,i t

    where:

    - mu_q,i is the driver's cost of waiting.
    - t is the expected queueing time.

    Parameters
    ----------
    waiting_time : float
        Expected queueing time in hours.

    waiting_cost : float
        Driver-specific cost of waiting per hour.

    Returns
    -------
    float
        Queueing utility.
    """

    if waiting_time < 0:
        raise ValueError(
            "Waiting time cannot be negative."
        )

    if waiting_cost < 0:
        raise ValueError(
            "Waiting cost cannot be negative."
        )

    return -waiting_cost * waiting_time


# ---------------------------------------------------------------------
# Total Utility
# ---------------------------------------------------------------------

def total_utility(
    range_anxiety: float,
    charging_utility_value: float,
    queue_utility_value: float
) -> float:
    """
    Calculate total utility.

    The total utility is:

        Pi_i = Pi_a,i + Pi_c,i + Pi_q,i

    Parameters
    ----------
    range_anxiety : float
        Range anxiety component.

    charging_utility_value : float
        Charging utility component.

    queue_utility_value : float
        Queueing utility component.

    Returns
    -------
    float
        Total utility.
    """

    # If the EV is below the danger threshold, driving without
    # charging is infeasible and range anxiety is infinity.
    #
    # The total utility remains mathematically well-defined
    # for the charging case as long as the charging utility and
    # queueing utility are finite.

    if range_anxiety == inf:
        return inf

    return (
        range_anxiety
        + charging_utility_value
        + queue_utility_value
    )


# ---------------------------------------------------------------------
# No-Charging Utility
# ---------------------------------------------------------------------

def no_charging_utility(
    range_anxiety: float
) -> float:
    """
    Calculate utility when the EV does not charge.

    According to the model:

        Pi_i^no_charge = Pi_a,i

    Parameters
    ----------
    range_anxiety : float
        Range anxiety associated with not charging.

    Returns
    -------
    float
        Utility of not charging.
    """

    return range_anxiety


# ---------------------------------------------------------------------
# Charging Utility
# ---------------------------------------------------------------------

def charging_decision_utility(
    charging_energy: float,
    electricity_price: float,
    waiting_time: float,
    waiting_cost: float
) -> float:
    """
    Calculate the utility of choosing to charge.

    According to the model:

        Pi_i^charge = Pi_c,i + Pi_q,i

    Parameters
    ----------
    charging_energy : float
        Required charging energy in kWh.

    electricity_price : float
        Electricity price per kWh.

    waiting_time : float
        Expected queueing time in hours.

    waiting_cost : float
        Driver-specific cost of waiting per hour.

    Returns
    -------
    float
        Utility of charging.
    """

    pi_c = charging_utility(
        charging_energy,
        electricity_price
    )

    pi_q = queue_utility(
        waiting_time,
        waiting_cost
    )

    return pi_c + pi_q


# ---------------------------------------------------------------------
# Charging Decision
# ---------------------------------------------------------------------

def should_charge(
    charge_utility: float,
    no_charge_utility: float
) -> bool:
    """
    Determine whether charging provides higher utility.

    The decision rule is:

        Charge if

            Pi_i^charge > Pi_i^no_charge

    Parameters
    ----------
    charge_utility : float
        Utility of charging.

    no_charge_utility : float
        Utility of not charging.

    Returns
    -------
    bool
        True if charging is preferred.
        False otherwise.
    """

    return charge_utility > no_charge_utility


# ---------------------------------------------------------------------
# Complete Utility Evaluation
# ---------------------------------------------------------------------

def evaluate_utility(
    ev: EV,
    charging_station: ChargingStation,
    distance_to_next_station: float,
    num_charging_evs: int,
    charging_energies: list[float],
    waiting_cost: float,
    lambda_i: float = 1.0,
    alpha_i: float = 1.0,
    existing_queue_time: float = 0.0
) -> dict:
    """
    Evaluate the complete utility structure of an EV.

    The function combines:

        EV model
            ↓
        Range anxiety
            ↓
        Charging energy
            ↓
        Charging time
            ↓
        Queueing time
            ↓
        Charging utility
            ↓
        Queueing utility
            ↓
        Total utility
            ↓
        Charging decision

    Parameters
    ----------
    ev : EV
        Electric vehicle object.

    charging_station : ChargingStation
        Charging station object.

    distance_to_next_station : float
        Distance to the next charging station in km.

    num_charging_evs : int
        Number of EVs choosing to charge.

    charging_energies : list[float]
        Charging energy requirements of all charging EVs.

    waiting_cost : float
        Driver-specific cost of waiting per hour.

    lambda_i : float, default=1.0
        Range anxiety intensity parameter.

    alpha_i : float, default=1.0
        Range anxiety curvature parameter.

    existing_queue_time : float, default=0.0
        Existing queueing time in hours.

    Returns
    -------
    dict
        Complete utility evaluation.
    """

    # -------------------------------------------------------------
    # Validate number of charging EVs
    # -------------------------------------------------------------

    if num_charging_evs < 0:
        raise ValueError(
            "Number of charging EVs cannot be negative."
        )

    if len(charging_energies) != num_charging_evs:
        raise ValueError(
            "Number of charging energies must match "
            "number of charging EVs."
        )

    # -------------------------------------------------------------
    # Range Anxiety
    # -------------------------------------------------------------

    range_anxiety = calculate_range_anxiety(
        ev=ev,
        distance_to_next_station=distance_to_next_station,
        lambda_i=lambda_i,
        alpha_i=alpha_i
    )

    # -------------------------------------------------------------
    # Charging Energy
    # -------------------------------------------------------------

    charging_energy = ev.charging_energy()

    # -------------------------------------------------------------
    # Queueing Time
    # -------------------------------------------------------------

    waiting_time = calculate_queue_time(
        num_charging_evs=num_charging_evs,
        charging_station=charging_station,
        charging_energies=charging_energies,
        existing_queue_time=existing_queue_time
    )

    # -------------------------------------------------------------
    # Charging Utility
    # -------------------------------------------------------------

    pi_c = charging_utility(
        charging_energy=charging_energy,
        electricity_price=(
            charging_station.electricity_price
        )
    )

    # -------------------------------------------------------------
    # Queueing Utility
    # -------------------------------------------------------------

    pi_q = queue_utility(
        waiting_time=waiting_time,
        waiting_cost=waiting_cost
    )

    # -------------------------------------------------------------
    # Utility of Charging
    #
    # Pi_i^charge = Pi_c,i + Pi_q,i
    # -------------------------------------------------------------

    pi_charge = pi_c + pi_q

    # -------------------------------------------------------------
    # Utility of Not Charging
    #
    # Pi_i^no_charge = Pi_a,i
    # -------------------------------------------------------------

    pi_no_charge = no_charging_utility(
        range_anxiety
    )

    # -------------------------------------------------------------
    # Total Utility
    #
    # Pi_i = Pi_a,i + Pi_c,i + Pi_q,i
    #
    # This is the combined utility representation.
    # -------------------------------------------------------------

    pi_total = total_utility(
        range_anxiety=range_anxiety,
        charging_utility_value=pi_c,
        queue_utility_value=pi_q
    )

    # -------------------------------------------------------------
    # Charging Decision
    # -------------------------------------------------------------

    charge = should_charge(
        charge_utility=pi_charge,
        no_charge_utility=pi_no_charge
    )

    return {
        "current_soc": ev.soc,
        "safe_soc": ev.safe_soc,
        "danger_soc": ev.danger_soc,
        "range_anxiety": range_anxiety,
        "charging_energy": charging_energy,
        "charging_time": charging_station.charging_time(
            charging_energy
        ),
        "queueing_time": waiting_time,
        "charging_utility": pi_c,
        "queueing_utility": pi_q,
        "charge_utility": pi_charge,
        "no_charge_utility": pi_no_charge,
        "total_utility": pi_total,
        "should_charge": charge,
    }


# ---------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------

if __name__ == "__main__":

    # -------------------------------------------------------------
    # Example EV
    #
    # Battery capacity = 80 kWh
    # Current SoC      = 40%
    # Target SoC       = 80%
    # Safe range       = 160 km
    # Maximum range    = 400 km
    #
    # Distance to next station = 120 km
    #
    # Safe SoC:
    #
    # SoC_s = 120 / 160
    #       = 0.75
    #
    # Danger SoC:
    #
    # SoC_d = 120 / 400
    #       = 0.30
    #
    # Current SoC = 0.40
    #
    # Therefore:
    #
    # 0.30 <= 0.40 < 0.75
    #
    # Range anxiety exists.
    # -------------------------------------------------------------

    ev = EV(
        battery_capacity=80.0,
        soc=0.40,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    # -------------------------------------------------------------
    # Charging station
    #
    # Charging power = 50 kW
    # Electricity price = 0.30 / kWh
    # Number of charging piles = 4
    # -------------------------------------------------------------

    station = ChargingStation(
        charging_power=50.0,
        electricity_price=0.30,
        num_piles=4
    )

    # -------------------------------------------------------------
    # Queue assumptions
    #
    # Three EVs choose to charge.
    # Their charging energy requirements are:
    #
    # 20 kWh
    # 40 kWh
    # 60 kWh
    #
    # Expected charging time:
    #
    # E[T] = 0.80 hours
    #
    # Expected queueing time:
    #
    # t = ((3 - 1) / (2 × 4)) × 0.80
    #   = 0.20 hours
    # -------------------------------------------------------------

    charging_energies = [
        20.0,
        40.0,
        60.0
    ]

    num_charging_evs = len(
        charging_energies
    )

    # Driver-specific cost of waiting.
    waiting_cost = 20.0

    lambda_i = 2.0
    alpha_i = 1.5

    existing_queue_time = 0.0

    result = evaluate_utility(
        ev=ev,
        charging_station=station,
        distance_to_next_station=120.0,
        num_charging_evs=num_charging_evs,
        charging_energies=charging_energies,
        waiting_cost=waiting_cost,
        lambda_i=lambda_i,
        alpha_i=alpha_i,
        existing_queue_time=existing_queue_time
    )

    print("=" * 60)
    print("EV Charging Utility Model")
    print("=" * 60)

    print(
        f"Current SoC:              "
        f"{result['current_soc']:.2f}"
    )

    print(
        f"Safe SoC:                 "
        f"{result['safe_soc']:.2f}"
    )

    print(
        f"Danger SoC:               "
        f"{result['danger_soc']:.2f}"
    )

    if result["range_anxiety"] == inf:
        print(
            "Range anxiety:            "
            "INFINITY"
        )
    else:
        print(
            f"Range anxiety:            "
            f"{result['range_anxiety']:.6f}"
        )

    print(
        f"Charging energy:          "
        f"{result['charging_energy']:.2f} kWh"
    )

    print(
        f"Charging time:            "
        f"{result['charging_time']:.2f} hours"
    )

    print(
        f"Queueing time:            "
        f"{result['queueing_time']:.2f} hours"
    )

    print(
        f"Charging utility:         "
        f"{result['charging_utility']:.2f}"
    )

    print(
        f"Queueing utility:         "
        f"{result['queueing_utility']:.2f}"
    )

    print(
        f"Utility of charging:      "
        f"{result['charge_utility']:.2f}"
    )

    print(
        f"Utility of no charging:   "
        f"{result['no_charge_utility']:.6f}"
    )

    print(
        f"Total utility:            "
        f"{result['total_utility']:.2f}"
    )

    print(
        f"Preferred decision:       "
        f"{'CHARGE' if result['should_charge'] else 'DO NOT CHARGE'}"
    )

    print("=" * 60)
```
