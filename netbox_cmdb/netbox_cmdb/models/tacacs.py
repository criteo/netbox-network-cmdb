from collections import Counter

from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb import protect
from netbox_cmdb.constants import MIN_TACACS_PASSKEY_LENGTH


def duplicate_priorities(servers):
    """Return the priorities shared by more than one server of a single configuration.

    SONiC keys its TACPLUS_SERVER table by address and relies on priority alone to order the
    servers, so two servers sharing a priority leaves the failover order undefined.
    """
    priorities = Counter(server.priority for server in servers)
    return sorted(priority for priority, count in priorities.items() if count > 1)


class TacacsServer(ChangeLoggedModel):
    """A Tacacs server."""

    # SONiC keys its TACPLUS_SERVER table by address, so an address can only appear once.
    server_address = models.GenericIPAddressField(blank=False, null=False, unique=True)
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

    def clean(self):
        """Validate the passkey for every ModelForm based surface (plugin UI and Django admin).

        DRF does not call full_clean(), the API enforces the same rule in
        TacacsSerializer.validate_passkey().
        """
        super().clean()
        if self.passkey and len(self.passkey) < MIN_TACACS_PASSKEY_LENGTH:
            raise ValidationError(
                {
                    "passkey": f"passkey should contain at least "
                    f"{MIN_TACACS_PASSKEY_LENGTH} characters."
                }
            )

    def serialize_object(self):
        """Keep the passkey out of the change log: it is a secret, diffing it has no value.

        This only affects change logging, the REST API still exposes the passkey as
        configuration generation needs it.
        """
        data = super().serialize_object()
        data.pop("passkey", None)
        return data

    def __str__(self):
        return f"{self.device.name}-Tacacs"
