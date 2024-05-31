"""Route Policy serializers."""

from rest_framework.serializers import ModelSerializer

from netbox_cmdb.models.snmp import SNMP, SNMPCommunity


class SNMPCommunitySerializer(ModelSerializer):

    class Meta:
        model = SNMPCommunity
        fields = "__all__"


class SNMPSerializer(ModelSerializer):

    class Meta:
        model = SNMP
        fields = "__all__"
