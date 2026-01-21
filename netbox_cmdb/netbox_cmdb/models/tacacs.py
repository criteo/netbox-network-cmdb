from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb import protect


class TacacsServer(ChangeLoggedModel):
    """A Tacacs server."""

    server_address = models.GenericIPAddressField(blank=False, null=False)
    priority = models.PositiveIntegerField(default=1)
    tcp_port = models.PositiveIntegerField(default=49)

    class Meta:
        verbose_name_plural = "Tacacs Servers"

    def __str__(self):
        return f"{self.server_address} (prio {self.priority}, port {self.tcp_port})"


@protect.from_device_name_change("device")
class Tacacs(ChangeLoggedModel):
    """
    A TACACS configuration for a device
    N:M relationship with TacacsServer + global settings
    """

    # Global config for the device
    passkey = models.CharField(max_length=128, blank=True, null=True)

    # TACACS server_list
    server_list = models.ManyToManyField(
        to=TacacsServer, related_name="%(class)s_tacacs_server", blank=True, default=None
    )

    # One configuration per device
    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = "Tacacs"

    def __str__(self):
        return f"{self.device.name}-Tacacs"
