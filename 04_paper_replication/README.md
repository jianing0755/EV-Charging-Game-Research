# 04 — Paper Replication


## 1. Purpose of This Module

The previous modules developed the basic concepts required for this paper:

```text
01 — Game Theory
        ↓
02 — Bayesian Game
        ↓
03 — EV Charging Model
        ↓
04 — Paper Replication
```

Therefore, this module does **not** introduce Game Theory, Bayesian Games, or the EV charging model from scratch.

Instead, the purpose of Module 04 is to answer:

> **Can the mathematical framework and solution procedures of a real research paper be translated into executable Python code and systematically validated?**

The implementation focuses on connecting the paper's mathematical formulation with executable functions and numerical validation.

---

# 2. What the Paper Studies

The paper studies **EV highway charging decisions under bounded rationality**.

The key idea is that EV drivers may reserve more electricity than is theoretically necessary because of behavioral factors such as risk aversion and range anxiety.

The paper therefore combines:

```text
Bounded Rationality
        +
Prospect Theory
        +
Bayesian Game
        +
EV Highway Charging
```

The EV drivers make charging decisions under incomplete information about other drivers.

Their decision cost incorporates:

* range anxiety;
* charging fees;
* queuing time.

The paper then analyzes the resulting **Bayesian Nash Equilibrium (BNE)**.

It establishes the existence and uniqueness of the BNE in two practical scenarios and uses real-life data to study the impact of risk aversion on charging behavior and highway charging-system outcomes.

---

# 3. What Is Being Reproduced

This implementation focuses on the following parts of the paper:

### Mathematical Model

* EV state and travel variables
* State of Charge (SoC)
* safety and destination-related thresholds
* range-anxiety cost
* charging cost
* queuing cost
* expected cost
* driver type distribution
* payoff / cost functions

### Bayesian Game

* incomplete information
* driver types
* expected cost
* best-response conditions
* Bayesian Nash Equilibrium

### Equilibrium Algorithms

* Algorithm 1
* Algorithm 2
* equilibrium threshold calculation
* destination-dependent equilibrium calculation

### Numerical Validation

* equation-level checks
* intermediate-value checks
* algorithm-level validation
* numerical reference cases

The long-term goal is to connect these components to the paper's data-driven simulation and reproduce its numerical results.

---

# 4. Paper-to-Code Structure

The implementation is organized according to the mathematical structure of the paper.

```text
Paper Model
     ↓
Mathematical Equations
     ↓
Python Functions
     ↓
Equation Validation
     ↓
Algorithm Validation
     ↓
Numerical Simulation
```

The main files are:

| File                   | Role in the paper                        |
| ---------------------- | ---------------------------------------- |
| `expected_cost.py`     | Expected-cost calculations               |
| `type_distribution.py` | Driver-type distributions                |
| `payoff.py`            | Paper-specific cost / payoff formulation |
| `bne_solver.py`        | Main BNE mathematical implementation     |
| `simulation.py`        | Numerical execution and validation       |

---

# 5. Equation-to-Code Mapping

A central goal of this reproduction is to make the mathematical model traceable.

The implementation in `bne_solver.py` contains functions corresponding to the paper's major equations and intermediate quantities.

The current structure includes:

```text
Eq. (1)
Eq. (2)
Eq. (3)
Eq. (4)
...
Eq. (21)
```

Rather than putting the entire mathematical model into one calculation, the equations are implemented as separate logical components whenever possible.

For example:

```text
Paper Equation
      ↓
Python Function
      ↓
Numerical Value
      ↓
Validation
```

This makes it possible to identify whether a discrepancy comes from:

* the mathematical implementation;
* the parameter setting;
* the equilibrium algorithm;
* or the numerical experiment.

---

# 6. Main Implementation Components

## `expected_cost.py`

Implements the expected-cost calculations required when an EV driver does not know the exact state or decision of other drivers.

---

## `type_distribution.py`

Represents the distribution of driver types used by the Bayesian game.

The current implementation supports both:

* continuous type distributions;
* discrete type distributions.

The distribution can then be passed into the expected-cost and BNE calculations.

---

## `payoff.py`

Implements the paper-specific cost / payoff structure.

The purpose is to keep the definition of the driver's objective separate from the equilibrium-solving procedure.

---

## `bne_solver.py`

This is the core of the paper reproduction.

It currently contains:

* EV representation;
* destination representation;
* SoC-related calculations;
* paper-specific equations;
* expected-cost relationships;
* equilibrium conditions;
* Algorithm 1;
* Algorithm 2;
* validation functions.

The main objective is to reproduce the paper's Bayesian Nash Equilibrium calculation rather than implement a generic game solver.

---

# 7. Algorithm 1

The first equilibrium-solving procedure corresponds to the paper's first practical scenario.

The implementation is:

```python
algorithm1_bne_without_destination_distribution()
```

Conceptually:

```text
EV / Driver Information
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

The implementation is designed to reproduce the paper's equilibrium calculation under the corresponding information setting.

---

# 8. Algorithm 2

The second equilibrium-solving procedure incorporates destination-distribution information.

The implementation is:

```python
algorithm2_bne_with_destination_distribution()
```

The algorithm explicitly handles the intermediate quantities required by the paper's destination-aware formulation, including:

```text
m
h(m)
destination threshold
```

The structure is:

```text
Destination Information
        ↓
Expected Charging Behavior
        ↓
Equilibrium Condition
        ↓
Threshold Update
        ↓
BNE
```

The purpose is to reproduce the paper's second practical scenario rather than simply simulate charging behavior independently.

---

# 9. Numerical Parameters

The implementation distinguishes between parameters from the paper and parameters introduced for testing.

### Paper / Model Parameters

Examples include:

```text
α
λ
μq
μa
SoCt
```

### Numerical Example Parameters

Examples include:

```text
d0
ds
V
t0
```

### Validation / Experimental Parameters

Additional parameters may be introduced for:

* debugging;
* controlled testing;
* synthetic experiments;
* sensitivity analysis.

These should not be confused with parameters directly specified by the paper.

---

# 10. Validation Strategy

Validation is separated from the implementation itself.

The intended validation hierarchy is:

```text
Equation
   ↓
Intermediate Variable
   ↓
Cost / Payoff
   ↓
Equilibrium Condition
   ↓
Algorithm
   ↓
Numerical Example
```

Current validation focuses on:

* equation-level calculations;
* type distributions;
* expected costs;
* payoff calculations;
* BNE conditions;
* Algorithm 1;
* Algorithm 2;
* selected numerical reference cases.

---

# 11. Current Progress

### Completed

* [x] Game-theoretic foundations
* [x] Bayesian-game foundations
* [x] EV charging model
* [x] Paper-specific parameterization
* [x] Expected-cost implementation
* [x] Driver-type distribution
* [x] Payoff / cost implementation
* [x] Bayesian Nash Equilibrium solver
* [x] Algorithm 1 implementation
* [x] Algorithm 2 implementation
* [x] Initial equation-level validation
* [x] Initial numerical validation

### In Progress

* [ ] Complete equation-by-equation verification
* [ ] Synthetic traffic-data interface
* [ ] Real-data interface
* [ ] End-to-end simulation
* [ ] Full numerical reproduction
* [ ] Comparison with paper-reported results

---

# 12. Data Reproduction

The paper uses real-life data for its numerical experiments and investigates how risk aversion affects:

* EV charging decisions;
* charging demand;
* queue lengths at charging stations;
* departure rates on the highway network;
* cumulative EV cost;
* charging-station costs.

The current implementation has **not yet completed the full real-data reproduction pipeline**.

The current stage is therefore:

```text
Mathematical Model
       ↓
Equation Validation
       ↓
BNE Algorithm
       ↓
Controlled / Synthetic Validation
       ↓
[Current Stage]
Data Interface
       ↓
Real-data Reproduction
```

This distinction is intentional: the project does not claim that the complete numerical experiments of the paper have already been reproduced.

---

# 13. Reproduction Philosophy

This repository is an **independent Python reproduction**, not the official implementation of the paper.

The goal is to understand the paper at three levels:

### Level 1 — Mathematical Understanding

Understand what each equation represents.

### Level 2 — Computational Implementation

Translate the equations and algorithms into executable Python functions.

### Level 3 — Numerical Reproduction

Use the implemented model and data to reproduce the paper's reported behavior and results.

The desired workflow is:

```text
Read Paper
    ↓
Understand Equation
    ↓
Implement Function
    ↓
Validate Function
    ↓
Implement Algorithm
    ↓
Validate Algorithm
    ↓
Reproduce Numerical Results
```

---

# 14. Next Steps

The next development steps are:

### Step 1 — Complete Equation Validation

Establish a one-to-one mapping between the paper's equations and the Python implementation.

### Step 2 — Build Data Interface

Add:

```text
traffic_data.py
```

with separate interfaces for:

* synthetic data;
* real data.

### Step 3 — Complete End-to-End Simulation

Connect:

```text
traffic_data
      ↓
bne_solver
      ↓
simulation
```

### Step 4 — Reproduce Numerical Experiments

Compare the implementation against the paper's reported results.

### Step 5 — Extension

Only after the reproduction is stable, consider extensions to the model or charging-network setting.


The official paper also provides MATLAB code. This repository is an independent Python implementation developed for research learning and reproduction.

---

## Current Status

**Research stage:** Paper reproduction

**Implementation:** Independent Python implementation

**Current focus:** Mathematical model + BNE algorithms + validation

**Next milestone:** Data interface → end-to-end simulation → numerical reproduction

