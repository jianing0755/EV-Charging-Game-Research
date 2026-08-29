"""
Expected Cost in a Bayesian Decision Problem.

This module computes expected costs when a player does not know
the exact type of another player but has probabilistic beliefs
about that type.

The model is intentionally simple and serves as a foundation
for the later EV charging Bayesian game.
"""

# Possible types of the other player.
TYPES = [
    "risk_averse",
    "risk_neutral",
]

# Available actions.
ACTIONS = [
    "A",
    "B",
]


# Conditional cost matrix.
#
# The cost depends on the type of the other player.
#
#                     Action A    Action B
# Risk-Averse             10           6
# Risk-Neutral             4           8
#
# These values are illustrative and are used only for
# demonstrating the Bayesian decision-making framework.

COST_BY_TYPE = {

    "risk_averse": {
        "A": 10,
        "B": 6,
    },

    "risk_neutral": {
        "A": 4,
        "B": 8,
    },
}


def validate_belief(belief):
    """
    Validate a probability distribution over player types.

    Parameters
    ----------
    belief : dict
        Probability assigned to each player type.

    Raises
    ------
    ValueError
        If probabilities are invalid or do not sum to 1.
    """

    missing_types = set(TYPES) - set(belief)

    if missing_types:
        raise ValueError(
            f"Missing probabilities for types: {missing_types}"
        )

    probabilities = [
        belief[player_type]
        for player_type in TYPES
    ]

    if any(
        probability < 0 or probability > 1
        for probability in probabilities
    ):
        raise ValueError(
            "All probabilities must be between 0 and 1."
        )

    if abs(sum(probabilities) - 1.0) > 1e-9:
        raise ValueError(
            "Belief probabilities must sum to 1."
        )


def expected_cost(action, belief):
    """
    Calculate the expected cost of an action.

    The expected cost is defined as:

        E[C(a)] = sum_t P(t) C(a | t)

    where:

        t       = type of the other player
        P(t)    = belief about that type
        C(a|t)  = conditional cost of taking action a

    Parameters
    ----------
    action : str
        Player's action, either "A" or "B".

    belief : dict
        Probability distribution over the other player's types.

        Example:
            {
                "risk_averse": 0.4,
                "risk_neutral": 0.6
            }

    Returns
    -------
    float
        Expected cost of the selected action.

    Raises
    ------
    ValueError
        If the action or belief is invalid.
    """

    if action not in ACTIONS:
        raise ValueError(
            f"Invalid action: {action}. "
            f"Available actions: {ACTIONS}"
        )

    validate_belief(belief)

    total = 0.0

    for player_type in TYPES:

        probability = belief[player_type]

        conditional_cost = COST_BY_TYPE[
            player_type
        ][action]

        total += (
            probability
            * conditional_cost
        )

    return total


if __name__ == "__main__":

    # Belief about the other player's type.
    belief = {
        "risk_averse": 0.4,
        "risk_neutral": 0.6,
    }

    print("Belief:")
    print(belief)

    print("\nExpected costs:")

    for action in ACTIONS:

        cost = expected_cost(
            action,
            belief
        )

        print(
            f"Action {action}: "
            f"Expected Cost = {cost:.2f}"
        )
