# 03 — EV Charging Model

This module develops a standalone computational model of an electric vehicle (EV) charging environment.

The purpose of this module is to translate EV charging concepts into modular and testable Python components before applying the game-theoretic framework to the target research paper in `04_paper_replication`.

The module focuses on the physical and economic components of an EV charging decision, including:

* State of Charge (SoC)
* Safe and danger SoC thresholds
* Range anxiety
* Charging energy
* Charging time
* Charging station capacity
* Queueing time
* Charging cost
* Queueing cost
* Total utility

This module is a **standalone modeling stage**. It is not intended to reproduce the target research paper directly.

---

## 1. Role in the Overall Project

The project follows the progression:

```text
01 — Game Theory Basics
        ↓
02 — Bayesian Game
        ↓
03 — EV Charging Model
        ↓
04 — Paper Replication
        ↓
05 — Extension
```

Each stage has a different purpose:

* **01:** Build the foundation of strategic decision-making.
* **02:** Introduce incomplete information, beliefs, and Bayesian decision-making.
* **03:** Translate EV charging behavior into a computational model.
* **04:** Integrate these foundations and independently reproduce the mathematical model and equilibrium algorithms of a published paper.
* **05:** Explore possible extensions beyond the original paper.

Therefore, Stage 03 serves as the bridge between **abstract game-theoretic concepts** and the **real EV charging research problem**.

---

## 2. Model Overview

An EV driver must decide whether charging is necessary or economically desirable before continuing a trip.

The decision depends on factors such as:

1. Current battery State of Charge (SoC)
2. Distance to the next charging station
3. Available driving range
4. Safe driving threshold
5. Range anxiety
6. Electricity price
7. Charging energy
8. Charging time
9. Expected queueing time
10. Driver-specific waiting cost

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
     ↓
Charging Decision
```

The model is intentionally modular so that individual components can be tested independently.

---

## 3. State of Charge

Let:

* \(SoC_i\) denote the current state of charge of EV \(i\).
* \(V_i\) denote the battery capacity.
* \(SoC_{t,i}\) denote the target state of charge.

The state of charge is normalized as:

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

* \(d_i\) be the distance to the next charging station.
* \(d_{s,i}\) be the safe driving range.

The safe SoC threshold is:

$$
SoC_{s,i} =
\begin{cases}
\dfrac{d_i}{d_{s,i}}, & d_i < d_{s,i} \\
1, & d_i \geq d_{s,i}
\end{cases}
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

Let \(d_{0,i}\) denote the theoretical maximum driving range.

The danger SoC threshold is:

$$
SoC_{d,i} =
\begin{cases}
\dfrac{d_i}{d_{0,i}}, & d_i < d_{0,i} \\
1, & d_i \geq d_{0,i}
\end{cases}
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

* \(\lambda_i\) controls the intensity of range anxiety.
* \(\alpha_i\) controls the curvature of the anxiety function.

The basic relationship is:

$$
SoC_i \downarrow
\quad\Rightarrow\quad
A_i \uparrow
$$

Therefore, lower battery levels create stronger incentives to charge.

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

Let \(\eta\) denote the effective charging power.

Charging time is:

$$
T_i =
\frac{
E_i
}{
\eta
}
$$

Therefore:

$$
E_i \uparrow
\quad\Rightarrow\quad
T_i \uparrow
$$

This component connects the battery model to the charging-station and queueing model.

---

## 9. Queueing Time

Suppose:

* \(c(N)\) EVs choose to charge.
* \(k\) charging piles are available.
* \(E[T]\) is expected charging time.
* \(t_0\) is the existing queueing time.

The expected queueing time is modeled as:

$$
t =
\frac{c(N)-1}{2k}E[T] + t_0
$$

This introduces congestion into the EV charging environment.

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

The resulting queueing component will later provide an important source of strategic interaction between EV drivers.

---

## 10. Charging Cost

Let \(P\) denote the electricity price.

The charging cost is:

$$
C_i = E_i P
$$

The corresponding utility component is:

$$
\Pi_{c,i} = -C_i
$$

Therefore:

**Charging cost utility**

`Pi_c,i = -V_i (SoC_t,i - SoC_i) P`

Charging therefore creates a direct monetary cost.

---

## 11. Queueing Cost

Let `mu_q,i` denote the driver's cost of waiting.

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

Drivers with a higher waiting-cost parameter place a greater economic cost on charging-station congestion.

---

## 12. Total Utility

The total utility combines the relevant components:

1. Range anxiety
2. Charging cost
3. Queueing cost

Conceptually:

$$
\Pi_i =
\Pi_{a,i}
+
\Pi_{c,i}
+
\Pi_{q,i}
$$

For an EV that chooses to charge:

- Charging utility = charging cost utility + queueing utility
- Total charging utility = `Pi_C`

For an EV that chooses not to charge:

- Non-charging utility = range-anxiety utility
- Total non-charging utility = `Pi_NC`

The EV chooses to charge when:

`Pi_C > Pi_NC`
This provides a basic payoff structure that can later be incorporated into a strategic decision model.

---

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

| File                  | Description                                     |
| --------------------- | ----------------------------------------------- |
| `README.md`           | Documentation and mathematical model            |
| `ev_model.py`         | EV driver model and SoC thresholds              |
| `range_anxiety.py`    | Range anxiety calculation                       |
| `charging_station.py` | Charging-station parameters                     |
| `queue_model.py`      | Charging time and queueing model                |
| `utility.py`          | Charging, queueing, and total utility functions |
| `simulation.py`       | End-to-end demonstration of the EV model        

---




