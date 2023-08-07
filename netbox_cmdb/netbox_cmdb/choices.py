from utilities.choices import ChoiceSet


class AssetStateChoices(ChoiceSet):
    """A ChoiceSet to define the state of an asset."""

    STATE_PRODUCTION = "production"
    STATE_MAINTENANCE = "maintenance"
    STATE_STAGING = "staging"
    STATE_OUT_OF_SERVICE = "out_of_service"

    CHOICES = [
        (STATE_PRODUCTION, "Production", "green"),
        (STATE_MAINTENANCE, "Maintenance", "orange"),
        (STATE_STAGING, "Staging", "blue"),
        (STATE_OUT_OF_SERVICE, "Out of service", "gray"),
    ]


class AssetMonitoringStateChoices(ChoiceSet):
    """A ChoiceSet to define the monitoring state of an asset independently of its state."""

    CRITICAL = "critical"
    WARNING = "warning"
    DISABLED = "disabled"

    CHOICES = (
        (CRITICAL, "Critical"),
        (WARNING, "Warning"),
        (DISABLED, "Disabled"),
    )


class DecisionChoice(ChoiceSet):
    """A ChoiceSet that could be used in many network related objects:
    ACLs, route policies, BGP community lists, etc..."""

    PERMIT = "permit"
    DENY = "deny"

    CHOICES = (
        (PERMIT, "Permit"),
        (DENY, "Deny"),
    )
