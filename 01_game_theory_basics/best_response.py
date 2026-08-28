"""
Best Response in a Two-Player Cost-Minimization Game.

This module implements best-response functions for a simple
two-player, two-action game.

Players:
    Player 1
    Player 2

Actions:
    A
    B

The players minimize cost rather than maximize utility.
"""

# Available actions
ACTIONS = ["A", "B"]


# Cost matrix:
#
#                    Player 2
#                 A          B
# Player 1
#       A       (10,10)    (4,6)
#       B       (6,4)      (8,8)
#
# The first value is Player 1's cost.
# The second value is Player 2's cost.

COST = {
    ("A", "A"): (10, 10),
    ("A", "B"): (4, 6),
    ("B", "A"): (6, 4),
    ("B", "B"): (8, 8),
}


def best_response_player1(player2_action):
    """
    Compute Player 1's best response to Player 2's action.

    Parameters
    ----------
    player2_action : str
        Player 2's action, either "A" or "B".

    Returns
    -------
    str
        Player 1's cost-minimizing action.
    """

    costs = {
        action: COST[(action, player2_action)][0]
        for action in ACTIONS
    }

    return min(costs, key=costs.get)


def best_response_player2(player1_action):
    """
    Compute Player 2's best response to Player 1's action.

    Parameters
    ----------
    player1_action : str
        Player 1's action, either "A" or "B".

    Returns
    -------
    str
        Player 2's cost-minimizing action.
    """

    costs = {
        action: COST[(player1_action, action)][1]
        for action in ACTIONS
    }

    return min(costs, key=costs.get)


if __name__ == "__main__":

    print("Best responses for Player 1:")

    for action in ACTIONS:
        print(
            f"If Player 2 chooses {action}, "
            f"Player 1 chooses "
            f"{best_response_player1(action)}"
        )

    print("\nBest responses for Player 2:")

    for action in ACTIONS:
        print(
            f"If Player 1 chooses {action}, "
            f"Player 2 chooses "
            f"{best_response_player2(action)}"
        )
