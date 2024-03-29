"""Route Policy views."""

from netbox_cmdb import filtersets

from netbox_cmdb.api.route_policy.serializers import WritableRoutePolicySerializer
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.route_policy import RoutePolicy


class RoutePolicyViewSet(CustomNetBoxModelViewSet):
    queryset = RoutePolicy.objects.all()
    serializer_class = WritableRoutePolicySerializer
    filterset_fields = [
        "id",
        "name",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset
