# This file is a rework of netbox/ipam/models/vlans.py
# We want all CMDB models to be inside the netbox_cmdb plugin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from netbox.models import ChangeLoggedModel

# 12-bit VLAN ID (values 0 and 4095 are reserved)
VLAN_VID_MIN = 1
VLAN_VID_MAX = 4094


class VLAN(ChangeLoggedModel):
    """A VLAN is a distinct layer two forwarding domain identified by a 12-bit integer (1-4094)."""

    vid = models.PositiveSmallIntegerField(
        verbose_name="ID",
        validators=(MinValueValidator(VLAN_VID_MIN), MaxValueValidator(VLAN_VID_MAX)),
    )
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=100, blank=True)
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="%(class)stenant",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.vid}--{self.name}"

    class Meta:
        ordering = ["vid"]
        unique_together = ("vid", "name")
        verbose_name = "VLAN"
        verbose_name_plural = "VLANs"
