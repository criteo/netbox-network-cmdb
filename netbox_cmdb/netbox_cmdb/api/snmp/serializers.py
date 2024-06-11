"""Route Policy serializers."""

from rest_framework.serializers import ModelSerializer

from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.api.common_serializers import CommonDeviceSerializer


class SNMPCommunitySerializer(ModelSerializer):

    class Meta:
        model = SNMPCommunity
        fields = "__all__"


class SNMPCommunityReadSerializer(ModelSerializer):

    class Meta:
        model = SNMPCommunity
        fields = ["community", "type"]


class SNMPReadSerializer(ModelSerializer):

    device = CommonDeviceSerializer()
    community_list = SNMPCommunityReadSerializer(many=True)

    class Meta:
        model = SNMP
        fields = "__all__"


class SNMPSerializer(ModelSerializer):

    device = CommonDeviceSerializer()

    class Meta:
        model = SNMP
        fields = "__all__"
