from utilities.choices import ChoiceSet


class DecisionChoice(ChoiceSet):
    """A ChoiceSet that could be used in many network related objects:
    ACLs, route policies, BGP community lists, etc..."""

    PERMIT = "permit"
    DENY = "deny"

    CHOICES = (
        (PERMIT, "Permit"),
        (DENY, "Deny"),
    )
