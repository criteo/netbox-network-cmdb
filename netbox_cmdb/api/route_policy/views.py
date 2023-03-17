"""Route Policy views."""

from netbox.api.viewsets import NetBoxModelViewSet

from netbox_cmdb.api.route_policy.serializers import WritableRoutePolicySerializer
from netbox_cmdb.models.route_policy import RoutePolicy


class RoutePolicyViewSet(NetBoxModelViewSet):
    queryset = RoutePolicy.objects.all()
    serializer_class = WritableRoutePolicySerializer
    filterset_fields = ["id", "name", "device__id", "device__name"]
