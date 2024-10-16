from django.db import models
from netbox.models import ChangeLoggedModel

from netbox_cmdb import protect


@protect.from_device_name_change("device")
class BGPCommunityList(ChangeLoggedModel):
    """An object used in RoutePolicy object to filter on a list of BGP communities."""

    name = models.CharField(max_length=100)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="%(class)sdevice",
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.device}-{self.name}"

    class Meta:
        unique_together = ("name", "device")
        verbose_name_plural = "BGP community lists"


class BGPCommunityListTerm(ChangeLoggedModel):
    bgp_community_list = models.ForeignKey(
        to="BgpCommunityList",
        on_delete=models.CASCADE,
        related_name="bgp_community_list_term",
    )
    sequence = models.PositiveIntegerField()
    community = models.CharField(max_length=100)

    def __str__(self):
        return str(f"{self.bgp_community_list} seq:{self.sequence}")

    class Meta:
        unique_together = ("bgp_community_list", "sequence")
        verbose_name_plural = "BGP community list terms"
        ordering = ["sequence"]
