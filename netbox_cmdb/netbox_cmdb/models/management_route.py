"""Management route models."""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from ipam.fields import IPNetworkField
from netaddr import AddrFormatError, IPAddress, IPNetwork
from netbox.models import ChangeLoggedModel
from utilities.choices import ChoiceSet

from netbox_cmdb.fields import CustomIPAddressField


class ManagementRouteKindChoices(ChoiceSet):
    """The two kinds of entries SONiC attaches to a management interface.

    Both end up in the MGMT_INTERFACE table of CONFIG_DB:
    - a static route carries a next-hop and becomes `gwaddr`, the default route of the
      management routing table (`ip route add <prefix> via <next_hop> dev eth0 table default`);
    - a forced route carries no next-hop and becomes one entry of `forced_mgmt_routes`, a policy
      rule steering the traffic to <prefix> into the management routing table
      (`ip rule add to <prefix> lookup default`), where it resolves through the static route.
    """

    STATIC = "static"
    FORCED = "forced"

    CHOICES = [
        (STATIC, "Static", "blue"),
        (FORCED, "Forced", "purple"),
    ]


def _parse(netaddr_type, value):
    """Return `value` as a netaddr object, None when empty or not parsable."""
    if value in (None, ""):
        return None
    try:
        return netaddr_type(value)
    except (AddrFormatError, TypeError, ValueError):
        return None


def management_route_errors(logical_interface, kind, prefix, next_hop, exclude_pk=None):
    """Return the reasons why a management route cannot be stored, keyed by field.

    Shared by ManagementRoute.clean() (plugin UI and Django admin forms) and by the API
    serializer, as DRF does not call full_clean().
    """
    errors = {}

    # Unparsable values are reported by the field validation itself, skip them here.
    prefix = _parse(IPNetwork, prefix)
    next_hop = _parse(IPAddress, next_hop)

    if prefix is not None and prefix.version != 4:
        errors["prefix"] = ["Only IPv4 management routes are supported."]

    if kind == ManagementRouteKindChoices.STATIC and next_hop is None:
        errors["next_hop"] = ["A static route requires a next-hop."]
    elif kind == ManagementRouteKindChoices.FORCED and next_hop is not None:
        errors["next_hop"] = [
            "A forced route has no next-hop: it resolves through the static route."
        ]
    elif next_hop is not None and next_hop.version != 4:
        errors["next_hop"] = ["Only IPv4 management routes are supported."]

    if logical_interface is None:
        return errors

    address = logical_interface.ipv4_address
    if address is None:
        errors["logical_interface"] = [
            f"{logical_interface.name} has no IPv4 address: management routes need one."
        ]
    elif kind == ManagementRouteKindChoices.STATIC and "next_hop" not in errors:
        network = IPNetwork(str(address.address))
        if next_hop == network.ip:
            errors["next_hop"] = [
                f"The next-hop cannot be the address of {logical_interface.name} itself."
            ]
        elif next_hop not in network:
            errors["next_hop"] = [
                f"The next-hop must be in the subnet of {logical_interface.name} ({network})."
            ]

    if prefix is not None and "prefix" not in errors:
        duplicates = ManagementRoute.objects.filter(
            logical_interface=logical_interface, kind=kind, prefix=prefix
        ).exclude(pk=exclude_pk)
        if duplicates.exists():
            errors["prefix"] = [
                f"A {kind} route to {prefix} already exists on {logical_interface.name}."
            ]

    return errors


class ManagementRoute(ChangeLoggedModel):
    """A route pinned to the management interface of a device.

    One row per prefix: the default route of the management interface (kind static, with the
    gateway as next-hop) and each destination forced through the management interface (kind
    forced, no next-hop).
    """

    logical_interface = models.ForeignKey(
        to="LogicalInterface",
        related_name="%(class)s",
        on_delete=models.CASCADE,
        help_text="The management logical interface the route is attached to.",
    )
    kind = models.CharField(
        max_length=10,
        choices=ManagementRouteKindChoices,
        help_text="Static: default route of the management table. Forced: destination steered through it.",
    )
    prefix = IPNetworkField(help_text="Destination prefix, e.g. 0.0.0.0/0 for the default route.")
    next_hop = CustomIPAddressField(
        blank=True,
        null=True,
        help_text="Gateway of a static route, in the subnet of the interface. Empty for a forced route.",
    )
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ("logical_interface", "kind", "prefix")
        verbose_name = "Management Route"
        verbose_name_plural = "Management Routes"

    def __str__(self):
        return f"{self.device}--{self.logical_interface.name}--{self.kind}--{self.prefix}"

    @property
    def device(self):
        """The device the route belongs to, through its logical interface."""
        return self.logical_interface.parent_interface.device

    def get_kind_color(self):
        return ManagementRouteKindChoices.colors.get(self.kind)

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:managementroute", args=[self.pk])

    def clean(self):
        """Validate the route for every ModelForm based surface (plugin UI and Django admin).

        DRF does not call full_clean(), the API enforces the same rules in
        ManagementRouteSerializer.validate().
        """
        super().clean()
        errors = management_route_errors(
            self.logical_interface if self.logical_interface_id else None,
            self.kind,
            self.prefix,
            self.next_hop,
            exclude_pk=self.pk,
        )
        if errors:
            raise ValidationError(errors)
