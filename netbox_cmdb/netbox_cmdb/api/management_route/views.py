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
    filterset_fields = [
        "id",
        "logical_interface__id",
        "logical_interface__index",
        "logical_interface__parent_interface__id",
        "logical_interface__parent_interface__name",
        "logical_interface__parent_interface__device__id",
        "logical_interface__parent_interface__device__name",
        "kind",
    ] + filtersets.logical_interface_device_location_filterset
