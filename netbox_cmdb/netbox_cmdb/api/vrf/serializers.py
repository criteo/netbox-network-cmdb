from netbox.api.serializers import WritableNestedSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from tenancy.api.nested_serializers import NestedTenantSerializer

from netbox_cmdb.models.vrf import VRF


class VRFSerializer(ModelSerializer):
    tenant = NestedTenantSerializer(required=False, many=False, allow_null=True)
    display = SerializerMethodField(read_only=True)

    class Meta:
        model = VRF
        fields = "__all__"

    def get_display(self, obj):
        return str(obj)


class NestedVRFSerializer(WritableNestedSerializer):

    class Meta:
        model = VRF
        fields = ["id", "name"]
