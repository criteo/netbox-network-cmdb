from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb import protect
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

    def clean(self):
        # List of checks to perform
        if self.untagged_vlan and (self.tagged_vlans.exists() or self.native_vlan):
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
