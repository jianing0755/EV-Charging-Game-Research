# 02 — Bayesian Game

This module introduces Bayesian decision-making under incomplete information.

The purpose of this module is to build the theoretical and computational foundation for modeling heterogeneous EV drivers in charging decision problems.

---

## 1. Motivation

In an EV charging environment, a driver may not know the exact characteristics or preferences of other drivers.

Different drivers may have different:

- Risk preferences
- Range anxiety levels
- Battery states
- Charging preferences

A driver may therefore know the possible types of other drivers without knowing their exact type.

Instead, the driver forms a probabilistic belief about the type of another player.

This creates a game with **incomplete information**.

---

## 2. Player Types

The current model considers two possible player types:

- `risk_averse`
- `risk_neutral`

Formally:

$$
t \in \{RiskAverse, RiskNeutral\}
$$

The player's belief about the type of the other player is represented by a probability distribution.

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

---

## 3. Actions

The player can choose between two possible actions:

- `A`
- `B`

Formally:

$$
a \in \{A, B\}
$$

At this stage, `A` and `B` are abstract actions.

In the later EV charging model, they will represent different charging stations.

---

## 4. Conditional Cost

The cost of an action depends on the type of the other player.

The current illustrative cost structure is:

| Other Player Type | Action A | Action B |
|-------------------|----------|----------|
| Risk-Averse       | 10       | 6        |
| Risk-Neutral      | 4        | 8        |

These values are **illustrative parameters for demonstrating the Bayesian game framework**.

They are not parameters taken from a published paper.

---

## 5. Expected Cost

Because the player does not know the exact type of the other player, each action is evaluated using its expected cost.

The expected cost is defined as:

$$
E[C(a)] = \sum_t P(t)C(a \mid t)
$$

where:

- \(a\) = player's action
- \(t\) = type of the other player
- \(P(t)\) = belief about the other player's type
- \(C(a \mid t)\) = conditional cost

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
E[C(A)] = 0.4(10) + 0.6(4)
$$

Therefore:

$$
E[C(A)] = 6.4
$$

For Action B:

$$
E[C(B)] = 0.4(6) + 0.6(8)
$$

Therefore:

$$
E[C(B)] = 7.2
$$

Since:

$$
E[C(A)] < E[C(B)]
$$

the player prefers Action A.

---

## 6. Bayesian Best Response

The Bayesian best response is the action that minimizes expected cost.

Formally:

$$
a^* = \arg\min_a E[C(a)]
$$

For the example above:

$$
a^* = A
$$

The Python implementation automatically evaluates all available actions and returns the action with the lowest expected cost.

---

## 7. Project Structure

```text
02_bayesian_game/
│
├── expected_cost.py
├── bayesian_best_response.py
└── README.md
```

### `expected_cost.py`

This module provides functions for:

- Validating probability distributions
- Looking up conditional costs
- Computing expected costs

Main function:

```python
expected_cost(action, belief)
```

### `bayesian_best_response.py`

This module provides functions for:

- Evaluating all available actions
- Comparing expected costs
- Computing the Bayesian best response

Main function:

```python
bayesian_best_response(belief)
```

---

## 8. How to Run

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

## 9. Computational Logic

The computational structure is:

```text
Player Type
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

---

## 10. Connection to EV Charging Research

The current abstract model will later be extended into an EV charging decision model.

The abstract actions:

```text
A / B
```

will become charging-station choices.

The current illustrative cost function:

```text
10 / 6 / 4 / 8
```

will eventually be replaced by a model-based cost function incorporating variables such as:

- Battery state of charge
- Remaining driving range
- Charging price
- Travel distance
- Waiting time
- Queue length
- Charging duration
- Range anxiety
- Driver risk preference

This will allow the model to represent strategic charging decisions under heterogeneous driver characteristics.

---

## 11. Current Limitations

This module is a simplified computational foundation rather than a complete EV charging model.

It currently does not include:

- Multiple interacting EVs
- Endogenous queue length
- Charging station capacity
- Battery dynamics
- Travel time
- Charging duration
- Explicit range-anxiety functions
- Type-dependent strategic policies
- Bayesian Nash equilibrium

These components will be introduced in later modules.

---

## 12. Next Step

The next module will extend the Bayesian game framework into an EV charging model.

```text
Bayesian Game
      ↓
EV Charging Model
      ↓
Battery State
      +
Charging Cost
      +
Travel Cost
      +
Waiting / Queueing Cost
      +
Range Anxiety
      ↓
Strategic Charging Decisions
      ↓
Equilibrium Analysis
```

The long-term goal is to develop a reproducible computational framework for studying EV charging decisions and eventually reproduce and extend published research.
