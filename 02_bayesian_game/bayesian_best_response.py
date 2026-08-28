```python
"""
Bayesian Best Response.

This module determines the cost-minimizing action when a player
faces uncertainty about another player's type.

The player chooses the action with the lowest expected cost.
"""

from expected_cost import (
    ACTIONS,
    expected_cost,
)


def evaluate_actions(belief):
    """
    Calculate the expected cost of every available action.

    Parameters
    ----------
    belief : dict
        Probability distribution over the other player's types.

    Returns
    -------
    dict
        Mapping from action to expected cost.

        Example:
            {
                "A": 6.4,
                "B": 7.2
            }
    """

    return {
        action: expected_cost(
            action,
            belief
        )
        for action in ACTIONS
    }


def bayesian_best_response(belief):
    """
    Compute the Bayesian best response.

    The player chooses the action with the lowest expected cost:

        a* = argmin_a E[C(a)]

    Parameters
    ----------
    belief : dict
        Probability distribution over the other player's types.

    Returns
    -------
    str
        Bayesian best-response action.
    """

    action_costs = evaluate_actions(
        belief
    )

    return min(
        action_costs,
        key=action_costs.get
    )


def compare_actions(belief):
    """
    Compare the expected costs of all actions.

    Parameters
    ----------
    belief : dict
        Probability distribution over the other player's types.

    Returns
    -------
    None
        Prints the expected cost and identifies the best action.
    """

    action_costs = evaluate_actions(
        belief
    )

    print("Expected costs:")

    for action, cost in action_costs.items():

        print(
            f"  {action}: {cost:.2f}"
        )

    best_action = bayesian_best_response(
        belief
    )

    print(
        f"\nBayesian Best Response: "
        f"{best_action}"
    )


if __name__ == "__main__":

    # Example belief:
    #
    # P(Risk-Averse) = 0.4
    # P(Risk-Neutral) = 0.6

    belief = {
        "risk_averse": 0.4,
        "risk_neutral": 0.6,
    }

    compare_actions(
        belief
    )
```
