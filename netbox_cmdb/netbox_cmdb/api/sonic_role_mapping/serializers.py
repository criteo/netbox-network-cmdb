"""SONiC role mapping serializers."""

from dcim.api.nested_serializers import NestedDeviceRoleSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator

from netbox_cmdb.models.sonic_role_mapping import SonicRoleMapping


class SonicRoleMappingSerializer(ModelSerializer):
    device_role = NestedDeviceRoleSerializer(
        validators=[
            UniqueValidator(
                queryset=SonicRoleMapping.objects.all(),
                message="This device role is already mapped to a SONiC type.",
            )
        ]
    )

    class Meta:
        model = SonicRoleMapping
        fields = "__all__"
