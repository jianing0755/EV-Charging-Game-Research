```python
"""
Queueing Model for EV Charging.

This module implements the queueing component of the
EV charging decision model.

The model captures congestion at a charging station.

The expected queueing time is defined as:

    t = ((c(N) - 1) / (2k)) E[T] + t_0

where:

- c(N) is the number of EVs choosing to charge.
- k is the number of available charging piles.
- E[T] is the expected charging time.
- t_0 is the existing queueing time.
- t is the expected queueing time.

This module is designed to work with:

- ev_model.py
- charging_station.py
- utility.py
- simulation.py
"""


from charging_station import ChargingStation


# ---------------------------------------------------------------------
# Charging Time
# ---------------------------------------------------------------------

def expected_charging_time(
    charging_energies: list[float],
    charging_station: ChargingStation
) -> float:
    """
    Calculate the expected charging time of EVs.

    Each EV's charging time is calculated using:

        T_i = E_i / eta

    The expected charging time is the arithmetic mean:

        E[T] = (1 / N) * sum(T_i)

    Parameters
    ----------
    charging_energies : list[float]
        Charging energy requirements of EVs in kWh.

    charging_station : ChargingStation
        Charging station object.

    Returns
    -------
    float
        Expected charging time in hours.
    """

    if not charging_energies:
        return 0.0

    charging_times = [
        charging_station.charging_time(
            energy
        )
        for energy in charging_energies
    ]

    return sum(charging_times) / len(charging_times)


# ---------------------------------------------------------------------
# Queueing Time
# ---------------------------------------------------------------------

def expected_queue_time(
    num_charging_evs: int,
    num_piles: int,
    expected_charging_time: float,
    existing_queue_time: float = 0.0
) -> float:
    """
    Calculate expected queueing time.

    The model is:

        t =
        ((c(N) - 1) / (2k)) E[T] + t_0

    where:

    - c(N) is the number of EVs choosing to charge.
    - k is the number of charging piles.
    - E[T] is expected charging time.
    - t_0 is existing queueing time.

    Parameters
    ----------
    num_charging_evs : int
        Number of EVs choosing to charge.

    num_piles : int
        Number of charging piles.

    expected_charging_time : float
        Expected charging time in hours.

    existing_queue_time : float, default=0.0
        Existing queueing time in hours.

    Returns
    -------
    float
        Expected queueing time in hours.
    """

    if num_charging_evs < 0:
        raise ValueError(
            "Number of charging EVs cannot be negative."
        )

    if num_piles <= 0:
        raise ValueError(
            "Number of charging piles must be positive."
        )

    if expected_charging_time < 0:
        raise ValueError(
            "Expected charging time cannot be negative."
        )

    if existing_queue_time < 0:
        raise ValueError(
            "Existing queueing time cannot be negative."
        )

    # If there are no charging EVs, there is no newly generated queue.
    if num_charging_evs == 0:
        return existing_queue_time

    queue_time = (
        (
            num_charging_evs - 1
        )
        / (2 * num_piles)
        * expected_charging_time
        + existing_queue_time
    )

    return queue_time


# ---------------------------------------------------------------------
# Queueing Time Using Charging Station
# ---------------------------------------------------------------------

def calculate_queue_time(
    num_charging_evs: int,
    charging_station: ChargingStation,
    charging_energies: list[float],
    existing_queue_time: float = 0.0
) -> float:
    """
    Calculate expected queueing time directly from a
    ChargingStation object and charging energy requirements.

    This function combines:

        Charging Energy
              ↓
        Charging Time
              ↓
        Expected Charging Time
              ↓
        Expected Queueing Time

    Parameters
    ----------
    num_charging_evs : int
        Number of EVs choosing to charge.

    charging_station : ChargingStation
        Charging station object.

    charging_energies : list[float]
        Charging energy requirements of charging EVs in kWh.

    existing_queue_time : float, default=0.0
        Existing queueing time in hours.

    Returns
    -------
    float
        Expected queueing time in hours.
    """

    if len(charging_energies) != num_charging_evs:
        raise ValueError(
            "Number of charging energies must match "
            "number of charging EVs."
        )

    expected_time = expected_charging_time(
        charging_energies,
        charging_station
    )

    return expected_queue_time(
        num_charging_evs=num_charging_evs,
        num_piles=charging_station.num_piles,
        expected_charging_time=expected_time,
        existing_queue_time=existing_queue_time
    )


# ---------------------------------------------------------------------
# Queueing Report
# ---------------------------------------------------------------------

def queue_report(
    num_charging_evs: int,
    charging_station: ChargingStation,
    charging_energies: list[float],
    existing_queue_time: float = 0.0
) -> dict:
    """
    Generate a complete queueing report.

    Returns
    -------
    dict
        Dictionary containing:

        - number of charging EVs
        - number of charging piles
        - expected charging time
        - existing queue time
        - expected queueing time
    """

    expected_time = expected_charging_time(
        charging_energies,
        charging_station
    )

    queue_time = expected_queue_time(
        num_charging_evs=num_charging_evs,
        num_piles=charging_station.num_piles,
        expected_charging_time=expected_time,
        existing_queue_time=existing_queue_time
    )

    return {
        "num_charging_evs": num_charging_evs,
        "num_piles": charging_station.num_piles,
        "expected_charging_time": expected_time,
        "existing_queue_time": existing_queue_time,
        "expected_queue_time": queue_time,
    }


# ---------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------

if __name__ == "__main__":

    # -------------------------------------------------------------
    # Example charging station
    #
    # Charging power = 50 kW
    # Number of charging piles = 4
    #
    # Three EVs choose to charge:
    #
    # EV 1: 20 kWh
    # EV 2: 40 kWh
    # EV 3: 60 kWh
    #
    # Charging times:
    #
    # T1 = 20 / 50 = 0.40 h
    # T2 = 40 / 50 = 0.80 h
    # T3 = 60 / 50 = 1.20 h
    #
    # Expected charging time:
    #
    # E[T] = (0.40 + 0.80 + 1.20) / 3
    #      = 0.80 h
    #
    # Queueing time:
    #
    # t = ((3 - 1) / (2 × 4)) × 0.80 + 0
    #   = 0.20 h
    #
    # Therefore:
    #
    # Expected queueing time = 0.20 hours
    #                         = 12 minutes
    # -------------------------------------------------------------

    station = ChargingStation(
        charging_power=50.0,
        electricity_price=0.30,
        num_piles=4
    )

    charging_energies = [
        20.0,
        40.0,
        60.0
    ]

    num_charging_evs = len(
        charging_energies
    )

    existing_queue_time = 0.0

    result = queue_report(
        num_charging_evs=num_charging_evs,
        charging_station=station,
        charging_energies=charging_energies,
        existing_queue_time=existing_queue_time
    )

    print("=" * 60)
    print("EV Charging Queue Model")
    print("=" * 60)

    print(
        f"Charging EVs:             "
        f"{result['num_charging_evs']}"
    )

    print(
        f"Charging piles:           "
        f"{result['num_piles']}"
    )

    print(
        f"Expected charging time:   "
        f"{result['expected_charging_time']:.2f} hours"
    )

    print(
        f"Existing queue time:      "
        f"{result['existing_queue_time']:.2f} hours"
    )

    print(
        f"Expected queueing time:   "
        f"{result['expected_queue_time']:.2f} hours"
    )

    print(
        f"Expected queueing time:   "
        f"{result['expected_queue_time'] * 60:.2f} minutes"
    )

    print("=" * 60)
```
