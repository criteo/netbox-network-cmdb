"""Route Policy views."""

from rest_framework.response import Response

from netbox_cmdb import filtersets
from netbox_cmdb.api.snmp.serializers import (
    SNMPCommunitySerializer,
    SNMPReadSerializer,
    SNMPSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity


class SNMPCommunityViewSet(CustomNetBoxModelViewSet):
    queryset = SNMPCommunity.objects.all()
    serializer_class = SNMPCommunitySerializer
    filterset_fields = [
        "name",
        "community",
        "type",
    ]


class SNMPViewSet(CustomNetBoxModelViewSet):
    queryset = SNMP.objects.all()
    serializer_class = SNMPSerializer
    filterset_fields = [
        "community_list",
        "contact",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset

    def get_serializer_class(self):
        if self.action == "list":
            return SNMPReadSerializer
        return SNMPSerializer
