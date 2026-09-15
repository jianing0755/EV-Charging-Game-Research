
# EV Charging Game Research

A research-oriented implementation and reproduction project based on:

> **Yan, H., & Tang, X. (2025).**
> *Incorporating Bounded Rationality into Electric Vehicle Highway Charging Decisions: A Bayesian Game Analysis.*
> **IEEE Internet of Things Journal, 12(11), 15249–15260.**
> DOI: 10.1109/JIOT.2025.3530449

This project aims to understand and reproduce the mathematical models, Bayesian game framework, EV charging behavior model, and numerical procedures presented in the paper.

---

## 1. Research Motivation

Electric vehicle (EV) charging decisions on highways are influenced by several interacting factors:

* remaining battery state;
* range anxiety;
* charging cost;
* charging station congestion;
* queuing time;
* travel distance;
* and the charging decisions of other EV drivers.

The paper studies this problem under **bounded rationality** and models EV drivers' charging decisions as a **Bayesian game with incomplete information**.

The central research question is:

> **How should an EV driver decide whether to charge when the driver's own state is known, but the decisions and types of other EV drivers are uncertain?**

The paper further studies how these individual decisions affect charging demand, queue lengths, and EV departures from the highway network.

---

## 2. Project Objective

The goal of this repository is not simply to reproduce numerical results.

It is designed as a step-by-step research implementation that connects:

```text
Game Theory
      ↓
Bayesian Game
      ↓
EV Charging Decision Model
      ↓
Bayesian Nash Equilibrium
      ↓
Paper-specific Algorithms
      ↓
Simulation and Numerical Analysis
```

The implementation separates general theoretical components from paper-specific components so that each equation, model assumption, and algorithm can be independently tested.

---

## 3. Project Structure

```text
EV-Charging-Game-Research/
│
├── 01_game_theory_basics/
│   ├── best_response.py
│   ├── nash_equilibrium.py
│   └── README.md
│
├── 02_bayesian_game/
│   ├── bayesian_best_response.py
│   ├── expected_cost.py
│   └── README.md
│
├── 03_ev_charging_model/
│   ├── ev_model.py
│   ├── range_anxiety.py
│   ├── charging_station.py
│   ├── queue_model.py
│   ├── utility.py
│   ├── simulation.py
│   ├── requirements.txt
│   └── README.md
│
├── 04_paper_replication/
│   ├── expected_cost.py
│   ├── type_distribution.py
│   ├── payoff.py
│   ├── bne_solver.py
│   ├── simulation.py
│   └── README.md
│
├── 05_extension/
│   └── ...
│
└── README.md
```

---

# 4. Module 01 — Game Theory Basics

### Purpose

This module establishes the basic concepts required to understand the paper's game-theoretic formulation.

### Main concepts

* Nash equilibrium
* Best response
* Payoff / cost
* Strategic interaction

### Main files

| File                  | Purpose                           |
| --------------------- | --------------------------------- |
| `best_response.py`    | Computes a player's best response |
| `nash_equilibrium.py` | Identifies Nash equilibrium       |

This module provides the theoretical foundation for the Bayesian game developed later.

---

# 5. Module 02 — Bayesian Game

The paper considers a decision-making environment with incomplete information.

An EV driver does not necessarily know the private information or charging decisions of other drivers.

This motivates the Bayesian game formulation.

### Main concepts

* Player type
* Type distribution
* Expected cost
* Bayesian best response
* Bayesian Nash equilibrium

### Main files

| File                        | Purpose                                   |
| --------------------------- | ----------------------------------------- |
| `bayesian_best_response.py` | Computes Bayesian best responses          |
| `expected_cost.py`          | Computes expected costs under uncertainty |

The purpose of this module is to bridge general game theory and the specific EV charging problem.

---

# 6. Module 03 — EV Charging Model

This module translates the abstract game-theoretic concepts into the EV highway charging scenario.

The model considers the main components of an EV driver's charging decision:

```text
EV State
   │
   ├── State of Charge (SoC)
   │
   ├── Travel Distance
   │
   └── Destination
          ↓
   Range Anxiety
          ↓
   Charging Decision
          ↓
 ┌────────┼─────────┐
 ↓        ↓         ↓
Charging Queue    Travel
Cost     Cost      Cost
 └────────┼─────────┘
          ↓
       Total Cost
```

### Main components

#### EV model

Represents vehicle state and charging-related variables.

#### Range anxiety

Models the driver's perceived cost associated with insufficient remaining battery energy.

#### Charging station

Represents charging-related characteristics.

#### Queue model

Models congestion and waiting time at charging stations.

#### Utility / Cost

Combines the relevant components into the driver's decision objective.

---

# 7. Module 04 — Paper Replication

This module implements the mathematical framework and algorithms described in the target paper.

### Target paper

> Yan, H., & Tang, X.
> *Incorporating Bounded Rationality into Electric Vehicle Highway Charging Decisions: A Bayesian Game Analysis.*

The implementation follows the paper's equations and algorithms as closely as possible.

---

## 7.1 Mathematical Model

The replication covers the main components of the paper's mathematical formulation, including:

* EV state variables;
* charging decisions;
* destination information;
* bounded-rational charging behavior;
* range anxiety;
* charging cost;
* queuing cost;
* expected cost;
* player types;
* payoff / cost functions;
* Bayesian best responses;
* Bayesian Nash equilibrium.

Each major mathematical component is implemented as an independent Python function where possible.

This design makes it easier to compare the implementation against the corresponding equations in the paper.

---

## 7.2 Bayesian Nash Equilibrium

The core of the replication is the computation of the **Bayesian Nash Equilibrium (BNE)**.

The implementation currently includes:

### Setting 1

A scenario where destination-related information is not explicitly incorporated into the distribution of other drivers' destinations.

Implemented through:

```text
Algorithm 1
BNE without destination distribution
```

### Setting 2

A scenario that explicitly incorporates destination distribution into the equilibrium calculation.

Implemented through:

```text
Algorithm 2
BNE with destination distribution
```

The solver contains implementations corresponding to the paper's equations and intermediate quantities, including:

```text
Eq. (01) — Eq. (21)
```

where applicable to the current replication scope.

---

# 8. Parameterization

The implementation distinguishes between:

### Paper-defined parameters

Parameters explicitly specified by the paper or its model formulation.

Examples include:

```text
α
λ
μq
μa
SoCt
```

### Numerical-example parameters

Parameters used for specific numerical demonstrations or validation cases.

### Experimental parameters

Parameters introduced only for testing, debugging, or synthetic experiments.

This distinction is maintained to avoid confusing paper assumptions with implementation choices.

---

# 9. Validation

The project separates **model implementation** from **validation**.

Current validation focuses on:

* equation-level consistency;
* expected-cost calculations;
* payoff calculations;
* type distributions;
* Bayesian best responses;
* Algorithm 1;
* Algorithm 2;
* numerical reference cases from the paper.

Example validation structure:

```text
MODEL IMPLEMENTATION
        ↓
EQUATION VALIDATION
        ↓
ALGORITHM VALIDATION
        ↓
NUMERICAL REFERENCE CASE
```

This separation is intended to make errors in the mathematical implementation easier to identify.

---

# 10. Current Progress

### Completed

* [x] Basic game theory implementation
* [x] Nash equilibrium / best-response foundations
* [x] Bayesian game foundations
* [x] Expected-cost formulation
* [x] EV charging model
* [x] Range-anxiety component
* [x] Charging-station model
* [x] Queue model
* [x] Utility / cost formulation
* [x] Paper-specific parameterization
* [x] Paper-specific payoff formulation
* [x] Bayesian Nash equilibrium solver
* [x] Algorithm 1 implementation
* [x] Algorithm 2 implementation
* [x] Initial numerical validation

### In progress

* [ ] Synthetic traffic-data interface
* [ ] Real-data interface
* [ ] End-to-end simulation pipeline
* [ ] Reproduction of the paper's numerical experiments
* [ ] Comparison with paper-reported results
* [ ] Visualization of charging demand and queue behavior

### Future extension

* [ ] More realistic traffic / demand data
* [ ] Sensitivity analysis
* [ ] Alternative behavioral assumptions
* [ ] Additional charging-network scenarios
* [ ] Potential optimization extensions

---

# 11. Research Pipeline

The intended final pipeline is:

```text
Traffic / EV Data
       ↓
EV State Initialization
       ↓
Driver Type Distribution
       ↓
Range Anxiety
       ↓
Charging Cost
       ↓
Queueing Cost
       ↓
Expected Cost
       ↓
Bayesian Best Response
       ↓
Bayesian Nash Equilibrium
       ↓
Charging Decisions
       ↓
Network-Level Simulation
       ↓
Charging Demand
Queue Length
Departure Rate
Total Cost
```

This pipeline connects the individual-level game model with the network-level outcomes studied in the paper.

---

# 12. Reproducibility

The project is implemented in Python.

Create the virtual environment:

```bash
python -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run module-level tests and validation scripts according to the README of each module.

---

# 13. Research Notes

This repository is primarily a **learning and research reproduction project**.

The implementation should not be interpreted as an official implementation released by the paper's authors.

The main purpose is to:

1. understand the mathematical structure of the paper;
2. translate equations into executable code;
3. validate intermediate calculations;
4. reproduce the paper's algorithms;
5. gradually build an end-to-end simulation framework.

---

# 14. Reference

### Target Paper

Yan, H., & Tang, X. (2025).

> *Incorporating Bounded Rationality into Electric Vehicle Highway Charging Decisions: A Bayesian Game Analysis.*

IEEE Internet of Things Journal, 12(11), 15249–15260.

DOI:

```text
10.1109/JIOT.2025.3530449
```

### Authors' Code

The authors provide MATLAB code associated with the paper. This repository is an independent Python implementation developed for research learning and reproduction.

---

# 15. Research Direction

This project is motivated by the intersection of:

```text
Operations Research
        +
Game Theory
        +
Optimization
        +
Electric Vehicle Charging
        +
Data-driven Decision Making
```

The longer-term goal is to move from reproducing an existing model toward studying practical optimization and decision-making problems in EV charging networks.

---

## Status

**Current stage: Paper reproduction and model validation**

**Primary focus: Bayesian game modeling for EV highway charging decisions**
