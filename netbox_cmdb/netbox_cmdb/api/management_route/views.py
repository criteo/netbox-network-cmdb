"""Management route views."""

from netbox_cmdb import filtersets
from netbox_cmdb.api.management_route.serializers import ManagementRouteSerializer
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.management_route import ManagementRoute


class ManagementRouteViewSet(CustomNetBoxModelViewSet):
    queryset = ManagementRoute.objects.select_related(
        "logical_interface__parent_interface__device", "logical_interface__ipv4_address"
    )
    serializer_class = ManagementRouteSerializer
    filterset_class = filtersets.ManagementRouteFilterSet
