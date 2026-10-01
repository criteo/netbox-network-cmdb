from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb import protect


class NTPServer(ChangeLoggedModel):
    """An NTP server."""

    name = models.CharField(max_length=100, blank=True, default="")
    server_address = models.GenericIPAddressField(blank=False, null=False, unique=True)

    class Meta:
        verbose_name = "NTP Server"
        verbose_name_plural = "NTP Servers"

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.server_address})"
        return f"{self.server_address}"


@protect.from_device_name_change("device")
class NTP(ChangeLoggedModel):
    """
    An NTP configuration for a device
    N:M relationship with NTPServer
    """

    server_list = models.ManyToManyField(
        to=NTPServer, related_name="%(class)s_ntp_server", blank=True, default=None
    )

    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "NTP"
        verbose_name_plural = "NTP"

    def __str__(self):
        return f"{self.device.name}-NTP"
