"""Route Policy views."""
from netbox_cmdb import filtersets
from netbox_cmdb.api.bgp_community_list.serializers import BGPCommunityListSerializer
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.bgp_community_list import BGPCommunityList


class BGPCommunityListViewSet(CustomNetBoxModelViewSet):
    queryset = BGPCommunityList.objects.all()
    serializer_class = BGPCommunityListSerializer
    filterset_fields = [
        "id",
        "name",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset
