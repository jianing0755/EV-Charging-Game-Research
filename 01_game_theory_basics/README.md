# 01 — Game Theory Basics

This module introduces the basic concepts of **game theory** through a simple two-player congestion-style game motivated by electric vehicle charging.

The purpose of this module is to build the theoretical foundation needed for the Bayesian game and EV charging models developed in the later stages of this project.

---

## Research Motivation

When multiple EVs make decisions in the same environment, the outcome for one EV may depend on the decisions of other EVs.

For example, if multiple EVs choose the same charging station, congestion and waiting costs may increase. Therefore, the best decision of one EV may depend on the action chosen by another EV.

This type of strategic interdependence can be modeled using **game theory**.

The model in this module is a simplified educational example rather than the model used in the target research paper.

---

## Model

There are two players:

* Player 1: EV 1
* Player 2: EV 2

Each player chooses one of two charging stations:

* A
* B

The players minimize their total cost.

The cost matrix is:

| Player 1 \ Player 2 |        A |      B |
| ------------------- | -------: | -----: |
| A                   | (10, 10) | (4, 6) |
| B                   |   (6, 4) | (8, 8) |

The first value represents Player 1's cost, while the second value represents Player 2's cost.

---

## Concepts

This module demonstrates the following fundamental concepts:

1. **Best Response**
2. **Pure-Strategy Nash Equilibrium**
3. **Unilateral Deviation**
4. **Strategic Interdependence**

### Best Response

A best response is the strategy that minimizes a player's cost given the strategy chosen by the other player.

For example, if Player 2 chooses A:

* Player 1 choosing A gives a cost of 10.
* Player 1 choosing B gives a cost of 6.

Therefore, Player 1's best response is B.

### Nash Equilibrium

A strategy profile is a Nash equilibrium if no player can reduce their cost by changing their strategy alone.

For this game, the pure-strategy Nash equilibria are:

* `(A, B)`
* `(B, A)`

At either equilibrium, neither player has an incentive to unilaterally change their strategy.

---

## Results

The game has two pure-strategy Nash equilibria:

* `(A, B)`
* `(B, A)`

These equilibria demonstrate how individual optimal decisions can depend on the decisions of other players.

---

## Files

### `best_response.py`

Implements the best-response functions for both players.

### `nash_equilibrium.py`

Enumerates all possible strategy profiles and identifies pure-strategy Nash equilibria.

---

## How to Run

From this directory:

```bash
python best_response.py
python nash_equilibrium.py
```

---

## Connection to Later Modules

This module provides the basic game-theoretic foundation for the subsequent stages of the project:

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

The progression is:

* **01:** Understand strategic decision-making and Nash equilibrium.
* **02:** Extend the framework to situations with incomplete information and private types.
* **03:** Translate these concepts into an EV charging decision model.
* **04:** Apply the theoretical and modeling components to reproduce a real research paper.
* **05:** Explore possible extensions beyond the original paper.

---

## Scope

This module focuses only on the fundamental concepts of game theory.

It does **not** attempt to reproduce the mathematical model of the target paper. Paper-specific modeling, Bayesian decision-making, EV charging behavior, and numerical reproduction are introduced in later modules.
