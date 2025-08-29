from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.api.vlan.serializers import VLANSerializer
from netbox_cmdb.models.vlan import VLAN


class VLANViewSet(CustomNetBoxModelViewSet):
    queryset = VLAN.objects.all()
    serializer_class = VLANSerializer
    filterset_fields = [
        "id",
        "vid",
        "name",
        "description",
        "tenant__id",
        "tenant__name",
    ]
