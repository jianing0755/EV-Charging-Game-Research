````markdown
# 02 — Bayesian Game

This module introduces Bayesian decision-making under
incomplete information and provides the theoretical foundation
for modeling heterogeneous EV drivers.

The current implementation is intentionally simple. Its purpose
is to establish the computational framework that will later be
extended to an electric vehicle charging game.

---

## 1. Motivation

In an EV charging environment, a driver may not know the exact
characteristics or preferences of other drivers.

For example, different drivers may have different:

- Risk preferences
- Range anxiety levels
- Battery states
- Charging preferences

A driver may therefore know the possible types of other drivers
but not their exact type.

Instead, the driver forms a probabilistic belief about the type
of another player.

This creates a game with incomplete information.

---

## 2. Player Types

The current model considers two possible types:

- `risk_averse`
- `risk_neutral`

Formally:

\[
t \in \{RiskAverse, RiskNeutral\}
\]

The player does not directly observe the type of the other
player.

Instead, the player has a belief distribution:

\[
P(t)
\]

For example:

\[
P(RiskAverse)=0.4
\]

\[
P(RiskNeutral)=0.6
\]

---

## 3. Actions

The player chooses between two possible actions:

\[
A = \{A,B\}
\]

In the eventual EV charging application, these actions can
represent different charging stations.

At this stage, `A` and `B` are abstract actions.

---

## 4. Conditional Cost

The player's cost depends on the type of the other player.

The illustrative conditional cost structure is:

| Other Player Type | Action A | Action B |
|---|---:|---:|
| Risk-Averse | 10 | 6 |
| Risk-Neutral | 4 | 8 |

These values are **illustrative only** and do not represent
parameters from a specific published paper.

---

## 5. Expected Cost

Because the player does not know the exact type of the other
player, the player evaluates each action using expected cost.

The expected cost is:

\[
E[C(a)]
=
\sum_t P(t)C(a|t)
\]

where:

- \(t\) is the type of the other player
- \(P(t)\) is the player's belief about that type
- \(C(a|t)\) is the conditional cost of action \(a\)

For example, with:

\[
P(RiskAverse)=0.4
\]

and:

\[
P(RiskNeutral)=0.6
\]

the expected cost of Action A is:

\[
E[C(A)]
=
0.4(10)+0.6(4)
=
6.4
\]

The expected cost of Action B is:

\[
E[C(B)]
=
0.4(6)+0.6(8)
=
7.2
\]

Therefore:

\[
E[C(A)] < E[C(B)]
\]

and the player chooses:

\[
\boxed{A}
\]

---

## 6. Bayesian Best Response

The Bayesian best response is the action that minimizes
expected cost:

\[
a^*
=
\arg\min_a E[C(a)]
\]

For the example above:

\[
a^*=A
\]

The implementation automatically evaluates all available
actions and returns the action with the lowest expected cost.

---

## 7. Files

### `expected_cost.py`

Provides functions for:

- Belief validation
- Conditional cost lookup
- Expected cost calculation

The main function is:

```python
expected_cost(action, belief)
````

---

### `bayesian_best_response.py`

Provides functions for:

* Evaluating all actions
* Comparing expected costs
* Computing the Bayesian best response

The main function is:

```python
bayesian_best_response(belief)
```

---

## 8. How to Run

From the `02_bayesian_game` directory:

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

## 9. Model Structure

The computational logic can be summarized as:

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
C(a|t)
\rightarrow
E[C(a)]
\rightarrow
a^*
$$

---

## 10. Relation to EV Charging Research

This Bayesian framework will later be incorporated into an
EV charging decision model.

The abstract action:

```text
A / B
```

will become a charging-station choice.

The illustrative cost:

```text
10 / 6 / 4 / 8
```

will eventually be replaced by a model-based cost function
depending on physical and behavioral variables such as:

* Battery state
* Remaining driving range
* Charging price
* Travel distance
* Waiting time
* Queue length
* Range anxiety
* Driver risk preference

The resulting model will combine Bayesian game theory with
EV charging network decisions.

---

## 11. Current Limitations

This module is a simplified educational and computational
foundation rather than a complete EV charging model.

It currently does not model:

* Multiple interacting EVs
* Endogenous queue length
* Charging station capacity
* Battery dynamics
* Travel time
* Charging duration
* Explicit range-anxiety functions
* Bayesian Nash equilibrium with strategic type-dependent
  strategies

These components will be introduced in later modules.

---

## 12. Next Step

The next module will extend this Bayesian framework into an
EV charging game:

```text
02 Bayesian Game
        ↓
03 EV Charging Model
        ↓
Battery State
        +
Charging Cost
        +
Travel Cost
        +
Queueing Cost
        +
Range Anxiety
        ↓
Strategic Charging Decisions
        ↓
Nash / Bayesian Equilibrium
```

The goal is to gradually move from a simple theoretical model
to a reproducible computational framework for EV charging
research.

```
```
