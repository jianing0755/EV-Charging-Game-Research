"""
EV Charging Model.

This module defines the basic electric vehicle (EV) model used in
the EV charging decision environment.

The module focuses on:

- State of Charge (SoC)
- Battery capacity
- Target SoC
- Maximum driving range
- Safe SoC threshold
- Danger SoC threshold

The more detailed components of the charging model are implemented
in separate modules:

- range_anxiety.py
- charging_station.py
- queue_model.py
- utility.py
- simulation.py
"""


from dataclasses import dataclass


@dataclass
class EV:
    """
    Electric vehicle model.

    Parameters
    ----------
    battery_capacity : float
        Battery capacity in kWh.

    soc : float
        Current State of Charge, normalized to [0, 1].

    target_soc : float
        Target State of Charge after charging, normalized to [0, 1].

    safe_range : float
        Safe driving range in km.

    max_range : float
        Theoretical maximum driving range in km.

    safe_soc : float
        Safe State of Charge threshold.

    danger_soc : float
        Danger State of Charge threshold.
    """

    battery_capacity: float
    soc: float
    target_soc: float
    safe_range: float
    max_range: float
    safe_soc: float = 0.0
    danger_soc: float = 0.0

    def __post_init__(self):
        """Validate EV parameters."""

        if self.battery_capacity <= 0:
            raise ValueError(
                "Battery capacity must be positive."
            )

        if not 0 <= self.soc <= 1:
            raise ValueError(
                "SoC must be between 0 and 1."
            )

        if not 0 <= self.target_soc <= 1:
            raise ValueError(
                "Target SoC must be between 0 and 1."
            )

        if self.safe_range < 0:
            raise ValueError(
                "Safe driving range cannot be negative."
            )

        if self.max_range <= 0:
            raise ValueError(
                "Maximum driving range must be positive."
            )

        if self.safe_range > self.max_range:
            raise ValueError(
                "Safe driving range cannot exceed maximum range."
            )

    # -----------------------------------------------------------------
    # Basic Battery Calculations
    # -----------------------------------------------------------------

    def available_energy(self) -> float:
        """
        Calculate the energy currently stored in the battery.

        Formula
        -------
        E_available = V_i * SoC_i

        Returns
        -------
        float
            Available battery energy in kWh.
        """

        return self.battery_capacity * self.soc

    # -----------------------------------------------------------------
    # SoC Thresholds
    # -----------------------------------------------------------------

    def calculate_safe_soc(
        self,
        distance_to_next_station: float
    ) -> float:
        """
        Calculate the safe SoC threshold.

        According to the model:

            SoC_s,i = d_i / d_s,i
                       if d_i < d_s,i

                       1
                       if d_i >= d_s,i

        where:

        - d_i is the distance to the next charging station.
        - d_s,i is the safe driving range.

        Parameters
        ----------
        distance_to_next_station : float
            Distance to the next charging station in km.

        Returns
        -------
        float
            Safe SoC threshold.
        """

        if distance_to_next_station < 0:
            raise ValueError(
                "Distance to next station cannot be negative."
            )

        if distance_to_next_station < self.safe_range:
            safe_soc = (
                distance_to_next_station
                / self.safe_range
            )
        else:
            safe_soc = 1.0

        self.safe_soc = safe_soc

        return safe_soc

    def calculate_danger_soc(
        self,
        distance_to_next_station: float
    ) -> float:
        """
        Calculate the danger SoC threshold.

        According to the model:

            SoC_d,i = d_i / d_0,i
                       if d_i < d_0,i

                       1
                       if d_i >= d_0,i

        where:

        - d_i is the distance to the next charging station.
        - d_0,i is the theoretical maximum driving range.

        Parameters
        ----------
        distance_to_next_station : float
            Distance to the next charging station in km.

        Returns
        -------
        float
            Danger SoC threshold.
        """

        if distance_to_next_station < 0:
            raise ValueError(
                "Distance to next station cannot be negative."
            )

        if distance_to_next_station < self.max_range:
            danger_soc = (
                distance_to_next_station
                / self.max_range
            )
        else:
            danger_soc = 1.0

        self.danger_soc = danger_soc

        return danger_soc

    def calculate_thresholds(
        self,
        distance_to_next_station: float
    ) -> tuple[float, float]:
        """
        Calculate both safe and danger SoC thresholds.

        Returns
        -------
        tuple[float, float]
            (safe_soc, danger_soc)
        """

        safe_soc = self.calculate_safe_soc(
            distance_to_next_station
        )

        danger_soc = self.calculate_danger_soc(
            distance_to_next_station
        )

        return safe_soc, danger_soc

    # -----------------------------------------------------------------
    # Charging Feasibility
    # -----------------------------------------------------------------

    def can_reach_next_station(
        self,
        distance_to_next_station: float
    ) -> bool:
        """
        Determine whether the EV can theoretically reach the next
        charging station without charging.

        The EV can reach the station if its current SoC is at least
        the danger SoC threshold.

        Returns
        -------
        bool
            True if the EV can reach the station.
            False otherwise.
        """

        danger_soc = self.calculate_danger_soc(
            distance_to_next_station
        )

        return self.soc >= danger_soc

    def has_range_anxiety(
        self,
        distance_to_next_station: float
    ) -> bool:
        """
        Determine whether the EV is in the range-anxiety region.

        Range anxiety exists when:

            SoC_d <= SoC < SoC_s

        Returns
        -------
        bool
            True if the EV is in the range-anxiety region.
            False otherwise.
        """

        safe_soc = self.calculate_safe_soc(
            distance_to_next_station
        )

        danger_soc = self.calculate_danger_soc(
            distance_to_next_station
        )

        return (
            danger_soc <= self.soc < safe_soc
        )

    def requires_charging(
        self,
        distance_to_next_station: float
    ) -> bool:
        """
        Determine whether the EV should charge based on the
        safe SoC threshold.

        Charging is required when:

            SoC_i < SoC_s,i

        Returns
        -------
        bool
            True if charging is required.
            False otherwise.
        """

        safe_soc = self.calculate_safe_soc(
            distance_to_next_station
        )

        return self.soc < safe_soc

    # -----------------------------------------------------------------
    # Charging State
    # -----------------------------------------------------------------

    def charging_energy(self) -> float:
        """
        Calculate the energy required to reach the target SoC.

        Formula
        -------
        E_i = V_i (SoC_t,i - SoC_i)

        If current SoC is already above the target SoC,
        the required charging energy is zero.

        Returns
        -------
        float
            Required charging energy in kWh.
        """

        soc_difference = max(
            self.target_soc - self.soc,
            0.0
        )

        return self.battery_capacity * soc_difference


# ---------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------

if __name__ == "__main__":

    # Example parameters
    #
    # Battery capacity = 80 kWh
    # Current SoC      = 30%
    # Target SoC       = 80%
    # Safe range       = 160 km
    # Maximum range    = 400 km
    # Distance to next station = 120 km

    ev = EV(
        battery_capacity=80.0,
        soc=0.30,
        target_soc=0.80,
        safe_range=160.0,
        max_range=400.0
    )

    distance_to_next_station = 120.0

    safe_soc, danger_soc = ev.calculate_thresholds(
        distance_to_next_station
    )

    available_energy = ev.available_energy()

    charging_energy = ev.charging_energy()

    print("=" * 60)
    print("EV Charging Model")
    print("=" * 60)

    print(
        f"Battery capacity:         "
        f"{ev.battery_capacity:.2f} kWh"
    )

    print(
        f"Current SoC:              "
        f"{ev.soc:.2f}"
    )

    print(
        f"Target SoC:               "
        f"{ev.target_soc:.2f}"
    )

    print(
        f"Safe driving range:       "
        f"{ev.safe_range:.2f} km"
    )

    print(
        f"Maximum driving range:    "
        f"{ev.max_range:.2f} km"
    )

    print(
        f"Distance to next station: "
        f"{distance_to_next_station:.2f} km"
    )

    print(
        f"Safe SoC:                 "
        f"{safe_soc:.2f}"
    )

    print(
        f"Danger SoC:               "
        f"{danger_soc:.2f}"
    )

    print(
        f"Available energy:         "
        f"{available_energy:.2f} kWh"
    )

    print(
        f"Can reach next station:   "
        f"{'YES' if ev.can_reach_next_station(distance_to_next_station) else 'NO'}"
    )

    print(
        f"Range anxiety:            "
        f"{'YES' if ev.has_range_anxiety(distance_to_next_station) else 'NO'}"
    )

    print(
        f"Requires charging:        "
        f"{'YES' if ev.requires_charging(distance_to_next_station) else 'NO'}"
    )

    print(
        f"Charging energy:          "
        f"{charging_energy:.2f} kWh"
    )

    print("=" * 60)
