# 04 — Paper Replication

A Python-based replication of the Bayesian game model proposed in:

> **Incorporating Bounded Rationality into Electric Vehicle Highway Charging Decisions: A Bayesian Game Analysis**

The purpose of this project is to reproduce the mathematical model, Bayesian Nash Equilibrium (BNE) analysis, equilibrium-solving algorithms, and selected numerical results presented in the paper.

This project builds directly on **03 — EV Charging Model**, which provides the computational environment for:

- State of Charge (SoC)
- Safe and danger SoC thresholds
- Range anxiety
- Charging energy
- Charging time
- Queueing time
- Charging cost
- Queueing cost
- Total utility

Stage 04 extends this environment into a strategic Bayesian game with incomplete information.

---

## 1. Paper Information

### Paper

**Incorporating Bounded Rationality into Electric Vehicle Highway Charging Decisions: A Bayesian Game Analysis**

### Authors

- Huanyu Yan
- Xiaoying Tang

### Publication

IEEE Internet of Things Journal, Vol. 12, No. 11, pp. 15249–15260, 2025.

### arXiv

arXiv:2608.16132

### Research Topic

The paper studies electric vehicle highway charging decisions under bounded rationality.

The authors combine:

- Prospect theory
- Range anxiety
- Charging cost
- Queueing congestion
- Bayesian game theory
- Bayesian Nash equilibrium

to model strategic charging decisions among multiple heterogeneous EV drivers.

The paper proves the existence and uniqueness of the Bayesian Nash Equilibrium under two information settings and proposes binary-search-based algorithms to obtain the equilibrium charging decisions.

The paper's source code is publicly available on GitHub.

---

## 2. Research Objective

The main objective of this project is to reproduce the computational and theoretical results of the paper using Python.

The replication proceeds in several stages:

```text
03 — EV Charging Environment
        ↓
Range Anxiety
        ↓
Charging Cost
        ↓
Queueing Cost
        ↓
Expected Utility
        ↓
Bayesian Game
        ↓
Bayesian Nash Equilibrium
        ↓
Decision Threshold
        ↓
Numerical Replication

````

The central research question is:

> How does bounded rationality, represented by range anxiety and risk aversion, affect EV highway charging decisions when multiple EV drivers interact through charging-station congestion?

The replication focuses on:

1. Reconstructing the mathematical model.
2. Implementing the Bayesian game.
3. Implementing the two BNE-solving algorithms.
4. Verifying the uniqueness and threshold structure of the equilibrium.
5. Replicating selected numerical results from the paper.
6. Creating a reproducible Python implementation that can later support Stage 05 — Extension.

---

## 3. Mathematical Model

### 3.1 State of Charge

Let:

- $SoC\_i$ denote the current state of charge of EV $i$.
- $V\_i$ denote the battery capacity.
- $SoC\_{t,i}$ denote the target state of charge.
- $d\_i$ denote the distance to the next charging station.
- $d\_{s,i}$ denote the absolutely safe driving range.
- $d\_{0,i}$ denote the theoretical maximum driving range.

The state of charge satisfies:

```math
0 \leq SoC_i \leq 1
```

---

### 3.2 Safe SoC

The safe SoC threshold is:

```math
SoC_{s,i} = \begin{cases} \dfrac{d_i}{d_{s,i}}, & d_i < d_{s,i}, \\[6pt] 1, & d_i \geq d_{s,i}. \end{cases}
```

The safe threshold represents the SoC level above which the driver perceives the next charging station as safely reachable.

---

### 3.3 Danger SoC

The danger SoC threshold is:

```math
SoC_{d,i} = \begin{cases} \dfrac{d_i}{d_{0,i}}, & d_i < d_{0,i}, \\[6pt] 1, & d_i \geq d_{0,i}. \end{cases}
```

The three regions are:

```text
0%                 SoC_d                 SoC_s                100%
|---------------------|---------------------|----------------------|
       Danger              Anxiety                 Safe

```

Interpretation:

```text
SoC < SoC_d
    ↓
No-charging is infeasible

SoC_d ≤ SoC ≤ SoC_s
    ↓
Range anxiety exists

SoC ≥ SoC_s
    ↓
No range anxiety

```

---

## 4. Range Anxiety

The paper models bounded rationality using a prospect-theory-inspired range anxiety function:

```math
A_i = \begin{cases} 0, & SoC_i \geq SoC_{s,i}, \\[6pt] \lambda_i (SoC_{s,i}-SoC_i)^{\alpha_i}, & SoC_{d,i} \leq SoC_i \leq SoC_{s,i}, \\[6pt] \infty, & SoC_i < SoC_{d,i}. \end{cases}
```

where:

- $\lambda\_i$ is the loss-aversion / risk-aversion parameter.
- $\alpha\_i$ controls the curvature of the anxiety function.

Larger $\lambda\_i$ represents stronger range anxiety.

The basic relationship is:

```math
\lambda_i \uparrow \quad\Rightarrow\quad A_i \uparrow
```

and:

```math
SoC_i \downarrow \quad\Rightarrow\quad A_i \uparrow.
```

The paper also introduces an anxiety cost parameter $\mu\_{a,i}$.

For an EV that does not charge:

```math
\Pi_{a,i} = -\mu_{a,i}A_i.
```

For an EV that charges:

```math
\Pi_{a,i}=0.
```

---

## 5. Charging Cost

The energy required to charge EV $i$ is:

```math
E_i = V_i(SoC_{t,i}-SoC_i).
```

The charging cost is:

```math
\Pi_{c,i} = -V_i(SoC_{t,i}-SoC_i)P
```

when the EV chooses to charge.

Here:

- $P$ is the charging price in CNY/kWh.

If the EV does not charge:

```math
\Pi_{c,i}=0.
```

---

## 6. Queueing Model

Let:

- $c(N)$ be the number of EVs choosing to charge.
- $k$ be the number of charging piles.
- $\eta$ be charging power.
- $t\_0$ be the queueing time caused by EVs that arrived earlier.

The charging time of EV $i$ is:

```math
T_i = \frac{V_i(SoC_{t,i}-SoC_i)} {\eta}.
```

The expected queueing time is:

```math
t = \frac{1}{2k} (c(N)-1) \mathbb{E} \left[ \frac{V(SoC_t-SoC)} {\eta} \right] +t_0.
```

The queueing utility is:

```math
\Pi_{q,i} = -\mu_{q,i}t
```

when the EV chooses to charge.

If the EV does not charge:

```math
\Pi_{q,i}=0.
```

---

## 7. Bayesian Game Formulation

The highway charging problem is modeled as a Bayesian game with $N$ EV drivers.

### Players

```math
\mathcal{N}=\{1,\ldots,N\}
```

Each player is an EV driver.

### Private Information

The primary private information is:

```math
SoC_i.
```

Each EV knows its own SoC but does not know the SoC of other EVs.

The distribution of SoC is common knowledge.

Let:

```math
f(SoC)
```

denote the density function of the SoC distribution.

### Action Space

Each EV has two possible actions:

```math
X_i=\{0,1\}
```

where:

```text
x_i = 1 → Charge
x_i = 0 → Do not charge

```

The joint action vector is:

```math
\mathbf{x} = [x_i]_{i\in\mathcal N}.
```

---

## 8. Utility Function

The total payoff is:

```math
\Pi_i(\mathbf{x}) = \Pi_{a,i} + \Pi_{c,i} + \Pi_{q,i}.
```

For a charging EV:

```math
\Pi_i^{charge} = -V_i(SoC_{t,i}-SoC_i)P -\mu_{q,i}t.
```

For an EV that does not charge:

```math
\Pi_i^{no\ charge} = -\mu_{a,i}A_i.
```

Therefore, the driver chooses the action with the larger expected payoff.

---

## 9. Decision Function

The paper defines:

```math
h(SoC_i) = \mathbb{E} [ \Pi_i(x_i=0) \mid SoC_i ] - \mathbb{E} [ \Pi_i(x_i=1) \mid SoC_i ].
```

Using the utility formulation:

```math
h(SoC_i) = -\mu_aA_i + V_iP(SoC_t-SoC_i) + \mu_q\mathbb{E}[t].
```

The charging decision is therefore determined by the sign of $h$:

```math
h(SoC_i)>0 \quad\Rightarrow\quad \text{Do not charge}
```

and:

```math
h(SoC_i)<0 \quad\Rightarrow\quad \text{Charge}.
```

The equilibrium decision point satisfies:

```math
h(\widehat{SoC_i})=0.
```

---

## 10. BNE Decision Threshold

The paper proves that the Bayesian Nash Equilibrium has a threshold structure.

For each EV:

```math
x_i= \begin{cases} 1, & SoC_i<\widehat{SoC_i}, \\ 0, & SoC_i\geq\widehat{SoC_i}. \end{cases}
```

where:

```math
\widehat{SoC_i} \in[0,1]
```

is the charging decision point.

Thus:

```text
Low SoC
   ↓
Charge

High SoC
   ↓
Do not charge

```

This threshold structure is central to the computational solution.

---

## 11. BNE Theorem

The paper establishes the following result.

### Lemma

In both information settings, each EV has a unique charging decision point:

```math
\widehat{SoC_i}.
```

The equilibrium strategy is:

```math
x_i=1 \quad\text{if}\quad SoC_i<\widehat{SoC_i},
```

and:

```math
x_i=0 \quad\text{if}\quad SoC_i\geq\widehat{SoC_i}.
```

### Theorem

Under the model assumptions, both Bayesian game settings possess a unique Bayesian Nash Equilibrium.

Therefore:

```text
Unique decision point
        ↓
Unique threshold strategy
        ↓
Unique BNE

```

This theorem is important for the numerical implementation because it allows the equilibrium threshold to be solved using binary search.

---

## 12. Setting 1 — Without Destination Distribution Knowledge

In Setting 1, EV drivers do not know the destination distribution of the other EVs.

Instead, they use **self-referencing**.

The driver assumes that other EVs have parameters similar to their own.

The expected charging time is:

```math
\mathbb{E}[t] = \frac{1}{2k} \left( \mathbb{E}[c(N)]-1 \right) \frac{ \mathbb{E}[V(SoC_t-SoC)] }{\eta} +t_0.
```

Under self-referencing:

```math
\mathbb{E}[V(SoC_t-SoC)] = V_i \left( SoC_t-\mathbb{E}[SoC] \right).
```

The probability that another EV chooses to charge is:

```math
p_i = \int_0^{\widehat{SoC_i}} f(SoC)dSoC.
```

Therefore:

```math
\mathbb{E}[c(N)] = 1+(N-1)p_i.
```

Substituting this into the expected queueing time gives the complete expected payoff function.

The decision point $\widehat{SoC\_i}$ is then obtained by solving:

```math
h(\widehat{SoC_i})=0.
```

The root is bounded by:

```math
SoC_{d,i} \leq \widehat{SoC_i} \leq 1.
```

If:

```math
h(SoC_{d,i})\geq0,
```

the paper sets:

```math
\widehat{SoC_i}=SoC_{d,i}.
```

Otherwise, the unique root is found using binary search.

---

## 13. Algorithm 1 — BNE Without Destination Distribution

The implementation follows the paper's Algorithm 1.

```text
For each EV i:

    Calculate Safe SoC
    Calculate Danger SoC

    Evaluate h(Danger SoC)

    If h(Danger SoC) >= 0:
        decision point = Danger SoC

    Else:
        initialize:
            left  = Danger SoC
            right = 1

        while right - left > epsilon:

            midpoint = (left + right) / 2

            calculate h(left)
            calculate h(midpoint)

            if h(left) * h(midpoint) <= 0:
                right = midpoint
            else:
                left = midpoint

        decision point = midpoint

    Charge if:
        SoC < decision point

    Do not charge otherwise

```

The default precision used by the paper is:

```math
\epsilon=0.1\%.
```

---

## 14. Setting 2 — With Destination Distribution Knowledge

In Setting 2, EV drivers know the distribution of destinations in the EV flow.

Different destinations may imply different distances to the next charging station.

Therefore, the charging decision point becomes destination-specific:

```math
\widehat{SoC_i^k}.
```

For destination $k$:

```math
p_i^k = \int_0^{\widehat{SoC_i^k}} f(SoC)dSoC.
```

Let:

```math
N_k
```

be the number of EVs traveling toward destination $k$.

For an EV traveling toward destination $k'$:

```math
\mathbb{E}[c(N)] = \sum_{k\neq k'} N_kp_i^k + (N_{k'}-1)p_i^{k'} + 1.
```

The decision points satisfy:

```math
\mu_q\mathbb{E}[t] = \mu_a \lambda (SoC_{s,i}^k-\widehat{SoC_i^k})^{\alpha_i} + V_iP_i(1-\widehat{SoC_i^k}).
```

The resulting system is solved using an improved binary-search procedure.

---

## 15. Algorithm 2 — BNE With Destination Distribution

The implementation follows the paper's Algorithm 2.

```text
For each EV i:

    initialize:
        left  = Danger SoC
        right = 1

    while right - left > epsilon:

        midpoint = (left + right) / 2

        assume:
            decision point for destination k
            = midpoint

        calculate decision points for
        other destinations

        calculate charging probabilities

        calculate expected number
        of charging EVs

        calculate expected queueing time

        calculate h(midpoint)
        calculate h(left)
        calculate h(right)

        if h(midpoint) == 0:
            break

        if h(left) * h(midpoint) <= 0:
            right = midpoint
        else:
            left = midpoint

    obtain destination-specific
    charging decision point

    charge if:
        SoC < decision point

    do not charge otherwise

```

---

## 16. Paper Parameter Table

The following parameters reproduce the primary settings reported in the paper.

| Parameter | Value |
| --- | --- |
| $\alpha\_i$    | 2.0                                       |
| $\lambda\_i$   | 1.5                                       |
| $d\_{0,i}$     | $\mathcal{N}(600\text{ km},50\text{ km})$ |
| $d\_{s,i}$     | $\mathcal{N}(400\text{ km},50\text{ km})$ |
| $V\_i$         | {40, 60, 80, 100} kWh                     |
| $SoC\_i$       | $\mathcal{U}(20%,100%)$                   |
| $\mu\_q$       | 30 CNY/hour                               |
| $\mu\_a$       | 3000 CNY                                  |
| $SoC\_t$       | 100%                                      |
| $f(SoC)$       | Uniform on [0,1]                          |
| $E\_0$         | 0 kWh                                     |
| $\overline{E}$ | 7 MWh                                     |
| $\overline{X}$ | 4 MW                                      |

For the highway-network simulations:

| Charging Station | Charging Piles | Price |
| --- | ---: | ---: |
| CS 1 | 4 | 2.3 CNY/kWh |
| CS 2 | 4 | 2.3 CNY/kWh |
| CS 3 | 4 | 2.3 CNY/kWh |
| CS 4 | 6 | 2.5 CNY/kWh |
| CS 5 | 6 | 2.5 CNY/kWh |

The simulation uses 15-minute time intervals and initializes:

```math
t_0=0
```

at the beginning of the simulation.

EV parameters are generated from the distributions reported in the paper.

---

## 17. Equation-to-Code Mapping

| Mathematical Component | Python Implementation |
| --- | --- |
| Current SoC                                 | `EV.soc`                          |
| Safe SoC                                    | `calculate_safe_soc()`            |
| Danger SoC                                  | `calculate_danger_soc()`          |
| Range anxiety                               | `calculate_range_anxiety()`       |
| Charging energy                             | `charging_energy()`               |
| Charging time                               | `charging_time()`                 |
| Queueing time                               | `expected_queue_time()`           |
| Charging utility                            | `charging_utility()`              |
| Queueing utility                            | `queue_utility()`                 |
| Total utility                               | `total_utility()`                 |
| Expected charging probability               | `charging_probability()`          |
| Expected number of chargers                 | `expected_charging_count()`       |
| Expected queueing cost                      | `expected_queue_cost()`           |
| Decision function $h(SoC)$                  | `decision_function()`             |
| Decision threshold                          | `solve_decision_point()`          |
| Setting 1 BNE                               | `solve_bne_without_destination()` |
| Setting 2 BNE                               | `solve_bne_with_destination()`    |
| BNE verification                            | `verify_bne()`                    |

---

## 18. Replication Targets

The project does not consider successful execution alone to be sufficient.

The implementation will be evaluated against numerical and qualitative results reported in the paper.

## Target 1 — Perfect Rationality Benchmark

When range anxiety is ignored:

```math
\lambda=0
```

the symmetric example produces a charging decision point of approximately:

```math
\boxed{33.3\%}.
```

---

## Target 2 — Bounded Rationality

For:

```math
\lambda=2,
```

the paper reports a charging decision point of approximately:

```math
\boxed{41.8\%}.
```

The interpretation is:

```text
SoC < 41.8%
    ↓
Charge

SoC ≥ 41.8%
    ↓
Do not charge

```

---

## Target 3 — Stronger Risk Aversion

When:

```math
\lambda=5,
```

the reported decision point increases to approximately:

```math
\boxed{45.7\%}.
```

Therefore:

```math
\lambda\uparrow \quad\Rightarrow\quad \widehat{SoC}\uparrow.
```

This provides a key behavioral replication test.

---

## Target 4 — Queue Length

The paper reports that higher range anxiety can substantially increase queue lengths at some charging stations.

For example, at CS 2 at 18:45:

```text
Perfect rationality: approximately 4 EVs
λ = 1.5:             approximately 9 EVs
λ = 3.5:             approximately 21 EVs

```

The exact replication will depend on reproducing the same traffic-flow data and simulation configuration.

---

## Target 5 — Charging Demand

At CS 2 between 11:45 and 12:00, the paper reports approximately:

```text
λ = 0:    140 kWh
λ = 1.5:  200 kWh
λ = 3.5:  250 kWh

```

The model should reproduce the qualitative increase in charging demand as range anxiety increases.

---

## Target 6 — BNE Strategy Verification

The paper verifies the equilibrium by allowing individual EVs to deviate from the calculated BNE strategy.

The reported Setting 1 equilibrium at 3:00 PM is:

```text
EV 1, 2, 3, 6, 8, 9 → Charge
EV 4, 5, 7           → Do not charge

```

For Setting 2:

```text
EV 1, 2, 3, 6, 8       → Charge
EV 4, 5, 7, 9          → Do not charge

```

A valid BNE should satisfy:

```math
\text{Cost after unilateral deviation} > \text{Cost at equilibrium}.
```

---

## Target 7 — Cumulative EV Cost

For the one-station weekday experiment, the paper reports an average cumulative total cost of approximately:

```math
33,836\text{ CNY}
```

for the proposed method without destination information.

The reported benchmark values include approximately:

```math
60,689\text{ CNY}
```

for Nra and:

```math
44,023\text{ CNY}
```

for Residual.

These values will be treated as higher-level replication targets after the core BNE model has been validated.

---

## 19. Repository Structure

```text
04_paper_replication/
│
├── README.md
│
├── expected_cost.py
├── type_distribution.py
├── payoff.py
├── bne_solver.py
├── simulation.py
├── benchmarks.py
├── requirements.txt
│
└── tests/
    ├── test_expected_cost.py
    ├── test_payoff.py
    ├── test_bne_solver.py
    └── test_benchmarks.py

```

---

## 20. File Description

| File | Description |
| --- | --- |
| `README.md`            | Mathematical model, replication protocol, and documentation      |
| `expected_cost.py`     | Expected charging probability, charging count, and queueing cost |
| `type_distribution.py` | Private-information and SoC distributions                        |
| `payoff.py`            | Bayesian payoff and decision function $h(SoC)$                   |
| `bne_solver.py`        | BNE algorithms and binary-search solution                        |
| `simulation.py`        | Numerical experiments and replication scenarios                  |
| `benchmarks.py`        | Perfect rationality and benchmark decision models                |
| `requirements.txt`     | Python dependencies                                              |
| `tests/`               | Unit and replication tests                                       |

---

## 21. Installation

Enter the project directory:

```bash
cd 04_paper_replication

```

Create a virtual environment:

```bash
python3 -m venv .venv

```

Activate the virtual environment on macOS/Linux:

```bash
source .venv/bin/activate

```

Install the required dependencies:

```bash
pip install -r requirements.txt

```

---

## 22. Running the Replication

The complete replication will be executed through:

```bash
python simulation.py

```

The simulation will progressively support:

```text
Setting 1
    ↓
BNE without destination distribution
    ↓
Setting 2
    ↓
BNE with destination distribution
    ↓
Sensitivity analysis
    ↓
Benchmark comparison
    ↓
Network-level simulation

```

---

## 23. Testing

Run all tests with:

```bash
pytest

```

The tests will verify:

- Expected charging probability
- Expected charging count
- Expected queueing time
- Charging payoff
- No-charging payoff
- Decision function
- BNE threshold
- Binary-search convergence
- Setting 1 equilibrium
- Setting 2 equilibrium
- Unilateral deviation
- Benchmark results

The replication tests will distinguish between:

### Unit Tests

Tests of individual mathematical components.

```text
Equation
   ↓
Python function
   ↓
Expected numerical result

```

### Replication Tests

Tests comparing the Python implementation against reported paper results.

```text
Paper result
      ↕
Python result
      ↓
Replication tolerance

```

---

## 24. Expected Results

A successful implementation should reproduce the following qualitative relationships.

### Range Anxiety

```math
SoC\downarrow \Rightarrow A\uparrow
```

### Risk Aversion

```math
\lambda\uparrow \Rightarrow \widehat{SoC}\uparrow
```

### Charging Demand

Higher range anxiety should generally increase charging demand at earlier charging stations.

### Queueing

Higher charging demand should generally increase queueing congestion.

### Destination Information

More accurate destination information should improve the prediction of other EVs' charging behavior.

### Equilibrium

The BNE should have a threshold structure:

```math
SoC_i<\widehat{SoC_i} \Rightarrow \text{Charge}
```

and:

```math
SoC_i\geq\widehat{SoC_i} \Rightarrow \text{Do not charge}.
```

---

## 25. Connection to Stage 03

Stage 03 provides the physical and economic EV environment.

```text
03 — EV Charging Model
│
├── SoC
├── Safe SoC
├── Danger SoC
├── Range Anxiety
├── Charging Energy
├── Charging Time
├── Queue
└── Utility

```

Stage 04 adds strategic interaction:

```text
03 EV Environment
        ↓
Private Information
        ↓
Beliefs
        ↓
Expected Utility
        ↓
Strategic Interaction
        ↓
Best Response
        ↓
BNE

```

The Stage 03 modules therefore provide the lower-level computational foundation for the Stage 04 Bayesian game.

Stage 04 should reuse the conceptual structure of Stage 03 while adapting parameters and equations to the paper's exact formulation.

---

## 26. Connection to Stage 05 — Extension

Stage 04 is designed to provide a validated baseline for future research.

After reproducing the paper's core model and numerical results, Stage 05 can extend the framework in several directions.

Possible extensions include:

```text
05 — Extension
│
├── Heterogeneous driver preferences
├── Dynamic electricity pricing
├── Endogenous charging prices
├── Alternative queueing models
├── Charging-station capacity optimization
├── More realistic SoC distributions
├── Learning-based beliefs
├── Alternative bounded-rationality models
└── Multi-station strategic optimization

```

The extension should be based on limitations identified during the replication process rather than introducing modifications before the baseline model has been validated.

The research workflow is therefore:

```text
01 — Game Theory
        ↓
02 — Bayesian Game
        ↓
03 — EV Charging Model
        ↓
04 — Paper Replication
        ↓
Validation
        ↓
05 — Extension

```

---

## 27. Reproducibility Principle

The goal of this project is not simply to reproduce a numerical output.

The implementation should establish a transparent chain:

```text
Paper Equation
      ↓
Python Function
      ↓
Unit Test
      ↓
BNE Solver
      ↓
Simulation
      ↓
Replication Result

```

Every major mathematical component should therefore have:

1. A documented equation.
2. A corresponding Python implementation.
3. At least one unit test.
4. A clear connection to the paper.
5. A reproducible numerical result where possible.

This structure makes it possible to distinguish between:

- implementation errors;
- parameter differences;
- stochastic simulation differences;
- and genuine model extensions.

---

## 28. Research Roadmap

### Stage 01 — Game Theory

Basic strategic interaction and utility concepts.

### Stage 02 — Bayesian Game

Private information, beliefs, expected utility, and Bayesian Nash equilibrium.

### Stage 03 — EV Charging Model

Computational implementation of the EV charging environment.

### Stage 04 — Paper Replication

Replication of:

- the bounded-rational EV charging model;
- the Bayesian game;
- the BNE threshold structure;
- Setting 1;
- Setting 2;
- Algorithm 1;
- Algorithm 2;
- parameter sensitivity;
- charging demand;
- queueing effects;
- and selected paper experiments.

### Stage 05 — Extension

Development of a new model or extension based on the limitations and research opportunities identified during replication.

---

## 29. Academic Purpose

This project is intended for:

- academic research;
- computational learning;
- paper replication;
- model validation;
- reproducible research;
- and future methodological extension.

The implementation is a Python replication of the mathematical and computational framework presented in the paper and is not intended to replace the original publication or its official source code.

```
```
