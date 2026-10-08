from django.db import models
from netbox.models import ChangeLoggedModel


class SonicHwskuMapping(ChangeLoggedModel):
    """Maps a DCIM device type (model) to the SONiC HwSKU, DEVICE_METADATA|localhost.hwsku."""

    device_type = models.OneToOneField(
        to="dcim.DeviceType",
        on_delete=models.CASCADE,
        related_name="sonic_hwsku_mapping",
    )
    # Free text: the HwSKUs are the directories of each platform in
    # /usr/share/sonic/device/<platform>/, which vary per vendor and image.
    hwsku = models.CharField(max_length=255)

    class Meta:
        ordering = ["device_type__model"]
        verbose_name = "SONiC HwSKU Mapping"
        verbose_name_plural = "SONiC HwSKU Mappings"

    def __str__(self):
        return f"{self.device_type} -> {self.hwsku}"
