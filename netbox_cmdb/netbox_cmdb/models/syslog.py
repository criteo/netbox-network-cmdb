from django.db import models
from netbox.models import ChangeLoggedModel
from netbox_cmdb import protect


class SyslogServer(ChangeLoggedModel):
    """A Syslog server."""

    server_address = models.GenericIPAddressField(blank=False, null=False)

    class Meta:
        verbose_name_plural = "Syslog Servers"

    def __str__(self):
        return f"{self.server_address}"


@protect.from_device_name_change("device")
class Syslog(ChangeLoggedModel):
    """
    A Syslog configuration for a device
    N:M relationship with SyslogServer
    """

    server_list = models.ManyToManyField(
        to=SyslogServer,
        related_name="%(class)s_syslog_server",
        blank=True,
        default=None
    )        

    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = "Syslog"

    def __str__(self):
        return f"{self.device.name}-Syslog"

