from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.api.vrf.serializers import VRFSerializer
from netbox_cmdb.models.vrf import VRF


class VRFViewSet(CustomNetBoxModelViewSet):
    queryset = VRF.objects.all()
    serializer_class = VRFSerializer
    filterset_fields = [
        "id",
        "name",
        "tenant__id",
        "tenant__name",
    ]
