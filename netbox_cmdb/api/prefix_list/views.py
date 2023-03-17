"""Route Policy views."""
from netbox.api.viewsets import NetBoxModelViewSet

from netbox_cmdb.api.prefix_list.serializers import PrefixListSerializer
from netbox_cmdb.models.prefix_list import PrefixList


class PrefixListViewSet(NetBoxModelViewSet):
    queryset = PrefixList.objects.all()
    serializer_class = PrefixListSerializer
    filterset_fields = ["id", "name", "ip_version", "device__id", "device__name"]
