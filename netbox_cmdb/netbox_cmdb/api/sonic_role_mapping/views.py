"""SONiC role mapping views."""

from netbox_cmdb.api.sonic_role_mapping.serializers import SonicRoleMappingSerializer
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.sonic_role_mapping import SonicRoleMapping


class SonicRoleMappingViewSet(CustomNetBoxModelViewSet):
    """
    CRUD for SONiC Role Mapping objects.
    """

    queryset = SonicRoleMapping.objects.select_related("device_role")
    serializer_class = SonicRoleMappingSerializer

    filterset_fields = [
        "device_role",
        "device_role__name",
        "device_role__slug",
        "sonic_type",
    ]
