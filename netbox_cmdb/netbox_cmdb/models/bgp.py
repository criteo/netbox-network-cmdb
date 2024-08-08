from dcim.models.devices import Device
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from netbox.models import ChangeLoggedModel
from utilities.choices import ChoiceSet
from utilities.querysets import RestrictedQuerySet

from netbox_cmdb.choices import AssetMonitoringStateChoices, AssetStateChoices
from netbox_cmdb.constants import BGP_MAX_ASN, BGP_MIN_ASN


class BGPGlobal(ChangeLoggedModel):
    """Global BGP configuration.

    One device can have multiple configuration, as there are possibily VRF.
    Note: VRF are not implemented yet.
    """

    # TODO: once VRF will be implemented, attach to the VRF instead of directly to the device
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )

    local_asn = models.ForeignKey(
        to="ASN",
        on_delete=models.PROTECT,
        blank=False,
        related_name="%(class)slocal_asn",
    )
    router_id = models.CharField(max_length=100, default="", blank=True)

    ebgp_administrative_distance = models.PositiveIntegerField(blank=True, null=True)
    ibgp_administrative_distance = models.PositiveIntegerField(blank=True, null=True)

    graceful_restart = models.BooleanField()
    graceful_restart_time = models.PositiveIntegerField(blank=True, null=True)

    ecmp = models.BooleanField(default=True, help_text="field ignored for JunOS")
    ecmp_maximum_paths = models.PositiveIntegerField(
        default=32, validators=[MinValueValidator(1)], help_text="field ignored for JunOS"
    )

    def __str__(self):
        return str(self.device)

    class Meta:
        verbose_name = "BGP global configuration"


class AfiSafiChoices(ChoiceSet):
    IPV4_UNICAST = "ipv4-unicast"
    IPV6_UNICAST = "ipv6-unicast"
    L2VPN_EVPN = "l2vpn-evpn"
    IPV4_FLOWSPEC = "ipv4-flowspec"

    CHOICES = (
        (IPV4_UNICAST, "ipv4-unicast"),
        (IPV6_UNICAST, "ipv6-unicast"),
        (L2VPN_EVPN, "l2vpn-evpn"),
        (IPV4_FLOWSPEC, "ipv4-flowspec"),
    )


class AfiSafi(ChangeLoggedModel):
    """An AfiSafi represents AFI/SAFI capabilities configured for a Device BGP session."""

    afi_safi_name = models.CharField(
        max_length=50,
        choices=AfiSafiChoices,
        help_text="AFI SAFI",
    )
    route_policy_in = models.ForeignKey(
        to="RoutePolicy",
        related_name="%(class)s_in",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    route_policy_out = models.ForeignKey(
        to="RoutePolicy",
        related_name="%(class)s_out",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    device_bgp_session = models.ForeignKey(
        to="DeviceBGPSession",
        related_name="afi_safis",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.afi_safi_name)

    @staticmethod
    def validate_device_consistency(device, route_policy_in, route_policy_out):
        errors = []
        if route_policy_in and route_policy_in.device_id != device.id:
            error = ValidationError(
                "%(field)s is not on the same device",
                code="device_mismatch",
                params={"field": "route_policy_in"},
            )
            errors.append(error)

        if route_policy_out and route_policy_out.device_id != device.id:
            error = ValidationError(
                "%(field)s is not on the same device",
                code="device_mismatch",
                params={"field": "route_policy_out"},
            )
            errors.append(error)

        if errors:
            raise ValidationError(errors)

    def clean(self):
        self.validate_device_consistency(
            self.device_bgp_session.device, self.route_policy_in, self.route_policy_out
        )

    class Meta:
        unique_together = ("device_bgp_session", "afi_safi_name")


class ASN(ChangeLoggedModel):
    """ASN.

    - number
    - organization_name
    """

    organization_name = models.CharField(max_length=100, unique=True)
    number = models.PositiveBigIntegerField(
        validators=[MinValueValidator(BGP_MIN_ASN), MaxValueValidator(BGP_MAX_ASN)]
    )

    objects = RestrictedQuerySet.as_manager()

    def __str__(self):
        return str(self.number)

    class Meta:
        verbose_name_plural = "AS Numbers"

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:asn", args=[self.pk])

    def get_available_asns(self, min_asn, max_asn):
        """
        Return all available ASNs in a given range.
        """
        available_asns = {asn for asn in range(min_asn, max_asn + 1)}
        available_asns -= set(self.__class__.objects.all().values_list("number", flat=True))

        return sorted(available_asns)


class BGPSessionCommon(ChangeLoggedModel):
    """BGPSessionCommon is an abstract model containing common attributes that
    could be inherited to a BGP session or Peer Group models."""

    local_asn = models.ForeignKey(
        to="ASN",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)slocal_asn",
    )
    description = models.CharField(max_length=100, default="", blank=True)
    enforce_first_as = models.BooleanField(default=True)
    route_policy_in = models.ForeignKey(
        to="RoutePolicy",
        related_name="%(class)s_in",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    route_policy_out = models.ForeignKey(
        to="RoutePolicy",
        related_name="%(class)s_out",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class BGPPeerGroup(BGPSessionCommon):
    """A BGP Peer Group contains a set of BGP neighbors that shares common attributes."""

    remote_asn = models.ForeignKey(
        to="ASN",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="%(class)sremote_asn",
    )
    name = models.CharField(max_length=100)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )

    objects = RestrictedQuerySet.as_manager()

    def __str__(self):
        return f"{self.device.name}--{self.name}"

    class Meta:
        verbose_name_plural = "BGP Peer Groups"
        unique_together = ("device", "name")

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:bgppeergroup", args=[self.pk])


class DeviceBGPSession(BGPSessionCommon):
    """A Device BGP Session is a BGP session from a given device's perspective.
    It contains BGP local parameters for the given devices (as the local address / ASN)."""

    device = models.ForeignKey(
        to="dcim.Device", on_delete=models.CASCADE, related_name="%(class)sdevice"
    )
    local_address = models.ForeignKey(
        to="ipam.IPAddress", on_delete=models.PROTECT, related_name="local_address"
    )
    # instance = models.ForeignKey(...)
    enabled = models.BooleanField(default=True)

    peer_group = models.ForeignKey(
        to="BGPPeerGroup",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="warning: changing this field will cause the reset of the BGP session",
    )
    maximum_prefixes = models.PositiveIntegerField(null=True, blank=True)

    objects = RestrictedQuerySet.as_manager()

    def __str__(self):
        return str(f"{self.device}--{self.local_asn}--{self.local_address}")

    @staticmethod
    def validate_device_consistency(device, peer_group, route_policy_in, route_policy_out):
        errors = []
        if peer_group and peer_group.device_id != device.id:
            error = ValidationError(
                "%(field)s is not on the same device",
                code="device_mismatch",
                params={"field": "peer_group"},
            )
            errors.append(error)

        if route_policy_in and route_policy_in.device_id != device.id:
            error = ValidationError(
                "%(field)s is not on the same device",
                code="device_mismatch",
                params={"field": "route_policy_in"},
            )
            errors.append(error)

        if route_policy_out and route_policy_out.device_id != device.id:
            error = ValidationError(
                "%(field)s is not on the same device",
                code="device_mismatch",
                params={"field": "route_policy_out"},
            )
            errors.append(error)

        if errors:
            raise ValidationError(errors)

    def clean(self):
        self.validate_device_consistency(
            self.device, self.peer_group, self.route_policy_in, self.route_policy_out
        )

    class Meta:
        verbose_name_plural = "Device BGP Sessions"


class BGPSession(ChangeLoggedModel):
    """A BGP Session represents a BGP session between two devices (DeviceBGPSession).
    This is where shared attributes (as session password) are stored."""

    def __str__(self):
        return str(f"{self.peer_a} <--> {self.peer_b}")

    state = models.CharField(
        max_length=50,
        choices=AssetStateChoices,
        default=AssetStateChoices.STATE_STAGING,
        help_text="State of this BGP session",
    )
    monitoring_state = models.CharField(
        max_length=50,
        choices=AssetMonitoringStateChoices,
        default=AssetMonitoringStateChoices.DISABLED,
        help_text="Monitoring state of this BGP session",
    )
    peer_a = models.ForeignKey(
        to="DeviceBGPSession", on_delete=models.CASCADE, related_name="peer_a"
    )
    peer_b = models.ForeignKey(
        to="DeviceBGPSession", on_delete=models.CASCADE, related_name="peer_b"
    )
    password = models.CharField(max_length=100, default="", blank=True)
    circuit = models.ForeignKey(
        to="Circuit",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    tenant = models.ForeignKey(to="tenancy.Tenant", on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        verbose_name_plural = "BGP Sessions"

    def validate_unique(self, exclude=None):
        # Check for a duplicate BGP session (same devices / ips).
        if BGPSession.objects.exclude(pk=self.pk).filter(
            Q(
                peer_a__device__name=self.peer_a.device.name,
                peer_a__local_address=self.peer_a.local_address,
                peer_b__device__name=self.peer_b.device.name,
                peer_b__local_address=self.peer_b.local_address,
            )
            | Q(
                peer_a__device__name=self.peer_b.device.name,
                peer_a__local_address=self.peer_b.local_address,
                peer_b__device__name=self.peer_a.device.name,
                peer_b__local_address=self.peer_a.local_address,
            )
        ):
            raise ValidationError(
                {
                    "peer_a": "A BGP session already exists between these 2 devices and IPs.",
                    "peer_b": "A BGP session already exists between these 2 devices and IPs.",
                }
            )

        super().validate_unique(exclude)

    def get_state_color(self):
        return AssetStateChoices.colors.get(self.state)

    def get_monitoring_state_color(self):
        return AssetMonitoringStateChoices.colors.get(self.monitoring_state)

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:bgpsession", args=[self.pk])
