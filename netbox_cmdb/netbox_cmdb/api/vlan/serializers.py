from netbox.api.serializers import WritableNestedSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from tenancy.api.nested_serializers import NestedTenantSerializer

from netbox_cmdb.models.vlan import VLAN


class VLANSerializer(ModelSerializer):
    tenant = NestedTenantSerializer(required=False, many=False, allow_null=True)
    display = SerializerMethodField(read_only=True)

    class Meta:
        model = VLAN
        fields = "__all__"

    def get_display(self, obj):
        return str(obj)


class NestedVLANSerializer(WritableNestedSerializer):
    class Meta:
        model = VLAN
        fields = ["id", "vid", "name", "description", "tenant"]
