from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb.choices import AssetMonitoringStateChoices, AssetStateChoices

FEC_CHOICES = [
    (None, "None"),
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


class DeviceInterface(ChangeLoggedModel):
    """A device interface configuration."""

    name = models.CharField(max_length=100)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )
    autonegotiation = models.BooleanField(default=True)
    speed = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(800000000)],
        blank=True,
        null=True,
        help_text="Interface speed in kB/s",
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

    class Meta:
        unique_together = ("device", "name")


class LogicalInterface(ChangeLoggedModel):
    """A logical interface configuration."""

    index = models.PositiveSmallIntegerField()
    parent_interface = models.ForeignKey(
        to="DeviceInterface",
        related_name="%(class)s",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
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
        return str(f"{self.interface_a} <--> {self.interface_b}")


class PortLayout(ChangeLoggedModel):
    """A port layout configuration on a Network device."""

    device_type = models.ForeignKey(
        to="dcim.DeviceType", related_name="%(class)s_device_type", on_delete=models.CASCADE
    )
    network_role = models.ForeignKey(
        to="dcim.DeviceRole", related_name="%(class)s_network_role", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64)
    label_name = models.CharField(max_length=64)
    logical_name = models.CharField(max_length=64)
    vendor_name = models.CharField(max_length=64)
    vendor_short_name = models.CharField(max_length=64)
    vendor_long_name = models.CharField(max_length=64)
