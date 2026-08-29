```python
"""
Complete EV Charging Simulation.

This module integrates all components of the EV charging model.

The simulation combines:

    EV Model
        ↓
    Safe / Danger SoC
        ↓
    Range Anxiety
        ↓
    Charging Energy
        ↓
    Charging Time
        ↓
    Queueing Time
        ↓
    Charging Cost
        ↓
    Queueing Cost
        ↓
    Total Utility
        ↓
    Charging Decision

The individual components are implemented in:

- ev_model.py
- range_anxiety.py
- charging_station.py
- queue_model.py
- utility.py

This file serves as the main entry point for running the
complete EV charging model.
"""


from math import inf

from ev_model import EV
from charging_station import ChargingStation
from range_anxiety import (
    calculate_range_anxiety
)
from queue_model import (
    calculate_queue_time
)
from utility import (
    charging_utility,
    queue_utility,
    total_utility,
    no_charging_utility,
    charging_decision_utility,
    should_charge
)


# ---------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------

def run_simulation(
    ev: EV,
    charging_station: ChargingStation,
    distance_to_next_station: float,
    charging_energies: list[float],
    waiting_cost: float,
    lambda_i: float = 1.0,
    alpha_i: float = 1.0,
    existing_queue_time: float = 0.0
) -> dict:
    """
    Run the complete EV charging simulation.

    Parameters
    ----------
    ev : EV
        Electric vehicle object.

    charging_station : ChargingStation
        Charging station object.

    distance_to_next_station : float
        Distance to the next charging station in km.

    charging_energies : list[float]
        Charging energy requirements of all EVs
        choosing to charge.

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
        Complete simulation results.
    """

    # -------------------------------------------------------------
    # Basic validation
    # -------------------------------------------------------------

    if distance_to_next_station < 0:
        raise ValueError(
            "Distance to next station cannot be negative."
        )

    if waiting_cost < 0:
        raise ValueError(
            "Waiting cost cannot be negative."
        )

    if existing_queue_time < 0:
        raise ValueError(
            "Existing queue time cannot be negative."
        )

    num_charging_evs = len(
        charging_energies
    )

    # -------------------------------------------------------------
    # Step 1: Calculate SoC thresholds
    # -------------------------------------------------------------

    safe_soc = ev.calculate_safe_soc(
        distance_to_next_station
    )

    danger_soc = ev.calculate_danger_soc(
        distance_to_next_station
    )

    # -------------------------------------------------------------
    # Step 2: Calculate range anxiety
    # -------------------------------------------------------------

    range_anxiety = calculate_range_anxiety(
        ev=ev,
        distance_to_next_station=distance_to_next_station,
        lambda_i=lambda_i,
        alpha_i=alpha_i
    )

    # -------------------------------------------------------------
    # Step 3: Calculate charging energy
    # -------------------------------------------------------------

    charging_energy = ev.charging_energy()

    # -------------------------------------------------------------
    # Step 4: Calculate charging time
    # -------------------------------------------------------------

    charging_time = charging_station.charging_time(
        charging_energy
    )

    # -------------------------------------------------------------
    # Step 5: Calculate expected queueing time
    # -------------------------------------------------------------

    queueing_time = calculate_queue_time(
        num_charging_evs=num_charging_evs,
        charging_station=charging_station,
        charging_energies=charging_energies,
        existing_queue_time=existing_queue_time
    )

    # -------------------------------------------------------------
    # Step 6: Calculate charging utility
    #
    # Pi_c,i = -E_i P
    # -------------------------------------------------------------

    pi_c = charging_utility(
        charging_energy=charging_energy,
        electricity_price=(
            charging_station.electricity_price
        )
    )

    # -------------------------------------------------------------
    # Step 7: Calculate queueing utility
    #
    # Pi_q,i = -mu_q,i t
    # -------------------------------------------------------------

    pi_q = queue_utility(
        waiting_time=queueing_time,
        waiting_cost=waiting_cost
    )

    # -------------------------------------------------------------
    # Step 8: Utility of charging
    #
    # Pi_i^charge = Pi_c,i + Pi_q,i
    # -------------------------------------------------------------

    pi_charge = charging_decision_utility(
        charging_energy=charging_energy,
        electricity_price=(
            charging_station.electricity_price
        ),
        waiting_time=queueing_time,
        waiting_cost=waiting_cost
    )

    # -------------------------------------------------------------
    # Step 9: Utility of not charging
    #
    # Pi_i^no_charge = Pi_a,i
    # -------------------------------------------------------------

    pi_no_charge = no_charging_utility(
        range_anxiety
    )

    # -------------------------------------------------------------
    # Step 10: Total utility
    #
    # Pi_i = Pi_a,i + Pi_c,i + Pi_q,i
    # -------------------------------------------------------------

    pi_total = total_utility(
        range_anxiety=range_anxiety,
        charging_utility_value=pi_c,
        queue_utility_value=pi_q
    )

    # -------------------------------------------------------------
    # Step 11: Final charging decision
    #
    # Charge if:
    #
    # Pi_i^charge > Pi_i^no_charge
    # -------------------------------------------------------------

    decision = should_charge(
        charge_utility=pi_charge,
        no_charge_utility=pi_no_charge
    )

    # -------------------------------------------------------------
    # Return complete results
    # -------------------------------------------------------------

    return {
        "current_soc": ev.soc,
        "target_soc": ev.target_soc,
        "safe_soc": safe_soc,
        "danger_soc": danger_soc,
        "distance_to_next_station": (
            distance_to_next_station
        ),
        "range_anxiety": range_anxiety,
        "charging_energy": charging_energy,
        "charging_time": charging_time,
        "num_charging_evs": num_charging_evs,
        "num_piles": charging_station.num_piles,
        "queueing_time": queueing_time,
        "electricity_price": (
            charging_station.electricity_price
        ),
        "charging_utility": pi_c,
        "queueing_utility": pi_q,
        "charge_utility": pi_charge,
        "no_charge_utility": pi_no_charge,
        "total_utility": pi_total,
        "should_charge": decision,
    }


# ---------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------

def print_simulation_results(
    results: dict
) -> None:
    """
    Print the complete simulation results.

    Parameters
    ----------
    results : dict
        Results returned by run_simulation().
    """

    print("=" * 70)
    print("EV CHARGING MODEL SIMULATION")
    print("=" * 70)

    print("\n[EV State]")

    print(
        f"Current SoC:              "
        f"{results['current_soc']:.2f}"
    )

    print(
        f"Target SoC:               "
        f"{results['target_soc']:.2f}"
    )

    print(
        f"Distance to next station: "
        f"{results['distance_to_next_station']:.2f} km"
    )

    print("\n[SoC Thresholds]")

    print(
        f"Safe SoC:                 "
        f"{results['safe_soc']:.2f}"
    )

    print(
        f"Danger SoC:               "
        f"{results['danger_soc']:.2f}"
    )

    print("\n[Range Anxiety]")

    if results["range_anxiety"] == inf:
        print(
            "Range anxiety:            "
            "INFINITY"
        )
    else:
        print(
            f"Range anxiety:            "
            f"{results['range_anxiety']:.6f}"
        )

    print("\n[Charging]")

    print(
        f"Charging energy:          "
        f"{results['charging_energy']:.2f} kWh"
    )

    print(
        f"Charging time:            "
        f"{results['charging_time']:.2f} hours"
    )

    print(
        f"Electricity price:        "
        f"{results['electricity_price']:.2f} / kWh"
    )

    print("\n[Queue]")

    print(
        f"Charging EVs:             "
        f"{results['num_charging_evs']}"
    )

    print(
        f"Charging piles:           "
        f"{results['num_piles']}"
    )

    print(
        f"Expected queueing time:   "
        f"{results['queueing_time']:.2f} hours"
    )

    print(
        f"Expected queueing time:   "
        f"{results['queueing_time'] * 60:.2f} minutes"
    )

    print("\n[Utility]")

    print(
        f"Charging utility:         "
        f"{results['charging_utility']:.4f}"
    )

    print(
        f"Queueing utility:         "
        f"{results['queueing_utility']:.4f}"
    )

    print(
        f"Utility of charging:      "
        f"{results['charge_utility']:.4f}"
    )

    if results["no_charge_utility"] == inf:
        print(
            "Utility of no charging:   "
            "INFINITY"
        )
    else:
        print(
            f"Utility of no charging:   "
            f"{results['no_charge_utility']:.6f}"
        )

    if results["total_utility"] == inf:
        print(
            "Total utility:            "
            "INFINITY"
        )
    else:
        print(
            f"Total utility:            "
            f"{results['total_utility']:.4f}"
        )

    print("\n[Decision]")

    if results["should_charge"]:
        print(
            "Preferred decision:       "
            "CHARGE"
        )
    else:
        print(
            "Preferred decision:       "
            "DO NOT CHARGE"
        )

    print("=" * 70)


# ---------------------------------------------------------------------
# Example Simulation
# ---------------------------------------------------------------------

if __name__ == "__main__":

    # -------------------------------------------------------------
    # EV Parameters
    # -------------------------------------------------------------
    #
    # Battery capacity = 80 kWh
    # Current SoC      = 40%
    # Target SoC       = 80%
    # Safe range       = 160 km
    # Maximum range    = 400 km
    #
    # -------------------------------------------------------------

    ev = EV(
        battery_capacity=80.0,
        soc=0.40,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    # -------------------------------------------------------------
    # Charging Station
    # -------------------------------------------------------------
    #
    # Charging power    = 50 kW
    # Electricity price = 0.30 / kWh
    # Charging piles    = 4
    #
    # -------------------------------------------------------------

    station = ChargingStation(
        charging_power=50.0,
        electricity_price=0.30,
        num_piles=4
    )

    # -------------------------------------------------------------
    # Trip and Queue Parameters
    # -------------------------------------------------------------

    distance_to_next_station = 120.0

    # Three EVs choose to charge.
    #
    # Their charging energy requirements are:
    #
    # EV 1 = 20 kWh
    # EV 2 = 40 kWh
    # EV 3 = 60 kWh

    charging_energies = [
        20.0,
        40.0,
        60.0
    ]

    # Driver-specific waiting cost.
    waiting_cost = 20.0

    # Range anxiety parameters.
    lambda_i = 2.0
    alpha_i = 1.5

    # Existing queue before the EV arrives.
    existing_queue_time = 0.0

    # -------------------------------------------------------------
    # Run simulation
    # -------------------------------------------------------------

    results = run_simulation(
        ev=ev,
        charging_station=station,
        distance_to_next_station=(
            distance_to_next_station
        ),
        charging_energies=charging_energies,
        waiting_cost=waiting_cost,
        lambda_i=lambda_i,
        alpha_i=alpha_i,
        existing_queue_time=existing_queue_time
    )

    # -------------------------------------------------------------
    # Print results
    # -------------------------------------------------------------

    print_simulation_results(
        results
    )
```
