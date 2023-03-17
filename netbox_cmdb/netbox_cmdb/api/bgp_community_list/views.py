"""Route Policy views."""
from netbox.api.viewsets import NetBoxModelViewSet

from netbox_cmdb.api.bgp_community_list.serializers import BGPCommunityListSerializer
from netbox_cmdb.models.bgp_community_list import BGPCommunityList


class BGPCommunityListViewSet(NetBoxModelViewSet):
    queryset = BGPCommunityList.objects.all()
    serializer_class = BGPCommunityListSerializer
    filterset_fields = ["id", "name", "device__id", "device__name"]
