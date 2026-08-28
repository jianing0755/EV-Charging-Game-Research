# 01 — Game Theory Basics

This module implements a simple two-player congestion-style
game to introduce strategic decision-making in electric vehicle
charging.

## Research Motivation

Electric vehicle charging decisions are interdependent.

If multiple EVs choose the same charging station, congestion
and waiting costs may increase. Therefore, the optimal decision
of one EV depends on the decisions of other EVs.

This creates a natural game-theoretic setting.

## Model

There are two players:

- Player 1: EV 1
- Player 2: EV 2

Each player chooses one of two charging stations:

- A
- B

The players minimize their total cost.

The cost matrix is:

| Player 1 \ Player 2 | A | B |
|---|---:|---:|
| A | (10, 10) | (4, 6) |
| B | (6, 4) | (8, 8) |

The first value represents Player 1's cost and the second
value represents Player 2's cost.

## Concepts

This module demonstrates:

1. Best Response
2. Pure-Strategy Nash Equilibrium
3. Unilateral Deviation
4. Strategic Interdependence

## Results

The game has two pure-strategy Nash equilibria:

- `(A, B)`
- `(B, A)`

At either equilibrium, neither player can reduce their cost
by changing their action alone.

## Files

### `best_response.py`

Implements the best-response functions for both players.

### `nash_equilibrium.py`

Enumerates all possible strategy profiles and identifies
pure-strategy Nash equilibria.

## How to Run

From this directory:

```bash
python best_response.py
python nash_equilibrium.py
