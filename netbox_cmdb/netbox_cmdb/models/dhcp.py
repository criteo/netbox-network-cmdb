"""DHCP relay models."""

from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb import protect


def dhcp_relay_interface_errors(logical_interface):
    """Return the reasons why a DHCP relay cannot be stored on `logical_interface`, keyed by field.

    Shared by DhcpRelayInterface.clean() (plugin UI and Django admin forms) and by the API
    serializer, as DRF does not call full_clean().
    """
    if logical_interface is not None and logical_interface.type != "l3":
        return {
            "logical_interface": [
                f"{logical_interface.name} is of type {logical_interface.type}: "
                "a DHCP relay can only be set on a l3 logical interface."
            ]
        }
    return {}


class DhcpServer(ChangeLoggedModel):
    """A DHCP server."""

    # SONiC lists the servers of a relay by address, so an address can only appear once.
    server_address = models.GenericIPAddressField(blank=False, null=False, unique=True)

    class Meta:
        verbose_name_plural = "Dhcp Servers"

    def __str__(self):
        return f"{self.server_address}"


@protect.from_device_name_change("logical_interface__parent_interface__device")
class DhcpRelayInterface(ChangeLoggedModel):
    """
    A DHCP relay configuration for a routed (l3) logical interface
    N:M relationship with DhcpServer

    SONiC keys DHCP_RELAY by the port name, which is the name of the parent interface.
    """

    server_list = models.ManyToManyField(
        to=DhcpServer, related_name="%(class)s_dhcp_server", blank=True, default=None
    )

    # One relay configuration per logical interface
    logical_interface = models.OneToOneField(
        to="LogicalInterface",
        related_name="%(class)s",
        on_delete=models.CASCADE,
        help_text="The l3 logical interface the DHCP relay is set on.",
    )

    class Meta:
        verbose_name = "Dhcp Relay Interface"
        verbose_name_plural = "Dhcp Relay Interfaces"

    def __str__(self):
        return f"{self.device.name}--{self.logical_interface.name}--DhcpRelay"

    @property
    def device(self):
        """The device the relay belongs to, through its logical interface."""
        return self.logical_interface.parent_interface.device

    def clean(self):
        """Validate the relay for every ModelForm based surface (plugin UI and Django admin).

        DRF does not call full_clean(), the API enforces the same rule in
        DhcpRelayInterfaceSerializer.validate().
        """
        super().clean()
        errors = dhcp_relay_interface_errors(
            self.logical_interface if self.logical_interface_id else None
        )
        if errors:
            raise ValidationError(errors)
