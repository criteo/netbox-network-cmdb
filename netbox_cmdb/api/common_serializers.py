from dcim.models import Device
from netbox.api.serializers import WritableNestedSerializer


class CommonDeviceSerializer(WritableNestedSerializer):
    class Meta:
        model = Device
        fields = ["id", "name"]
