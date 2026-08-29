# 03 — EV Charging Model

A Python implementation of the EV charging decision model that serves as the computational foundation for the subsequent paper replication.

This project translates the mathematical structure of an electric vehicle (EV) charging decision problem into modular and testable Python code.

The model focuses on:

- State of Charge (SoC)
- Safe and danger SoC thresholds
- Range anxiety
- Charging energy
- Charging time
- Charging station capacity
- Queueing time
- Charging cost
- Queueing cost
- Total utility

This module serves as the foundation for **04 — Paper Replication**, where the EV charging environment will be combined with Bayesian game theory and equilibrium analysis.

---

## 1. Research Workflow

This project is organized into five stages:

```text
01 — Game Theory
        ↓
02 — Bayesian Game
        ↓
03 — EV Charging Model
        ↓
04 — Paper Replication
        ↓
05 — Extension
```

The purpose of Stage 03 is to convert the mathematical EV charging model into a working computational environment.

---

## 2. Model Overview

An EV driver must decide whether to charge at a charging station before continuing the trip.

The decision depends on several factors:

1. Current battery State of Charge (SoC)
2. Distance to the next charging station
3. Safe driving range
4. Maximum driving range
5. Range anxiety
6. Electricity price
7. Charging time
8. Expected queueing time
9. Driver-specific cost of waiting

The computational structure is:

```text
Current SoC
    ↓
Safe / Danger SoC
    ↓
Range Anxiety
    ↓
Charging Requirement
    ↓
Charging Time
    ↓
Expected Queue
    ↓
Charging Cost + Queueing Cost
    ↓
Total Utility
```

---

## 3. State of Charge

Let:

- $SoC_i$ denote the current state of charge of EV $i$.
- $V_i$ denote the battery capacity.
- $SoC_{t,i}$ denote the target state of charge.

The state of charge is normalized to:

$$
0 \leq SoC_i \leq 1
$$

For example:

```text
SoC = 0.20  → 20%
SoC = 0.50  → 50%
SoC = 0.80  → 80%
```

---
## 4. Safe State of Charge

Let:

* $d_i$ be the distance to the next charging station.
* $d_{s,i}$ be the safe driving range.

The safe SoC threshold is:

$$
SoC_{s,i} = \frac{d_i}{d_{s,i}} \quad \text{if } d_i < d_{s,i}, \qquad SoC_{s,i} = 1 \quad \text{if } d_i \geq d_{s,i}
$$

The interpretation is:

```text
SoC ≥ Safe SoC
    ↓
No range anxiety

SoC < Safe SoC
    ↓
Range anxiety may occur
```

---

## 5. Danger State of Charge

Let $d_{0,i}$ denote the theoretical maximum driving range.

The danger SoC threshold is:

$$
SoC_{d,i} = \frac{d_i}{d_{0,i}} \quad \text{if } d_i < d_{0,i}, \qquad SoC_{d,i} = 1 \quad \text{if } d_i \geq d_{0,i}
$$

This creates three regions:

```text
0%                SoC_d                 SoC_s                100%
|-------------------|---------------------|----------------------|
       Danger            Range Anxiety             Safe
```

The interpretation is:

```text
SoC < SoC_d
    ↓
Driving without charging is infeasible

SoC_d ≤ SoC < SoC_s
    ↓
Range anxiety exists

SoC ≥ SoC_s
    ↓
No range anxiety
```

---

## 6. Range Anxiety

Range anxiety is modeled as:

$$
A_i =
\begin{cases}
0, & SoC_i \geq SoC_{s,i} \\
\lambda_i (SoC_{s,i} - SoC_i)^{\alpha_i},
& SoC_{d,i} \leq SoC_i < SoC_{s,i} \\
\infty, & SoC_i < SoC_{d,i}
\end{cases}
$$

where:

- $\lambda_i$ controls the intensity of range anxiety.
- $\alpha_i$ controls the curvature of the anxiety function.

The basic relationship is:

$$
SoC_i \downarrow
\quad\Rightarrow\quad
A_i \uparrow
$$

Therefore, lower battery levels generate stronger incentives to charge.

---

## 7. Charging Energy

The energy required to reach the target SoC is:

$$
E_i =
V_i
\left(
SoC_{t,i} - SoC_i
\right)
$$

If the current SoC is already above the target SoC, the required charging energy is set to zero.

For example:

```text
Battery capacity = 80 kWh
Current SoC      = 20%
Target SoC       = 80%

Required energy
= 80 × (0.80 - 0.20)
= 48 kWh
```

---

## 8. Charging Time

Let $\eta$ denote charging power.

Charging time is:

$$
T_i =
\frac{
V_i(SoC_{t,i} - SoC_i)
}{
\eta
}
$$

Equivalently:

$$
T_i =
\frac{E_i}{\eta}
$$

Therefore:

$$
E_i \uparrow
\quad\Rightarrow\quad
T_i \uparrow
$$

---

## 9. Queueing Time

Suppose:

- $c(N)$ EVs choose to charge.
- $k$ charging piles are available.
- $E[T]$ is expected charging time.
- $t_0$ is the existing queueing time.

The expected queueing time is modeled as:

$$
t =
\frac{c(N)-1}{2k}E[T] + t_0
$$

This captures the strategic interaction created by congestion.

As the number of charging EVs increases:

$$
c(N) \uparrow
\quad\Rightarrow\quad
t \uparrow
$$

As the number of charging piles increases:

$$
k \uparrow
\quad\Rightarrow\quad
t \downarrow
$$

---

## 10. Charging Utility

Let $P$ denote the electricity price.

The charging cost is:

$$
C_i = E_i P
$$

The corresponding utility component is:

$$
\Pi_{c,i} = -C_i
$$

Therefore:

$$
\Pi_{c,i} = -V_i(SoC_{t,i} - SoC_i)P
$$

Charging creates a direct monetary cost.

---

## 11. Queueing Utility

Let $\mu_{q,i}$ denote the driver's cost of waiting.

The queueing utility is:

$$
\Pi_{q,i} = -\mu_{q,i}t
$$

Therefore:

$$
t \uparrow
\quad\Rightarrow\quad
\Pi_{q,i} \downarrow
$$

Drivers who dislike waiting more strongly will place a higher cost on charging-station congestion.

---

## 12. Total Utility

The total utility combines:

1. Range anxiety
2. Charging cost
3. Queueing cost

Conceptually:

$$
\Pi_i = \Pi_{a,i} + \Pi_{c,i} + \Pi_{q,i}
$$

For a charging EV:

$$
\Pi_i^{\mathrm{charge}} = \Pi_{c,i} + \Pi_{q,i}
$$

For an EV that does not charge:

$$
\Pi_i^{\mathrm{no\ charge}} = \Pi_{a,i}
$$

The charging decision can therefore be represented as:

$$
\text{Charge if}
\qquad
\Pi_i^{\mathrm{charge}} >
\Pi_i^{\mathrm{no\ charge}}
$$

This utility comparison becomes the basis for the Bayesian equilibrium analysis in Stage 04.


## 13. Repository Structure

```text
03_ev_charging_model/
│
├── README.md
├── ev_model.py
├── range_anxiety.py
├── charging_station.py
├── queue_model.py
├── utility.py
├── simulation.py
├── requirements.txt
│
└── tests/
    ├── test_range_anxiety.py
    ├── test_queue.py
    └── test_utility.py
```

---

## 14. File Description

| File | Description |
|---|---|
| `README.md` | Documentation and mathematical model |
| `ev_model.py` | EV driver model and SoC thresholds |
| `range_anxiety.py` | Range anxiety calculation |
| `charging_station.py` | Charging station parameters |
| `queue_model.py` | Charging time and queueing model |
| `utility.py` | Utility functions |
| `simulation.py` | Complete simulation example |
| `requirements.txt` | Python dependencies |
| `tests/` | Unit tests |

---

## 15. Equation-to-Code Mapping

| Mathematical Component | Python Implementation |
|---|---|
| Current SoC | `EV.soc` |
| Battery capacity | `EV.battery_capacity` |
| Target SoC | `EV.target_soc` |
| Safe SoC | `EV.safe_soc` |
| Danger SoC | `EV.danger_soc` |
| Range anxiety | `calculate_range_anxiety()` |
| Charging energy | `charging_energy()` |
| Charging time | `charging_time()` |
| Queueing time | `expected_queue_time()` |
| Charging utility | `charging_utility()` |
| Queueing utility | `queue_utility()` |
| Total utility | `total_utility()` |

---

## 16. Installation

Enter the project directory:

```bash
cd 03_ev_charging_model
```

Install the required dependency:

```bash
pip install -r requirements.txt
```

---

## 17. Run the Simulation

Run:

```bash
python simulation.py
```

The simulation reports:

- EV SoC
- Safe SoC
- Danger SoC
- Range anxiety
- Charging energy
- Charging time
- Expected queueing time
- Utility when charging
- Utility when not charging
- Preferred charging decision

---

## 18. Run Tests

Run:

```bash
pytest
```

The tests verify the mathematical implementation of:

- Range anxiety
- Charging energy
- Charging time
- Queueing time
- Charging utility
- Queueing utility
- Total utility

---

## 19. Research Interpretation

Stage 03 should be understood as the **computational environment**, rather than the complete game-theoretic solution.

The model separates the problem into two layers.

### EV Environment

```text
Battery
   ↓
SoC
   ↓
Range
   ↓
Charging Requirement
   ↓
Charging Time
   ↓
Queue
```

### Economic Decision

```text
Range Anxiety
      +
Charging Cost
      +
Queueing Cost
      ↓
Total Utility
      ↓
Charging Decision
```

The second layer will become strategically interactive when multiple EVs make decisions simultaneously.

---

## 20. Connection to Stage 04

The next stage introduces Bayesian game theory.

Stage 04 will build on this module by adding:

```text
Private Type
     ↓
Belief
     ↓
Expected Utility
     ↓
Strategic Interaction
     ↓
Best Response
     ↓
Threshold
     ↓
Bayesian Nash Equilibrium
```

The current module therefore provides the payoff structure required by the Bayesian game.

---

## 21. Reproducibility

The implementation is designed to be:

- modular;
- transparent;
- testable;
- reproducible;
- directly connected to the mathematical formulation.

Each major component of the model is implemented as an independent Python function or class.

This makes it possible to verify the mathematical model before introducing the more complex Bayesian equilibrium calculations.

---

## 22. Project Roadmap

### 01 — Game Theory

Basic strategic interaction and utility concepts.

### 02 — Bayesian Game

Private information, beliefs, expected utility, and Bayesian Nash equilibrium.

### 03 — EV Charging Model

Implementation of the EV charging environment.

### 04 — Paper Replication

Reproduce the paper's Bayesian charging model, equilibrium algorithm, numerical experiments, and key results.

### 05 — Extension

Develop and evaluate a new model or extension based on limitations identified during replication.

---

## 23. License

This project is intended for academic research, learning, and reproducibility purposes.
