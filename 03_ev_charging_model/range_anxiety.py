```python
"""
Range Anxiety Model.

This module implements the range anxiety component of the
EV charging decision model.

The range anxiety function is defined by three regions:

    A_i = 0,
          if SoC_i >= SoC_s,i

    A_i = lambda_i (SoC_s,i - SoC_i)^alpha_i,
          if SoC_d,i <= SoC_i < SoC_s,i

    A_i = infinity,
          if SoC_i < SoC_d,i

where:

- SoC_i is the current State of Charge.
- SoC_s,i is the safe SoC threshold.
- SoC_d,i is the danger SoC threshold.
- lambda_i controls the intensity of range anxiety.
- alpha_i controls the curvature of the anxiety function.

This module uses the EV class defined in ev_model.py.
"""


from math import inf

from ev_model import EV


# ---------------------------------------------------------------------
# Range Anxiety Calculation
# ---------------------------------------------------------------------

def calculate_range_anxiety(
    ev: EV,
    distance_to_next_station: float,
    lambda_i: float = 1.0,
    alpha_i: float = 1.0
) -> float:
    """
    Calculate the range anxiety of an EV.

    The model is:

        A_i = 0,
              if SoC_i >= SoC_s,i

        A_i = lambda_i (SoC_s,i - SoC_i)^alpha_i,
              if SoC_d,i <= SoC_i < SoC_s,i

        A_i = infinity,
              if SoC_i < SoC_d,i

    Parameters
    ----------
    ev : EV
        Electric vehicle object.

    distance_to_next_station : float
        Distance to the next charging station in km.

    lambda_i : float, default=1.0
        Range anxiety intensity parameter.

    alpha_i : float, default=1.0
        Range anxiety curvature parameter.

    Returns
    -------
    float
        Range anxiety value.

        0.0
            No range anxiety.

        Positive finite value
            Range anxiety exists.

        infinity
            Driving without charging is infeasible.
    """

    if lambda_i < 0:
        raise ValueError(
            "lambda_i must be non-negative."
        )

    if alpha_i <= 0:
        raise ValueError(
            "alpha_i must be positive."
        )

    if distance_to_next_station < 0:
        raise ValueError(
            "Distance to next station cannot be negative."
        )

    # Calculate the two SoC thresholds.
    safe_soc = ev.calculate_safe_soc(
        distance_to_next_station
    )

    danger_soc = ev.calculate_danger_soc(
        distance_to_next_station
    )

    # -------------------------------------------------------------
    # Region 1: Safe
    #
    # SoC_i >= SoC_s,i
    #
    # No range anxiety.
    # -------------------------------------------------------------

    if ev.soc >= safe_soc:
        return 0.0

    # -------------------------------------------------------------
    # Region 2: Range Anxiety
    #
    # SoC_d,i <= SoC_i < SoC_s,i
    #
    # A_i = lambda_i
    #       (SoC_s,i - SoC_i)^alpha_i
    # -------------------------------------------------------------

    if ev.soc >= danger_soc:
        return (
            lambda_i
            * (safe_soc - ev.soc) ** alpha_i
        )

    # -------------------------------------------------------------
    # Region 3: Danger
    #
    # SoC_i < SoC_d,i
    #
    # Driving without charging is infeasible.
    # -------------------------------------------------------------

    return inf


# ---------------------------------------------------------------------
# Range Anxiety Region
# ---------------------------------------------------------------------

def get_range_anxiety_region(
    ev: EV,
    distance_to_next_station: float
) -> str:
    """
    Determine the current range-anxiety region.

    Regions
    -------
    "safe"
        SoC_i >= SoC_s,i

    "range_anxiety"
        SoC_d,i <= SoC_i < SoC_s,i

    "danger"
        SoC_i < SoC_d,i

    Returns
    -------
    str
        Current range-anxiety region.
    """

    if distance_to_next_station < 0:
        raise ValueError(
            "Distance to next station cannot be negative."
        )

    safe_soc = ev.calculate_safe_soc(
        distance_to_next_station
    )

    danger_soc = ev.calculate_danger_soc(
        distance_to_next_station
    )

    if ev.soc >= safe_soc:
        return "safe"

    if ev.soc >= danger_soc:
        return "range_anxiety"

    return "danger"


# ---------------------------------------------------------------------
# Feasibility Check
# ---------------------------------------------------------------------

def is_driving_feasible(
    ev: EV,
    distance_to_next_station: float
) -> bool:
    """
    Determine whether the EV can theoretically reach the next
    charging station without charging.

    The condition is:

        SoC_i >= SoC_d,i

    Returns
    -------
    bool
        True if driving is feasible.
        False otherwise.
    """

    danger_soc = ev.calculate_danger_soc(
        distance_to_next_station
    )

    return ev.soc >= danger_soc


# ---------------------------------------------------------------------
# Range Anxiety Report
# ---------------------------------------------------------------------

def range_anxiety_report(
    ev: EV,
    distance_to_next_station: float,
    lambda_i: float = 1.0,
    alpha_i: float = 1.0
) -> dict:
    """
    Generate a complete range anxiety report.

    Returns
    -------
    dict
        Dictionary containing:

        - current_soc
        - safe_soc
        - danger_soc
        - region
        - feasible
        - range_anxiety
    """

    safe_soc = ev.calculate_safe_soc(
        distance_to_next_station
    )

    danger_soc = ev.calculate_danger_soc(
        distance_to_next_station
    )

    anxiety = calculate_range_anxiety(
        ev,
        distance_to_next_station,
        lambda_i,
        alpha_i
    )

    region = get_range_anxiety_region(
        ev,
        distance_to_next_station
    )

    feasible = is_driving_feasible(
        ev,
        distance_to_next_station
    )

    return {
        "current_soc": ev.soc,
        "safe_soc": safe_soc,
        "danger_soc": danger_soc,
        "region": region,
        "feasible": feasible,
        "range_anxiety": anxiety,
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
    # Therefore:
    #
    # Safe SoC
    # = 120 / 160
    # = 0.75
    #
    # Danger SoC
    # = 120 / 400
    # = 0.30
    #
    # Current SoC = 0.40
    #
    # Therefore:
    #
    # 0.30 <= 0.40 < 0.75
    #
    # The EV is in the range-anxiety region.
    # -------------------------------------------------------------

    ev = EV(
        battery_capacity=80.0,
        soc=0.40,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    distance_to_next_station = 120.0

    lambda_i = 2.0
    alpha_i = 1.5

    result = range_anxiety_report(
        ev,
        distance_to_next_station,
        lambda_i,
        alpha_i
    )

    print("=" * 60)
    print("Range Anxiety Model")
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

    print(
        f"Region:                   "
        f"{result['region']}"
    )

    print(
        f"Driving feasible:         "
        f"{'YES' if result['feasible'] else 'NO'}"
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

    print("=" * 60)
```
