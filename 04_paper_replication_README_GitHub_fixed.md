# 04 — Paper Replication

This module implements the mathematical models, Bayesian game formulation, and solution procedures presented in:

> **Yan, H., & Tang, X.**
> *Incorporating Bounded Rationality into Electric Vehicle Highway Charging Decisions: A Bayesian Game Analysis.*
> **IEEE Internet of Things Journal**, 2025, 12(11), 15249–15260.
> DOI: `10.1109/JIOT.2025.3530449`

The purpose of this module is to build an **independent Python implementation** of the paper's mathematical framework and algorithms, with each major model component separated into an interpretable function and validated against the paper's formulation.

> **Current status:** Paper replication — mathematical model implementation, equation-level validation, and data-reproduction stage.

---

# 1. Paper Overview

The paper studies EV highway charging decisions when drivers do not behave as perfectly rational decision makers.

The key idea is to combine:

```text
Bounded Rationality
        +
Prospect Theory
        +
Bayesian Game
        +
EV Highway Charging
```

The paper focuses on the following decision problem:

> **Given uncertainty about other EV drivers' charging decisions, how should an EV driver decide whether to charge while balancing range anxiety, charging cost, and queuing cost?**

The model captures the fact that drivers may reserve more battery energy than is theoretically necessary because of **range anxiety and risk aversion**.

The paper then models the interaction among EV drivers as a **Bayesian game with incomplete information**.

---

# 2. Research Logic

The mathematical structure implemented in this module can be summarized as:

```text
EV / Trip Information
        │
        ├── Initial SoC
        ├── Destination
        ├── Travel Distance
        └── Vehicle Characteristics
                │
                ↓
        Range Anxiety
                │
                ↓
        Driver Type
        / Risk Preference
                │
                ↓
       Charging Decision
                │
       ┌────────┼─────────┐
       ↓        ↓         ↓
 Range Anxiety  Charging  Queueing
     Cost         Fee       Cost
       └────────┼─────────┘
                ↓
          Total Cost
                ↓
       Bayesian Game
                ↓
 Bayesian Nash Equilibrium
                ↓
    Charging Decisions
                ↓
   Network-level Outcomes
```

The implementation follows this logical chain rather than treating the equations as independent calculations.

---

# 3. Model Components

## 3.1 EV Charging Decision

The fundamental decision of an EV driver is whether to charge during the highway trip.

The driver's decision is affected by:

* remaining State of Charge (SoC);
* travel distance;
* destination;
* charging fee;
* expected waiting time;
* range anxiety;
* behavioral type / risk preference;
* other drivers' charging decisions.

The action space is represented by the charging decision used in the paper's game formulation.

---

# 4. Bounded Rationality and Prospect Theory

A central feature of the paper is that EV drivers are not assumed to have perfect rationality.

Instead, the model incorporates behavioral characteristics through **prospect theory**.

The main behavioral implication is that drivers may perceive the risk of insufficient battery energy differently from a perfectly rational benchmark.

This produces a tendency to maintain a higher perceived safety margin.

In the implementation, the behavioral parameter is separated from the physical EV state so that the effect of risk preference can be studied independently.

---

# 5. Range Anxiety

Range anxiety represents the driver's perceived cost or risk associated with insufficient remaining battery energy.

The relevant EV state is determined by variables such as:

```text
Initial SoC
Travel Distance
Destination Distance
Battery / Vehicle Parameters
Safety Requirement
```

The resulting range-anxiety component enters the driver's total cost.

The corresponding implementation is separated into the EV model and paper-specific payoff calculations.

---

# 6. Driver Type

The Bayesian game requires uncertainty about the characteristics of other EV drivers.

A driver is therefore associated with a private type related to behavioral characteristics.

The implementation provides explicit representations of the type distribution.

### Current implementation

```text
type_distribution.py
```

This module currently supports:

* continuous type distributions;
* discrete type distributions;
* uniform-type representations used in numerical validation.

For example, the current replication uses a uniform distribution when reproducing the paper's corresponding numerical setting.

---

# 7. Cost Structure

The driver's objective is to minimize the overall cost associated with a charging decision.

The implementation separates the main cost components:

```text
Total Cost
    =
Range Anxiety Cost
+
Charging Cost
+
Queuing Cost
```

The paper's Bayesian game is therefore not simply a charging-price optimization problem.

The charging decision represents a trade-off between:

* charging now;
* paying the charging fee;
* waiting in a queue;
* and reducing the risk/cost associated with insufficient battery energy.

---

# 8. Expected Cost

Because an EV driver does not know the private information and actions of other drivers, the driver evaluates decisions using expected cost.

The expected-cost formulation is implemented in:

```text
expected_cost.py
```

The purpose of this module is to translate uncertain information about other drivers into an expected decision cost.

Conceptually:

```text
Unknown Other Drivers
        ↓
Type Distribution
        ↓
Possible Actions
        ↓
Expected Cost
        ↓
Best Response
```

This is the key step connecting the EV cost model to the Bayesian game.

---

# 9. Bayesian Game Formulation

The EV charging problem is formulated as a Bayesian game because drivers possess incomplete information about other players.

The game contains:

### Players

EV drivers traveling on the highway.

### Types

Private behavioral / state information associated with individual drivers.

### Actions

Charging decisions.

### Payoffs / Costs

The total perceived cost associated with each charging decision.

### Beliefs

Probability distributions over the types and decisions of other players.

The objective is to find a strategy profile in which no player can reduce expected cost by unilaterally changing their strategy.

This corresponds to the **Bayesian Nash Equilibrium (BNE)**.

---

# 10. Bayesian Nash Equilibrium

The core solver is:

```text
bne_solver.py
```

The solver implements the paper-specific equilibrium calculation rather than relying on a generic game-theory package.

The main structure is:

```text
Driver Type
      ↓
Expected Cost
      ↓
Best Response
      ↓
Equilibrium Condition
      ↓
Bayesian Nash Equilibrium
```

The implementation contains the mathematical relationships corresponding to the paper's equations and the equilibrium algorithms.

---

# 11. Equation-to-Code Mapping

A major design principle of this replication is:

> **Each important equation should correspond to an identifiable implementation component.**

The current implementation is organized around the following equation groups.

| Paper Component             | Implementation             |
| --------------------------- | -------------------------- |
| EV / trip variables         | `bne_solver.py`            |
| Safety / SoC relationships  | `bne_solver.py`            |
| Range-anxiety relationships | `bne_solver.py` / EV model |
| Expected cost               | `expected_cost.py`         |
| Type distribution           | `type_distribution.py`     |
| Payoff / total cost         | `payoff.py`                |
| Bayesian best response      | `bne_solver.py`            |
| BNE conditions              | `bne_solver.py`            |
| Algorithm 1                 | `bne_solver.py`            |
| Algorithm 2                 | `bne_solver.py`            |
| Numerical validation        | `simulation.py`            |

The objective is to make the implementation traceable from the paper's mathematical formulation to executable code.

---

# 12. Algorithm 1 — BNE Without Destination Distribution

The first practical scenario considers the Bayesian equilibrium without explicitly incorporating the destination distribution into the equilibrium calculation.

The corresponding implementation is:

```text
algorithm1_bne_without_destination_distribution()
```

The computational logic is:

```text
EV Information
      ↓
Driver Type
      ↓
Expected Cost
      ↓
Best Response
      ↓
Equilibrium Threshold
      ↓
BNE
```

The implementation is validated using deterministic and stochastic parameter settings corresponding to the paper's numerical framework.

---

# 13. Algorithm 2 — BNE With Destination Distribution

The second practical scenario incorporates information about destination distribution.

The corresponding implementation is:

```text
algorithm2_bne_with_destination_distribution()
```

The algorithm introduces an additional relationship between:

```text
Destination
     ↓
Charging Need
     ↓
Driver Distribution
     ↓
Expected Charging Behavior
     ↓
Equilibrium
```

The implementation explicitly handles the intermediate quantities used by the paper's algorithm, including:

```text
m
h(m)
destination threshold
```

The purpose is to reproduce the destination-aware equilibrium calculation rather than treating destination information as an external simulation parameter.

---

# 14. Paper Equations

The current implementation follows the mathematical framework from the paper's equation system.

The solver contains implementations corresponding to:

```text
Eq. (1)
Eq. (2)
Eq. (3)
Eq. (4)
Eq. (5)
Eq. (6)
Eq. (7)
Eq. (8)
...
Eq. (21)
```

The equations are implemented as separate logical components rather than being collapsed into one large numerical procedure.

This makes it possible to validate:

1. individual equations;
2. intermediate quantities;
3. equilibrium conditions;
4. complete algorithms.

---

# 15. Parameters

The implementation distinguishes between three types of parameters.

## 15.1 Model Parameters

Parameters defined by the mathematical model.

Examples include:

```text
α
λ
μq
μa
SoCt
```

where the exact interpretation follows the paper's notation.

---

## 15.2 Numerical Example Parameters

Parameters used for specific numerical demonstrations.

Examples include:

```text
d0
ds
V
t0
```

These are used only when reproducing the corresponding numerical scenarios.

---

## 15.3 Experimental / Validation Parameters

Parameters introduced for:

* debugging;
* sensitivity analysis;
* synthetic-data experiments;
* implementation validation.

These are explicitly distinguished from parameters directly reported by the paper.

---

# 16. Numerical Validation

The validation framework is designed to compare the implementation against the mathematical relationships and numerical behavior described in the paper.

The validation process follows:

```text
Equation
   ↓
Intermediate Variable
   ↓
Algorithm
   ↓
Numerical Example
   ↓
Simulation Result
```

Current validation includes:

* expected-cost calculations;
* type-distribution calculations;
* payoff calculations;
* BNE conditions;
* Algorithm 1;
* Algorithm 2;
* selected numerical reference cases.

---

# 17. Current Validation Status

### Completed

* [x] Paper mathematical structure identified
* [x] EV state representation
* [x] Type-distribution implementation
* [x] Expected-cost implementation
* [x] Payoff implementation
* [x] Bayesian Nash equilibrium solver
* [x] Algorithm 1 implementation
* [x] Algorithm 2 implementation
* [x] Initial equation-level validation
* [x] Initial numerical validation

### In Progress

* [ ] Complete equation-by-equation validation
* [ ] Full reproduction of all numerical experiments
* [ ] Real-data preprocessing
* [ ] Traffic-data interface
* [ ] End-to-end simulation
* [ ] Comparison with all paper-reported results
* [ ] Reproduction of network-level charging-demand results

---

# 18. Data and Simulation

The paper's numerical experiments use real-life data to investigate the impact of driver risk aversion on:

* EV charging decisions;
* charging demand;
* queue lengths;
* departure rates;
* EV costs;
* charging-station costs.

The current repository is still at the **data reproduction stage**.

Therefore, the current implementation distinguishes between:

```text
Paper Model
     ↓
Synthetic / Controlled Validation
```

and the future:

```text
Real Traffic / EV Data
     ↓
Paper Parameterization
     ↓
BNE Solver
     ↓
Network Simulation
     ↓
Paper-level Numerical Results
```

A dedicated data interface will be added before attempting full real-data reproduction.

---

# 19. Simulation Pipeline

The intended complete pipeline is:

```text
Traffic / EV Data
        ↓
EV Initialization
        ↓
Destination & Distance
        ↓
SoC
        ↓
Driver Type
        ↓
Range Anxiety
        ↓
Charging / Queue Costs
        ↓
Expected Cost
        ↓
BNE Solver
        ↓
Charging Decision
        ↓
Charging Demand
        ↓
Queue Length
        ↓
Departure Rate
        ↓
Cost Analysis
```

The current implementation has completed the core model and equilibrium components.

The end-to-end data-driven simulation remains under development.

---

# 20. File Structure

```text
04_paper_replication/
│
├── expected_cost.py
│
├── type_distribution.py
│
├── payoff.py
│
├── bne_solver.py
│
├── simulation.py
│
└── README.md
```

### `expected_cost.py`

Implements expected-cost calculations under incomplete information.

### `type_distribution.py`

Defines the behavioral / private-type distributions used by the Bayesian game.

### `payoff.py`

Computes the paper-specific payoff / cost structure.

### `bne_solver.py`

Core mathematical implementation of the paper's Bayesian Nash equilibrium formulation.

Contains:

* EV representation;
* destination representation;
* SoC-related equations;
* cost relationships;
* equilibrium conditions;
* Algorithm 1;
* Algorithm 2;
* validation functions.

### `simulation.py`

Provides the numerical execution layer for testing the implemented model and algorithms.

---

# 21. Design Principle

The implementation follows three principles.

## 21.1 Paper First

The code is based on the mathematical formulation in the paper rather than introducing a new model.

## 21.2 Equation Traceability

Important mathematical relationships should be traceable to specific functions.

```text
Paper Equation
      ↓
Python Function
      ↓
Validation
```

## 21.3 Implementation ≠ Validation

The mathematical implementation and validation procedures are kept separate.

This allows a numerical failure to be identified as either:

* an implementation problem;
* a parameter problem;
* or a validation / reproduction problem.

---

# 22. Reproduction Status

This repository should currently be understood as an:

> **Independent Python implementation and reproduction attempt**

rather than an official implementation of the paper.

The project does **not** claim that the complete numerical results of the paper have already been reproduced.

The current goal is to progressively establish:

```text
Mathematical Correctness
        ↓
Algorithmic Correctness
        ↓
Numerical Reproduction
        ↓
Data-driven Reproduction
```

---

# 23. Next Steps

The next development stages are:

### Stage 1 — Equation Validation

Complete a one-to-one check between the paper's equations and the Python implementation.

### Stage 2 — Data Interface

Implement:

```text
traffic_data.py
```

with separate interfaces for:

* synthetic data;
* real data.

### Stage 3 — End-to-End Simulation

Connect:

```text
traffic_data
      ↓
bne_solver
      ↓
simulation
```

to create a complete charging-decision pipeline.

### Stage 4 — Numerical Reproduction

Reproduce the paper's numerical experiments and compare:

* charging demand;
* queue length;
* departure rate;
* EV cost;
* charging-station cost.

### Stage 5 — Extension

Only after the reproduction is stable, investigate possible extensions such as:

* alternative driver distributions;
* sensitivity to risk aversion;
* alternative traffic conditions;
* additional charging-network scenarios;
* optimization extensions.

---

# 24. Reference

**Yan, H., & Tang, X. (2025).**

*Incorporating Bounded Rationality Into Electric Vehicle Highway Charging Decisions: A Bayesian Game Analysis.*

IEEE Internet of Things Journal, 12(11), 15249–15260.

DOI:

```text
10.1109/JIOT.2025.3530449
```

The authors' work provides the mathematical and experimental basis for this independent Python reproduction project.

---

## Current Status

**Paper:** EV highway charging decisions under bounded rationality

**Method:** Prospect Theory + Bayesian Game

**Implementation:** Independent Python reproduction

**Current stage:** Model implementation + equation-level validation + data reproduction

**Next milestone:** Synthetic/real data interface → end-to-end simulation → numerical reproduction
