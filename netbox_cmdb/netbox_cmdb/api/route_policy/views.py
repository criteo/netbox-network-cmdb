"""Route Policy views."""

from netbox_cmdb.api.route_policy.serializers import WritableRoutePolicySerializer
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.filtersets import RoutePolicyFilterSet
from netbox_cmdb.models.route_policy import RoutePolicy


class RoutePolicyViewSet(CustomNetBoxModelViewSet):
    queryset = RoutePolicy.objects.all()
    serializer_class = WritableRoutePolicySerializer
    filterset_class = RoutePolicyFilterSet
