from utilities.choices import ChoiceSet


class SNMPCommunityType(ChoiceSet):
    """A ChoiceSet to define the communityType."""

    RO = "readonly"
    RW = "readwrite"

    CHOICES = [
        (RO, "ReadOnly", "green"),
        (RW, "Read&Write", "red"),
    ]


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
        (CRITICAL, "Critical", "red"),
        (WARNING, "Warning", "orange"),
        (DISABLED, "Disabled", "gray"),
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


class SonicDeviceTypeChoices(ChoiceSet):
    """The DEVICE_METADATA|localhost.type values supported, a subset of what SONiC accepts.

    Choices can be seen here: https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-device_metadata.yang
    (do not forget to change master by the branch you want).
    Not all types are implemented.
    """

    TOR_ROUTER = "ToRRouter"
    LEAF_ROUTER = "LeafRouter"
    SPINE_ROUTER = "SpineRouter"
    NOT_PROVISIONED = "not-provisioned"

    CHOICES = [
        (TOR_ROUTER, TOR_ROUTER),
        (LEAF_ROUTER, LEAF_ROUTER),
        (SPINE_ROUTER, SPINE_ROUTER),
        (NOT_PROVISIONED, NOT_PROVISIONED),
    ]
