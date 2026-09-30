from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb.choices import SonicDeviceTypeChoices


class SonicRoleMapping(ChangeLoggedModel):
    """Maps a DCIM device role to the SONiC device type, DEVICE_METADATA|localhost.type."""

    device_role = models.OneToOneField(
        to="dcim.DeviceRole",
        on_delete=models.CASCADE,
        related_name="sonic_role_mapping",
    )
    sonic_type = models.CharField(
        max_length=50,
        choices=SonicDeviceTypeChoices,
        default=SonicDeviceTypeChoices.NOT_PROVISIONED,
    )

    class Meta:
        ordering = ["device_role__name"]
        verbose_name = "SONiC Role Mapping"
        verbose_name_plural = "SONiC Role Mappings"

    def __str__(self):
        return f"{self.device_role} -> {self.sonic_type}"
