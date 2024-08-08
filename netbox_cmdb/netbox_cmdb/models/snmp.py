from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb.choices import SNMPCommunityType


class SNMPCommunity(ChangeLoggedModel):
    """A Snmp Community"""

    name = models.CharField(max_length=100, unique=True)
    community = models.CharField(max_length=31)
    type = models.CharField(
        max_length=10,
        choices=SNMPCommunityType,
        default=SNMPCommunityType.RO,
        help_text="Defines the community string permissions of either read-only RO or read-write RW",
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "SNMP Communities"


class SNMP(ChangeLoggedModel):
    """A Snmp configuration"""

    community_list = models.ManyToManyField(
        to=SNMPCommunity, related_name="%(class)s_community", blank=True, default=None
    )

    location = models.CharField(max_length=31)
    contact = models.CharField(max_length=31)

    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = "SNMP"

    def __str__(self):
        return f"SNMP configuration of {self.device.name}"
