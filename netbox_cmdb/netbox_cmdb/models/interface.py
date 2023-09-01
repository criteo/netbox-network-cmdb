from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from netbox.models import ChangeLoggedModel

FEC_CHOICES = [
    (None, "None"),
    ("rs", "Reed Solomon"),
    ("fc", "FireCode"),
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
