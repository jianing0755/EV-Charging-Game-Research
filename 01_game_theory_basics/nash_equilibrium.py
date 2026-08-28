"""
Pure-Strategy Nash Equilibrium.

This module identifies pure-strategy Nash equilibria
in a two-player cost-minimization game.
"""

from itertools import product

from best_response import (
    ACTIONS,
    COST,
    best_response_player1,
    best_response_player2,
)


def is_nash_equilibrium(profile):
    """
    Check whether a strategy profile is a pure-strategy Nash equilibrium.

    Parameters
    ----------
    profile : tuple
        A strategy profile (player1_action, player2_action).

    Returns
    -------
    bool
        True if neither player can reduce their cost by unilateral deviation.
    """

    player1_action, player2_action = profile

    player1_best_response = best_response_player1(
        player2_action
    )

    player2_best_response = best_response_player2(
        player1_action
    )

    return (
        player1_action == player1_best_response
        and
        player2_action == player2_best_response
    )


def find_nash_equilibria():
    """
    Enumerate all pure-strategy Nash equilibria.

    Returns
    -------
    list
        A list of Nash equilibrium strategy profiles.
    """

    equilibria = []

    for profile in product(ACTIONS, repeat=2):

        if is_nash_equilibrium(profile):
            equilibria.append(profile)

    return equilibria


if __name__ == "__main__":

    equilibria = find_nash_equilibria()

    print("Pure-strategy Nash equilibria:")

    for equilibrium in equilibria:

        profile = equilibrium
        costs = COST[profile]

        print(
            f"Strategy = {profile}, "
            f"Costs = {costs}"
        )
