import re
from collections import Counter

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import ChangeLoggedModel
from utilities.ordering import naturalize_interface

from netbox_cmdb import protect
from netbox_cmdb.choices import AssetMonitoringStateChoices, AssetStateChoices

FEC_CHOICES = [
    (None, "None"),
    ("auto", "Auto"),
    ("rs", "Reed Solomon"),
    ("fc", "FireCode"),
]

LOGICAL_INTERFACE_TYPE_CHOICES = [
    ("l1", "L1"),
    ("l2", "L2"),
    ("l3", "L3"),
]
LOGICAL_INTERFACE_MODE_CHOICES = [
    (None, "None"),
    ("access", "Access"),
    ("tagged", "Tagged"),
]

# Lanes a single port can own: a breakout never splits a port into uneven parts.
PORT_LAYOUT_LANE_COUNTS = (1, 2, 4, 8)
# A breakout child is its parent port name followed by a single letter: etp3a is a child of etp3.
BREAKOUT_CHILD_NAME = re.compile(r"^(?P<parent>.*\d)[a-z]$", re.IGNORECASE)


def breakout_parent_name(name):
    """Return the lowercased parent port name of a breakout child, None if `name` is not one."""
    match = BREAKOUT_CHILD_NAME.match(name or "")
    return match.group("parent").lower() if match else None


def port_layout_lane_errors(device_type, network_role, name, lanes, exclude_pk=None):
    """Return the reasons why `lanes` cannot be assigned to a port of a given layout.

    A layout describes a single ASIC (a device type used in a network role), so its ports can't
    share a lane. The lanes of a port must be contiguous, they are kept in the provided order, and
    an empty list is accepted for the ports whose lanes are not documented.
    """
    if not lanes:
        return []

    errors = []
    duplicates = sorted(lane for lane, count in Counter(lanes).items() if count > 1)
    if duplicates:
        errors.append(f"Lanes used more than once: {duplicates}.")
    elif max(lanes) - min(lanes) + 1 != len(lanes):
        errors.append(f"Lanes must be contiguous, got {sorted(lanes)}.")
    if len(lanes) not in PORT_LAYOUT_LANE_COUNTS:
        *counts, last_count = PORT_LAYOUT_LANE_COUNTS
        errors.append(
            f"A port must use {', '.join(map(str, counts))} or {last_count} lanes, "
            f"got {len(lanes)}."
        )

    if device_type is None or network_role is None:
        return errors

    others = (
        PortLayout.objects.filter(device_type=device_type, network_role=network_role)
        .exclude(pk=exclude_pk)
        .exclude(lanes=[])
    )
    for other in others.filter(lanes__overlap=lanes).order_by("name"):
        shared = sorted(set(lanes) & set(other.lanes))
        errors.append(f"Lanes {shared} are already used by {other.name}.")

    parent = breakout_parent_name(name)
    if parent:
        for sibling in others.filter(name__istartswith=parent).order_by("name"):
            if breakout_parent_name(sibling.name) == parent and len(sibling.lanes) != len(lanes):
                errors.append(
                    f"Breakout ports of {parent} must use the same number of lanes: "
                    f"{sibling.name} uses {len(sibling.lanes)}, got {len(lanes)}."
                )

    return errors


@protect.from_device_name_change("device")
class DeviceInterface(ChangeLoggedModel):
    """A device interface configuration."""

    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    state = models.CharField(
        max_length=50,
        choices=AssetStateChoices,
        default=AssetStateChoices.STATE_STAGING,
        help_text="State of this DeviceInterface",
    )
    monitoring_state = models.CharField(
        max_length=50,
        choices=AssetMonitoringStateChoices,
        default=AssetMonitoringStateChoices.DISABLED,
        help_text="Monitoring state of this DeviceInterface",
    )
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )
    autonegotiation = models.BooleanField(default=True)
    speed = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Interface speed in kb/s",
    )
    fec = models.CharField(
        choices=FEC_CHOICES,
        max_length=5,
        blank=True,
        null=True,
    )
    description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.device.name}--{self.name}"

    def get_state_color(self):
        return AssetStateChoices.colors.get(self.state)

    def get_monitoring_state_color(self):
        return AssetMonitoringStateChoices.colors.get(self.monitoring_state)

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:deviceinterface", args=[self.pk])

    class Meta:
        unique_together = ("device", "name")


@protect.from_ip_address_change("ipv4_address", "ipv6_address")
class LogicalInterface(ChangeLoggedModel):
    """A logical interface configuration."""

    index = models.PositiveSmallIntegerField()
    enabled = models.BooleanField(default=True)
    state = models.CharField(
        max_length=50,
        choices=AssetStateChoices,
        default=AssetStateChoices.STATE_STAGING,
        help_text="State of this LogicalInterface",
    )
    monitoring_state = models.CharField(
        max_length=50,
        choices=AssetMonitoringStateChoices,
        default=AssetMonitoringStateChoices.DISABLED,
        help_text="Monitoring state of this LogicalInterface",
    )
    parent_interface = models.ForeignKey(
        to="DeviceInterface", related_name="%(class)s", on_delete=models.CASCADE
    )
    mtu = models.PositiveIntegerField(blank=True, null=True)
    type = models.CharField(
        choices=LOGICAL_INTERFACE_TYPE_CHOICES,
        max_length=2,
        default=None,
    )
    vrf = models.ForeignKey(
        to="VRF", related_name="%(class)s_vrf", on_delete=models.CASCADE, blank=True, null=True
    )
    ipv4_address = models.ForeignKey(
        to="ipam.IPAddress",
        related_name="%(class)s_ipv4_address",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    ipv6_address = models.ForeignKey(
        to="ipam.IPAddress",
        related_name="%(class)s_ipv6_address",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    use_ipv6_link_local_only = models.BooleanField(
        default=False,
        help_text="Use only the IPv6 link-local address, without a global IPv6 address.",
    )
    mode = models.CharField(
        choices=LOGICAL_INTERFACE_MODE_CHOICES,
        blank=True,
        null=True,
        default=None,
        max_length=20,
        help_text="Interface mode (802.1Q)",
    )
    untagged_vlan = models.ForeignKey(
        to="VLAN",
        related_name="%(class)s_untagged_vlan",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    tagged_vlans = models.ManyToManyField(
        to="VLAN", related_name="%(class)s_tagged_vlans", blank=True, default=None
    )
    native_vlan = models.ForeignKey(
        to="VLAN",
        related_name="%(class)s_native_vlan",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.parent_interface.name}--{self.index}"

    @property
    def name(self):
        """Conventional display name, e.g. `ge-0/0/32.0`."""
        return f"{self.parent_interface.name}.{self.index}"

    def get_state_color(self):
        return AssetStateChoices.colors.get(self.state)

    def get_monitoring_state_color(self):
        return AssetMonitoringStateChoices.colors.get(self.monitoring_state)

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:logicalinterface", args=[self.pk])

    def clean(self):
        # List of checks to perform
        # The M2M can only be inspected once the instance has a PK (on creation,
        # tagged VLANs are assigned after the initial save anyway).
        if self.untagged_vlan and (self.native_vlan or (self.pk and self.tagged_vlans.exists())):
            raise ValidationError(
                "Untagged VLAN cannot be combined with tagged VLANs or native VLAN."
            )

        super(LogicalInterface, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(LogicalInterface, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("index", "parent_interface")


class Link(ChangeLoggedModel):
    """A link between two DeviceInterface."""

    interface_a = models.ForeignKey(
        to="DeviceInterface",
        related_name="%(class)s_interface_a",
        on_delete=models.CASCADE,
    )
    interface_b = models.ForeignKey(
        to="DeviceInterface",
        related_name="%(class)s_interface_b",
        on_delete=models.CASCADE,
    )
    state = models.CharField(
        max_length=50,
        choices=AssetStateChoices,
        default=AssetStateChoices.STATE_STAGING,
        help_text="State of this Link",
    )
    monitoring_state = models.CharField(
        max_length=50,
        choices=AssetMonitoringStateChoices,
        default=AssetMonitoringStateChoices.DISABLED,
        help_text="Monitoring state of this Link",
    )

    def __str__(self):
        return f"{self.interface_a} <--> {self.interface_b}"

    def get_state_color(self):
        return AssetStateChoices.colors.get(self.state)

    def get_monitoring_state_color(self):
        return AssetMonitoringStateChoices.colors.get(self.monitoring_state)

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:link", args=[self.pk])


class PortLayout(ChangeLoggedModel):
    """A port layout configuration on a Network device."""

    device_type = models.ForeignKey(
        to="dcim.DeviceType",
        related_name="%(class)s_device_type",
        on_delete=models.CASCADE,
        help_text="The hardware associated with this PortLayout",
    )
    network_role = models.ForeignKey(
        to="dcim.DeviceRole",
        related_name="%(class)s_network_role",
        on_delete=models.CASCADE,
        help_text="The specific network role this port layout is designed to support.",
    )
    name = models.CharField(max_length=64, help_text="The generic name assigned to the interface.")
    label_name = models.CharField(
        max_length=64, help_text="The physical label name of the interface on the device."
    )
    logical_name = models.CharField(
        max_length=64, help_text="The logical name used to identify the interface in the system."
    )
    vendor_name = models.CharField(
        max_length=64, help_text="The vendor-specific name of the interface."
    )
    vendor_short_name = models.CharField(
        max_length=64, help_text="The short vendor-specific name of the interface."
    )
    vendor_long_name = models.CharField(
        max_length=64, help_text="The long vendor-specific name of the interface."
    )
    lanes = ArrayField(
        base_field=models.PositiveSmallIntegerField(),
        blank=True,
        default=list,
        help_text="The ASIC lanes used by the interface, in hardware order (e.g. 0,1,2,3).",
    )

    def __str__(self):
        return f"{self.device_type}--{self.network_role}--{self.name}"

    @property
    def lanes_display(self):
        """Lanes as a comma-separated string, e.g. `0,1,2,3`."""
        return ",".join(str(lane) for lane in self.lanes)

    @property
    def natural_name(self):
        """Naturalized version of `name`, suitable as a sort key (etp2 before etp10).

        Lowercased first, since Python string comparison is case-sensitive and would
        otherwise sort e.g. `etp5B` before `etp5a`.
        """
        return naturalize_interface(self.name.lower(), max_length=100)

    def get_absolute_url(self):
        return reverse("plugins:netbox_cmdb:portlayout", args=[self.pk])

    def clean(self):
        """Validate the lanes for every ModelForm based surface (plugin UI and Django admin).

        DRF does not call full_clean(), the API enforces the same rules in
        PortLayoutSerializer.validate().
        """
        super().clean()
        errors = port_layout_lane_errors(
            self.device_type if self.device_type_id else None,
            self.network_role if self.network_role_id else None,
            self.name,
            self.lanes,
            exclude_pk=self.pk,
        )
        if errors:
            raise ValidationError({"lanes": errors})
