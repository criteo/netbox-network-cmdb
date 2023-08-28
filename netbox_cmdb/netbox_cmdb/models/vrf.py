# This file is a rework of netbox/ipam/models/vrfs.py
# We prefer all CMDB models to be inside the netbox_cmdb plugin
from django.db import models
from netbox.models import ChangeLoggedModel


class VRF(ChangeLoggedModel):
    """
    A virtual routing and forwarding (VRF) table represents a discrete layer three forwarding domain (e.g. a routing
    table).
    """

    name = models.CharField(max_length=100)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="%(class)stenant",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.device}--{self.name}"

    class Meta:
        ordering = ["name"]
        unique_together = ("device", "name")
        verbose_name = "VRF"
        verbose_name_plural = "VRFs"
