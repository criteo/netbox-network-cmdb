"""SONiC HwSKU mapping serializers."""

from dcim.api.nested_serializers import NestedDeviceTypeSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator

from netbox_cmdb.models.sonic_hwsku_mapping import SonicHwskuMapping


class SonicHwskuMappingSerializer(ModelSerializer):
    device_type = NestedDeviceTypeSerializer(
        validators=[
            UniqueValidator(
                queryset=SonicHwskuMapping.objects.all(),
                message="This device type is already mapped to a SONiC HwSKU.",
            )
        ]
    )

    class Meta:
        model = SonicHwskuMapping
        fields = "__all__"
