"""Route Policy serializers."""

from rest_framework.serializers import ModelSerializer, ValidationError

from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.constants import MAX_COMMUNITY_PER_DEVICE


class SNMPCommunitySerializer(ModelSerializer):

    class Meta:
        model = SNMPCommunity
        fields = "__all__"


class SNMPCommunityReadSerializer(ModelSerializer):

    class Meta:
        model = SNMPCommunity
        fields = ["name", "community", "type"]


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

    def validate_community_list(self, value):
        if len(value) > MAX_COMMUNITY_PER_DEVICE:
            raise ValidationError(
                f"You cannot select more than {MAX_COMMUNITY_PER_DEVICE} SNMP Communities."
            )
        return value
