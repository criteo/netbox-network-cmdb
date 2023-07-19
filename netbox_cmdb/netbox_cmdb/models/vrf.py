# This file is a rework of netbox/ipam/models/vrfs.py
# We prefer all CMDB models to be inside the netbox_cmdb plugin
from django.db import models
from netbox.models import ChangeLoggedModel


class VRF(ChangeLoggedModel):
    """
    A virtual routing and forwarding (VRF) table represents a discrete layer three forwarding domain (e.g. a routing
    table).
    """

    name = models.CharField(max_length=100, unique=True)
    tenant = models.ForeignKey(
        to="tenancy.Tenant", on_delete=models.PROTECT, related_name="_vrfs", blank=True, null=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "VRF"
        verbose_name_plural = "VRFs"

    def __str__(self):
        return self.name
