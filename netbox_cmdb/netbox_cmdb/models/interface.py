from django.db import models
from netbox_cmdb.choices import AssetStateChoices, AssetMonitoringStateChoices
from netbox.models import ChangeLoggedModel

FEC_CHOICES = [
    (None, "None"),
    ("rs", "Reed Solomon"),
    ("fc", "FireCode"),
]


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
