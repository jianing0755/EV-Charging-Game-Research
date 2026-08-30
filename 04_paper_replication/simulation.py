"""
Complete Simulation for the Bayesian EV Charging Game.

Paper
-----
"Incorporating Bounded Rationality into Electric Vehicle
Highway Charging Decisions: A Bayesian Game Analysis"

This module integrates the main components of Stage 04:

    type_distribution.py
            ↓
    expected_cost.py
            ↓
    payoff.py
            ↓
    bne_solver.py
            ↓
    Bayesian Nash Equilibrium

The simulation provides:

1. Baseline Bayesian game parameters
2. EV type distribution
3. Charging probability
4. Expected number of charging EVs
5. Charging and non-charging payoffs
6. BNE threshold
7. Equilibrium verification
8. Comparative parameter experiments

Run:

    python simulation.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from type_distribution import (
    PAPER_SOC_MIN,
    PAPER_SOC_MAX,
    generate_ev_population,
    summarize_population,
)

from payoff import (
    calculate_safe_soc,
    calculate_danger_soc,
    charging_energy,
    charging_time,
    charging_cost,
    range_anxiety_cost,
    charging_payoff,
    no_charging_payoff,
)

from bne_solver import (
    BNEParameters,
    BNEResult,
    charging_probability,
    expected_charging_evs,
    solve_bne,
    verify_equilibrium,
)


# ============================================================
# 1. Simulation Configuration
# ============================================================

@dataclass(frozen=True)
class SimulationConfig:
    """
    Configuration for a complete Bayesian EV charging
    simulation.
    """

    n_evs: int = 10

    battery_capacity: float = 80.0

    target_soc: float = 0.80

    electricity_price: float = 0.30

    distance_to_station: float = 120.0

    safe_range: float = 160.0

    maximum_range: float = 400.0

    lambda_risk: float = 1.5

    alpha: float = 2.0

    charging_piles: int = 4

    charging_power: float = 50.0

    waiting_cost_per_hour: float = 20.0

    existing_queue_time: float = 0.0

    random_seed: int = 42

    initial_threshold: float = 0.50

    tolerance: float = 1e-3

    max_iterations: int = 50

    grid_size: int = 501


# ============================================================
# 2. Build Bayesian Game Parameters
# ============================================================

def build_bne_parameters(
    config: SimulationConfig,
) -> BNEParameters:
    """
    Convert simulation configuration into BNE parameters.
    """

    return BNEParameters(
        n_evs=config.n_evs,
        battery_capacity=config.battery_capacity,
        target_soc=config.target_soc,
        electricity_price=config.electricity_price,
        distance_to_station=config.distance_to_station,
        safe_range=config.safe_range,
        maximum_range=config.maximum_range,
        lambda_risk=config.lambda_risk,
        alpha=config.alpha,
        charging_piles=config.charging_piles,
        charging_power=config.charging_power,
        waiting_cost_per_hour=config.waiting_cost_per_hour,
        existing_queue_time=config.existing_queue_time,
        soc_min=PAPER_SOC_MIN,
        soc_max=PAPER_SOC_MAX,
    )


# ============================================================
# 3. Generate EV Population
# ============================================================

def generate_population(
    config: SimulationConfig,
):
    """
    Generate a reproducible EV population.
    """

    return generate_ev_population(
        n_evs=config.n_evs,
        distance_to_station=config.distance_to_station,
        seed=config.random_seed,
        alpha=config.alpha,
        lambda_risk=config.lambda_risk,
        mu_a=3000.0,
        mu_q=config.waiting_cost_per_hour,
        target_soc=config.target_soc,
    )


# ============================================================
# 4. Print Population Summary
# ============================================================

def print_population_summary(
    population,
) -> None:
    """
    Display the simulated private-type distribution.
    """

    summary = summarize_population(
        population
    )

    print("\n[EV Population]")

    print(
        f"Number of EVs:             "
        f"{int(summary['n_evs'])}"
    )

    print(
        f"Mean SoC:                  "
        f"{summary['mean_soc']:.4f}"
    )

    print(
        f"Mean battery capacity:     "
        f"{summary['mean_battery_capacity']:.2f} kWh"
    )

    print(
        f"Mean safe range:           "
        f"{summary['mean_safe_range']:.2f} km"
    )

    print(
        f"Mean maximum range:        "
        f"{summary['mean_maximum_range']:.2f} km"
    )


# ============================================================
# 5. Print Representative EV
# ============================================================

def print_representative_ev(
    population,
    config: SimulationConfig,
) -> None:
    """
    Display the payoff structure of the first EV in the
    simulated population.

    This provides an intuitive connection between the private
    type and the Bayesian game.
    """

    ev = population[0]

    safe_soc = calculate_safe_soc(
        distance_to_station=config.distance_to_station,
        safe_range=ev.safe_range,
    )

    danger_soc = calculate_danger_soc(
        distance_to_station=config.distance_to_station,
        maximum_range=ev.maximum_range,
    )

    energy = charging_energy(
        battery_capacity=ev.battery_capacity,
        soc=ev.soc,
        target_soc=config.target_soc,
    )

    time = charging_time(
        battery_capacity=ev.battery_capacity,
        soc=ev.soc,
        target_soc=config.target_soc,
        charging_power=config.charging_power,
    )

    cost = charging_cost(
        battery_capacity=ev.battery_capacity,
        soc=ev.soc,
        target_soc=config.target_soc,
        electricity_price=config.electricity_price,
    )

    anxiety = range_anxiety_cost(
        soc=ev.soc,
        distance_to_station=config.distance_to_station,
        safe_range=ev.safe_range,
        maximum_range=ev.maximum_range,
        lambda_risk=ev.lambda_risk,
        alpha=ev.alpha,
    )

    print("\n[Representative EV]")

    print(
        f"Current SoC:              "
        f"{ev.soc:.4f}"
    )

    print(
        f"Battery capacity:         "
        f"{ev.battery_capacity:.2f} kWh"
    )

    print(
        f"Safe SoC:                 "
        f"{safe_soc:.4f}"
    )

    print(
        f"Danger SoC:               "
        f"{danger_soc:.4f}"
    )

    print(
        f"Range anxiety:            "
        f"{anxiety:.6f}"
    )

    print(
        f"Charging energy:          "
        f"{energy:.2f} kWh"
    )

    print(
        f"Charging time:            "
        f"{time:.4f} hours"
    )

    print(
        f"Charging cost:            "
        f"{cost:.4f} CNY"
    )


# ============================================================
# 6. Evaluate Representative EV at BNE
# ============================================================

def evaluate_representative_ev(
    population,
    config: SimulationConfig,
    bne_result: BNEResult,
) -> Dict[str, float]:
    """
    Evaluate the first EV under the equilibrium strategy.
    """

    ev = population[0]

    charge = charging_payoff(
        battery_capacity=ev.battery_capacity,
        soc=ev.soc,
        target_soc=config.target_soc,
        electricity_price=config.electricity_price,
        n_evs=config.n_evs,
        decision_point=bne_result.threshold,
        charging_piles=config.charging_piles,
        expected_soc=(
            config.soc_min
            if hasattr(config, "soc_min")
            else 0.60
        ),
        charging_power=config.charging_power,
        waiting_cost_per_hour=config.waiting_cost_per_hour,
        existing_queue_time=config.existing_queue_time,
    )

    no_charge = no_charging_payoff(
        soc=ev.soc,
        distance_to_station=config.distance_to_station,
        safe_range=ev.safe_range,
        maximum_range=ev.maximum_range,
        lambda_risk=ev.lambda_risk,
        alpha=ev.alpha,
    )

    return {
        "soc": ev.soc,
        "charge_payoff": charge,
        "no_charge_payoff": no_charge,
    }


# ============================================================
# 7. Run Baseline Simulation
# ============================================================

def run_baseline_simulation(
    config: SimulationConfig,
) -> BNEResult:
    """
    Run the complete baseline Bayesian game simulation.
    """

    print("=" * 70)
    print("EV CHARGING BAYESIAN GAME SIMULATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Parameters
    # --------------------------------------------------------

    print("\n[Model Parameters]")

    print(
        f"Number of EVs:             "
        f"{config.n_evs}"
    )

    print(
        f"Battery capacity:          "
        f"{config.battery_capacity:.2f} kWh"
    )

    print(
        f"Target SoC:                "
        f"{config.target_soc:.2f}"
    )

    print(
        f"Distance to station:       "
        f"{config.distance_to_station:.2f} km"
    )

    print(
        f"Electricity price:         "
        f"{config.electricity_price:.2f} CNY/kWh"
    )

    print(
        f"Charging piles:            "
        f"{config.charging_piles}"
    )

    print(
        f"Charging power:            "
        f"{config.charging_power:.2f} kW"
    )

    print(
        f"Waiting cost:              "
        f"{config.waiting_cost_per_hour:.2f} CNY/hour"
    )

    print(
        f"SoC distribution:          "
        f"U({config.soc_min if hasattr(config, 'soc_min') else PAPER_SOC_MIN:.2f}, "
        f"{config.soc_max if hasattr(config, 'soc_max') else PAPER_SOC_MAX:.2f})"
    )

    # --------------------------------------------------------
    # Population
    # --------------------------------------------------------

    population = generate_population(
        config
    )

    print_population_summary(
        population
    )

    print_representative_ev(
        population,
        config,
    )

    # --------------------------------------------------------
    # Bayesian game
    # --------------------------------------------------------

    parameters = build_bne_parameters(
        config
    )

    print("\n[Bayesian Game]")

    print(
        f"Initial threshold:        "
        f"{config.initial_threshold:.4f}"
    )

    initial_probability = charging_probability(
        threshold=config.initial_threshold,
        soc_min=config.soc_min
        if hasattr(config, "soc_min")
        else PAPER_SOC_MIN,
        soc_max=config.soc_max
        if hasattr(config, "soc_max")
        else PAPER_SOC_MAX,
    )

    print(
        f"Initial charging probability: "
        f"{initial_probability:.4f}"
    )

    print(
        f"Initial expected chargers: "
        f"{config.n_evs * initial_probability:.4f}"
    )

    # --------------------------------------------------------
    # Solve BNE
    # --------------------------------------------------------

    result = solve_bne(
        parameters=parameters,
        initial_threshold=config.initial_threshold,
        tolerance=config.tolerance,
        max_iterations=config.max_iterations,
        grid_size=config.grid_size,
    )

    print("\n[BNE Result]")

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
            "BNE verification:          PASS"
        )
    else:
        print(
            "BNE verification:          FAIL"
        )

    # --------------------------------------------------------
    # Representative payoff
    # --------------------------------------------------------

    representative = evaluate_representative_ev(
        population=population,
        config=config,
        bne_result=result,
    )

    print("\n[Representative EV Payoff]")

    print(
        f"SoC:                       "
        f"{representative['soc']:.4f}"
    )

    print(
        f"Utility of charging:       "
        f"{representative['charge_payoff']:.6f}"
    )

    print(
        f"Utility of no charging:    "
        f"{representative['no_charge_payoff']:.6f}"
    )

    if (
        representative["charge_payoff"]
        >
        representative["no_charge_payoff"]
    ):
        print(
            "Preferred decision:        CHARGE"
        )
    else:
        print(
            "Preferred decision:        DO NOT CHARGE"
        )

    print("=" * 70)

    return result


# ============================================================
# 8. Price Sensitivity Experiment
# ============================================================

def price_sensitivity(
    base_config: SimulationConfig,
    prices: List[float],
) -> List[Dict[str, float]]:
    """
    Test how electricity price affects the equilibrium.

    This experiment is useful for validating the economic
    interpretation of the model.
    """

    results = []

    for price in prices:

        config = SimulationConfig(
            n_evs=base_config.n_evs,
            battery_capacity=base_config.battery_capacity,
            target_soc=base_config.target_soc,
            electricity_price=price,
            distance_to_station=base_config.distance_to_station,
            safe_range=base_config.safe_range,
            maximum_range=base_config.maximum_range,
            lambda_risk=base_config.lambda_risk,
            alpha=base_config.alpha,
            charging_piles=base_config.charging_piles,
            charging_power=base_config.charging_power,
            waiting_cost_per_hour=base_config.waiting_cost_per_hour,
            existing_queue_time=base_config.existing_queue_time,
            random_seed=base_config.random_seed,
            initial_threshold=base_config.initial_threshold,
            tolerance=base_config.tolerance,
            max_iterations=base_config.max_iterations,
            grid_size=base_config.grid_size,
        )

        parameters = build_bne_parameters(
            config
        )

        result = solve_bne(
            parameters=parameters,
            initial_threshold=config.initial_threshold,
            tolerance=config.tolerance,
            max_iterations=config.max_iterations,
            grid_size=config.grid_size,
        )

        results.append(
            {
                "electricity_price": price,
                "threshold": result.threshold,
                "charging_probability": (
                    result.charging_probability
                ),
                "expected_charging_evs": (
                    result.expected_charging_evs
                ),
            }
        )

    return results


def print_price_sensitivity(
    results: List[Dict[str, float]],
) -> None:
    """
    Print electricity-price sensitivity results.
    """

    print("\n[Price Sensitivity]")

    print(
        f"{'Price':>10}"
        f"{'Threshold':>15}"
        f"{'P(Charge)':>15}"
        f"{'E[Chargers]':>15}"
    )

    print("-" * 55)

    for result in results:

        print(
            f"{result['electricity_price']:>10.2f}"
            f"{result['threshold']:>15.4f}"
            f"{result['charging_probability']:>15.4f}"
            f"{result['expected_charging_evs']:>15.4f}"
        )


# ============================================================
# 9. Queue Capacity Experiment
# ============================================================

def capacity_sensitivity(
    base_config: SimulationConfig,
    capacities: List[int],
) -> List[Dict[str, float]]:
    """
    Test how the number of charging piles affects equilibrium.
    """

    results = []

    for capacity in capacities:

        config = SimulationConfig(
            n_evs=base_config.n_evs,
            battery_capacity=base_config.battery_capacity,
            target_soc=base_config.target_soc,
            electricity_price=base_config.electricity_price,
            distance_to_station=base_config.distance_to_station,
            safe_range=base_config.safe_range,
            maximum_range=base_config.maximum_range,
            lambda_risk=base_config.lambda_risk,
            alpha=base_config.alpha,
            charging_piles=capacity,
            charging_power=base_config.charging_power,
            waiting_cost_per_hour=base_config.waiting_cost_per_hour,
            existing_queue_time=base_config.existing_queue_time,
            random_seed=base_config.random_seed,
            initial_threshold=base_config.initial_threshold,
            tolerance=base_config.tolerance,
            max_iterations=base_config.max_iterations,
            grid_size=base_config.grid_size,
        )

        parameters = build_bne_parameters(
            config
        )

        result = solve_bne(
            parameters=parameters,
            initial_threshold=config.initial_threshold,
            tolerance=config.tolerance,
            max_iterations=config.max_iterations,
            grid_size=config.grid_size,
        )

        results.append(
            {
                "charging_piles": capacity,
                "threshold": result.threshold,
                "charging_probability": (
                    result.charging_probability
                ),
                "expected_charging_evs": (
                    result.expected_charging_evs
                ),
            }
        )

    return results


def print_capacity_sensitivity(
    results: List[Dict[str, float]],
) -> None:
    """
    Print charging-pile sensitivity results.
    """

    print("\n[Charging Capacity Sensitivity]")

    print(
        f"{'Piles':>10}"
        f"{'Threshold':>15}"
        f"{'P(Charge)':>15}"
        f"{'E[Chargers]':>15}"
    )

    print("-" * 55)

    for result in results:

        print(
            f"{result['charging_piles']:>10}"
            f"{result['threshold']:>15.4f}"
            f"{result['charging_probability']:>15.4f}"
            f"{result['expected_charging_evs']:>15.4f}"
        )


# ============================================================
# 10. Main
# ============================================================

def main() -> None:
    """
    Main entry point for the Stage 04 simulation.
    """

    config = SimulationConfig()

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    run_baseline_simulation(
        config
    )

    # --------------------------------------------------------
    # Price experiment
    # --------------------------------------------------------

    price_results = price_sensitivity(
        base_config=config,
        prices=[
            0.20,
            0.30,
            0.40,
            0.50,
        ],
    )

    print_price_sensitivity(
        price_results
    )

    # --------------------------------------------------------
    # Charging capacity experiment
    # --------------------------------------------------------

    capacity_results = capacity_sensitivity(
        base_config=config,
        capacities=[
            2,
            4,
            6,
            8,
        ],
    )

    print_capacity_sensitivity(
        capacity_results
    )


# ============================================================
# Standalone Execution
# ============================================================

if __name__ == "__main__":
    main()
