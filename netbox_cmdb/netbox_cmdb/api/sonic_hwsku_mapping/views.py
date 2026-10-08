"""SONiC HwSKU mapping views."""

from netbox_cmdb.api.sonic_hwsku_mapping.serializers import SonicHwskuMappingSerializer
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.sonic_hwsku_mapping import SonicHwskuMapping


class SonicHwskuMappingViewSet(CustomNetBoxModelViewSet):
    """
    CRUD for SONiC HwSKU Mapping objects.
    """

    queryset = SonicHwskuMapping.objects.select_related("device_type")
    serializer_class = SonicHwskuMappingSerializer

    filterset_fields = [
        "device_type",
        "device_type__model",
        "device_type__slug",
        "hwsku",
    ]
