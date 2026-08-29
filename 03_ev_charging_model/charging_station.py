```python
"""
Charging Station Model.

This module implements the charging station component of the
EV charging decision model.

The charging station provides:

- Charging power
- Electricity price
- Number of charging piles
- Charging time
- Charging cost

The mathematical structure follows the model described in README.md.

Charging time:

    T_i = E_i / eta

where:

- E_i is the required charging energy.
- eta is the charging power.

Charging cost:

    C_i = E_i P

where:

- E_i is the required charging energy.
- P is the electricity price.

This module is designed to work with:

- ev_model.py
- queue_model.py
- utility.py
- simulation.py
"""


from dataclasses import dataclass


# ---------------------------------------------------------------------
# Charging Station
# ---------------------------------------------------------------------

@dataclass
class ChargingStation:
    """
    Charging station model.

    Parameters
    ----------
    charging_power : float
        Charging power in kW.

    electricity_price : float
        Electricity price in monetary units per kWh.

    num_piles : int
        Number of available charging piles.
    """

    charging_power: float
    electricity_price: float
    num_piles: int

    def __post_init__(self):
        """Validate charging station parameters."""

        if self.charging_power <= 0:
            raise ValueError(
                "Charging power must be positive."
            )

        if self.electricity_price < 0:
            raise ValueError(
                "Electricity price cannot be negative."
            )

        if self.num_piles <= 0:
            raise ValueError(
                "Number of charging piles must be positive."
            )

        if not isinstance(self.num_piles, int):
            raise TypeError(
                "Number of charging piles must be an integer."
            )

    # -----------------------------------------------------------------
    # Charging Time
    # -----------------------------------------------------------------

    def charging_time(
        self,
        charging_energy: float
    ) -> float:
        """
        Calculate charging time.

        Formula
        -------
        T_i = E_i / eta

        where:

        - E_i is charging energy in kWh.
        - eta is charging power in kW.

        Parameters
        ----------
        charging_energy : float
            Required charging energy in kWh.

        Returns
        -------
        float
            Charging time in hours.
        """

        if charging_energy < 0:
            raise ValueError(
                "Charging energy cannot be negative."
            )

        return charging_energy / self.charging_power

    # -----------------------------------------------------------------
    # Charging Cost
    # -----------------------------------------------------------------

    def charging_cost(
        self,
        charging_energy: float
    ) -> float:
        """
        Calculate charging cost.

        Formula
        -------
        C_i = E_i P

        where:

        - E_i is charging energy in kWh.
        - P is electricity price per kWh.

        Parameters
        ----------
        charging_energy : float
            Required charging energy in kWh.

        Returns
        -------
        float
            Charging cost.
        """

        if charging_energy < 0:
            raise ValueError(
                "Charging energy cannot be negative."
            )

        return (
            charging_energy
            * self.electricity_price
        )

    # -----------------------------------------------------------------
    # Charging Utility
    # -----------------------------------------------------------------

    def charging_utility(
        self,
        charging_energy: float
    ) -> float:
        """
        Calculate the utility associated with charging cost.

        The utility component is:

            Pi_c,i = -C_i

        Therefore:

            Pi_c,i = -E_i P

        Parameters
        ----------
        charging_energy : float
            Required charging energy in kWh.

        Returns
        -------
        float
            Charging utility.
        """

        return -self.charging_cost(
            charging_energy
        )

    # -----------------------------------------------------------------
    # Station Information
    # -----------------------------------------------------------------

    def available_piles(self) -> int:
        """
        Return the number of charging piles available
        at the station.

        Returns
        -------
        int
            Number of charging piles.
        """

        return self.num_piles

    # -----------------------------------------------------------------
    # Complete Charging Calculation
    # -----------------------------------------------------------------

    def evaluate_charging(
        self,
        charging_energy: float
    ) -> dict:
        """
        Calculate the main charging station outcomes.

        Parameters
        ----------
        charging_energy : float
            Required charging energy in kWh.

        Returns
        -------
        dict
            Dictionary containing:

            - charging_energy
            - charging_power
            - charging_time
            - electricity_price
            - charging_cost
            - charging_utility
        """

        charging_time = self.charging_time(
            charging_energy
        )

        charging_cost = self.charging_cost(
            charging_energy
        )

        charging_utility = self.charging_utility(
            charging_energy
        )

        return {
            "charging_energy": charging_energy,
            "charging_power": self.charging_power,
            "charging_time": charging_time,
            "electricity_price": self.electricity_price,
            "charging_cost": charging_cost,
            "charging_utility": charging_utility,
        }


# ---------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------

if __name__ == "__main__":

    # -------------------------------------------------------------
    # Example charging station
    #
    # Charging power    = 50 kW
    # Electricity price = 0.30 monetary units / kWh
    # Charging piles    = 4
    #
    # Suppose an EV needs 48 kWh of energy.
    #
    # Charging time:
    #
    # T_i = E_i / eta
    #     = 48 / 50
    #     = 0.96 hours
    #
    # Charging cost:
    #
    # C_i = E_i P
    #     = 48 × 0.30
    #     = 14.40
    # -------------------------------------------------------------

    station = ChargingStation(
        charging_power=50.0,
        electricity_price=0.30,
        num_piles=4
    )

    charging_energy = 48.0

    result = station.evaluate_charging(
        charging_energy
    )

    print("=" * 60)
    print("Charging Station Model")
    print("=" * 60)

    print(
        f"Charging power:           "
        f"{result['charging_power']:.2f} kW"
    )

    print(
        f"Electricity price:        "
        f"{result['electricity_price']:.2f} / kWh"
    )

    print(
        f"Charging piles:           "
        f"{station.num_piles}"
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
        f"Charging cost:            "
        f"{result['charging_cost']:.2f}"
    )

    print(
        f"Charging utility:         "
        f"{result['charging_utility']:.2f}"
    )

    print("=" * 60)
```
