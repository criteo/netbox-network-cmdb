from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import ChangeLoggedModel
from utilities.querysets import RestrictedQuerySet

from netbox_cmdb.choices import DecisionChoice
from netbox_cmdb.fields import CustomIPAddressField


class RoutePolicy(ChangeLoggedModel):
    """
    A RoutePolicy contains a name and a description and is optionally linked to a Device.
    It could be applied to a DeviceBGPSession
    It is referred by RoutePolicyTerms objects to populate its content.
    """

    name = models.CharField(max_length=100)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )
    description = models.CharField(max_length=100, blank=True)
    objects = RestrictedQuerySet.as_manager()

    def __str__(self):
        return f"{self.device}-{self.name}"

    def __repr__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:routepolicy", args=[self.pk])

    class Meta:
        verbose_name_plural = "Route Policies"
        unique_together = ["device", "name"]


class RoutePolicyTerm(ChangeLoggedModel):
    """Route Policy term"""

    ORIGIN = (
        ("igp", ("IGP")),
        ("egp", ("EGP")),
        ("incomplete", ("INCOMPLETE")),
    )

    ROUTE_TYPE = (
        ("ibgp", ("IBGP")),
        ("ebgp", ("EBGP")),
    )

    SOURCE_PROTOCOL = (
        ("bgp", ("BGP")),
        ("isis", ("IS-IS")),
        ("static", ("Static")),
        ("connected", ("Connected")),
        ("ospf", ("OSPF")),
    )

    route_policy = models.ForeignKey(
        to="RoutePolicy", on_delete=models.CASCADE, related_name="route_policy_term"
    )
    description = models.CharField(max_length=100, blank=True)
    sequence = models.PositiveIntegerField()
    decision = models.CharField(
        max_length=10,
        choices=DecisionChoice,
        default=DecisionChoice.PERMIT,
    )

    # match
    from_bgp_community = models.CharField(max_length=100, blank=True)
    from_bgp_community_list = models.ForeignKey(
        to="BgpCommunityList", on_delete=models.PROTECT, null=True, blank=True
    )
    from_prefix_list = models.ForeignKey(
        to="PrefixList", on_delete=models.PROTECT, null=True, blank=True
    )
    from_source_protocol = models.CharField(max_length=32, choices=SOURCE_PROTOCOL, blank=True)
    from_route_type = models.CharField(max_length=32, choices=ROUTE_TYPE, blank=True)
    from_local_pref = models.PositiveBigIntegerField(blank=True, null=True)

    # set
    set_local_pref = models.PositiveBigIntegerField(blank=True, null=True)
    set_community = models.CharField(max_length=100, blank=True)
    set_origin = models.CharField(max_length=32, choices=ORIGIN, blank=True)
    set_metric = models.PositiveBigIntegerField(blank=True, null=True)
    set_large_community = models.CharField(max_length=100, blank=True)
    set_as_path_prepend_asn = models.ForeignKey(
        to="ASN",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(class)slocal_asn",
    )
    set_as_path_prepend_repeat = models.PositiveSmallIntegerField(blank=True, null=True)
    set_next_hop = CustomIPAddressField(null=True, blank=True)

    def __str__(self):
        return str(f"{self.route_policy} seq:{self.sequence} decision:{self.decision}")

    @staticmethod
    def validate_device_consistency(device, from_bgp_community_list, from_prefix_list):
        errors = []
        if from_bgp_community_list and from_bgp_community_list.device_id != device.id:
            error = ValidationError(
                "%(field)s is not on the same device",
                code="device_mismatch",
                params={"field": "from_bgp_community_list"},
            )
            errors.append(error)

        if from_prefix_list and from_prefix_list.device_id != device.id:
            error = ValidationError(
                "%(field)s is not on the same device",
                code="device_mismatch",
                params={"field": "from_prefix_list"},
            )
            errors.append(error)

        if errors:
            raise ValidationError(errors)

    def clean(self):
        self.validate_device_consistency(
            self.route_policy.device, self.from_bgp_community_list, self.from_prefix_list
        )

    class Meta:
        unique_together = ("route_policy", "sequence")
        verbose_name_plural = "Route Policy terms"
        ordering = ["sequence"]
