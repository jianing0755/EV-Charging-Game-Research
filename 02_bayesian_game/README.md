# 02 — Bayesian Game

This module extends the basic game-theoretic framework from `01_game_theory_basics` to situations with **incomplete information**.

The purpose of this module is to introduce the computational foundations of Bayesian games:

* Player types
* Belief distributions
* Conditional costs
* Expected costs
* Bayesian best responses

These concepts provide the theoretical foundation for modeling heterogeneous decision-makers in the later EV charging model and paper replication.

---

## 1. Motivation

In a standard game, players are assumed to know the relevant characteristics of other players.

In many real-world decision problems, however, a player may not know the exact characteristics or preferences of another player.

For example, different decision-makers may have different:

* Risk preferences
* Cost sensitivities
* Behavioral characteristics
* Decision-making tendencies

A player may know the possible types of another player without knowing which type the player actually has.

This creates a game with **incomplete information**.

Bayesian games provide a framework for making decisions under this uncertainty.

---

## 2. Player Types

The current illustrative model considers two possible player types:

* `risk_averse`
* `risk_neutral`

Formally:

$$
t \in \{RiskAverse, RiskNeutral\}
$$

The player does not directly observe the type of the other player.

Instead, the player has a belief about the probability of each possible type.

For example:

$$
P(RiskAverse) = 0.4
$$

$$
P(RiskNeutral) = 0.6
$$

The probabilities must satisfy:

$$
\sum_t P(t) = 1
$$

The type distribution therefore represents the player's **belief** about the unknown type.

---

## 3. Actions

The player can choose between two abstract actions:

* `A`
* `B`

Formally:

$$
a \in \{A, B\}
$$

At this stage, the actions are intentionally abstract.

They will later be mapped to concrete decisions in the EV charging model.

---

## 4. Conditional Cost

The cost of an action depends on the type of the other player.

The current illustrative cost structure is:

| Other Player Type | Action A | Action B |
| ----------------- | -------: | -------: |
| Risk-Averse       |       10 |        6 |
| Risk-Neutral      |        4 |        8 |

These values are **illustrative parameters used only to demonstrate the Bayesian game framework**.

They are not parameters taken from the target research paper.

The important idea is that the optimal action depends on information that the player does not directly observe.

---

## 5. Expected Cost

Because the player does not know the exact type of the other player, the player evaluates each action using its expected cost.

The expected cost is:

$$
E[C(a)] = \sum_t P(t)C(a \mid t)
$$

where:

* \(a\) = player's action
* \(t\) = type of the other player
* \(P(t)\) = belief about the other player's type
* \(C(a \mid t)\) = conditional cost given that type

### Example

Suppose:

$$
P(RiskAverse) = 0.4
$$

and:

$$
P(RiskNeutral) = 0.6
$$

For Action A:

$$
E[C(A)]
=
0.4(10)+0.6(4)
=
6.4
$$

For Action B:

$$
E[C(B)]
=
0.4(6)+0.6(8)
=
7.2
$$

Therefore:

$$
E[C(A)] < E[C(B)]
$$

and the player prefers Action A.

---

## 6. Bayesian Best Response

The Bayesian best response is the action that minimizes expected cost given the player's belief about the unknown type.

Formally:

$$
a^*
=
\arg\min_a E[C(a)]
$$

For the example above:

$$
a^* = A
$$

The Python implementation evaluates the available actions and returns the action with the lowest expected cost.

---

## 7. From Bayesian Decision to Bayesian Game

The key difference from `01_game_theory_basics` is the presence of **incomplete information**.

The conceptual progression is:

```text
Complete Information
        ↓
Player observes opponent's action/type
        ↓
Best Response
        ↓
Nash Equilibrium
```

In the Bayesian setting:

```text
Incomplete Information
        ↓
Unknown Player Type
        ↓
Belief Distribution
        ↓
Expected Cost
        ↓
Bayesian Best Response
```

This module focuses on the computational building blocks of this process.

A complete **Bayesian Nash Equilibrium (BNE)** solver is introduced later when the framework is applied to the target EV charging paper.

---

## 8. Project Structure

```text
02_bayesian_game/
│
├── expected_cost.py
├── bayesian_best_response.py
└── README.md
```

### `expected_cost.py`

Provides functions for:

* Validating probability distributions
* Looking up conditional costs
* Computing expected costs

Main function:

```python
expected_cost(action, belief)
```

### `bayesian_best_response.py`

Provides functions for:

* Evaluating available actions
* Comparing expected costs
* Computing the Bayesian best response

Main function:

```python
bayesian_best_response(belief)
```

---

## 9. How to Run

Navigate to this directory:

```bash
cd 02_bayesian_game
```

Run:

```bash
python expected_cost.py
```

Expected output:

```text
Belief:
{'risk_averse': 0.4, 'risk_neutral': 0.6}

Expected costs:
Action A: Expected Cost = 6.40
Action B: Expected Cost = 7.20
```

Then run:

```bash
python bayesian_best_response.py
```

Expected output:

```text
Expected costs:
  A: 6.40
  B: 7.20

Bayesian Best Response: A
```

---

## 10. Computational Logic

The computational structure is:

```text
Unknown Player Type
        ↓
Belief Distribution
        ↓
Conditional Cost
        ↓
Expected Cost
        ↓
Bayesian Best Response
```

Mathematically:

$$
P(t)
\rightarrow
C(a \mid t)
\rightarrow
E[C(a)]
\rightarrow
a^*
$$

The implementation separates these components so that each mathematical concept corresponds to a clear computational function.

---

## 11. Connection to the EV Charging Model

The abstract Bayesian framework will later be connected to the EV charging problem.

At this stage:

```text
Type
    ↓
Risk-Averse / Risk-Neutral

Action
    ↓
A / B

Cost
    ↓
Illustrative Cost
```

In later modules, these abstract components become problem-specific:

```text
Driver Type
    ↓
Behavioral / Risk Characteristics

Action
    ↓
Charging Decision

Cost
    ↓
Charging Cost
+ Waiting Cost
+ Range Anxiety
+ Other EV-Specific Costs
```

The detailed EV charging model is implemented in `03_ev_charging_model`.

---

## 12. Current Limitations

This module is intentionally a simplified Bayesian game framework.

It currently does not include:

* Multiple EVs with heterogeneous private information
* Endogenous queue formation
* Charging station capacity
* Battery dynamics
* Travel distance
* Charging duration
* Explicit range-anxiety functions
* Type-dependent equilibrium strategies
* A complete Bayesian Nash Equilibrium solver
* Real-world EV charging data

These components are introduced progressively in later modules.

---

## 13. Connection to the Overall Project

The role of this module in the overall project is:

```text
01 — Game Theory Basics
        ↓
Basic strategic interaction
        ↓
02 — Bayesian Game
        ↓
Incomplete information and beliefs
        ↓
03 — EV Charging Model
        ↓
Problem-specific EV decision model
        ↓
04 — Paper Replication
        ↓
Apply the framework to a real research paper
        ↓
05 — Extension
        ↓
Explore possible extensions
```

Therefore, this module serves as the bridge between **basic game theory** and the **EV charging research problem**.

---

## 14. Next Step

The next module, `03_ev_charging_model`, translates the abstract decision-making framework into a concrete EV charging problem.

It introduces problem-specific components such as:

* Battery state of charge
* Driving range
* Range anxiety
* Charging stations
* Queueing
* Charging cost
* Utility

The goal is to move from:

$$
\text{Abstract Bayesian Decision}
$$

to:

$$
\text{EV Charging Decision Model}
$$

which will later provide the modeling foundation for the paper replication in `04_paper_replication`.
