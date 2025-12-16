from dcim.api.nested_serializers import (
    NestedDeviceRoleSerializer,
    NestedDeviceTypeSerializer,
)
from ipam.api.nested_serializers import NestedIPAddressSerializer
from netbox.api.serializers import WritableNestedSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.api.vlan.serializers import NestedVLANSerializer
from netbox_cmdb.api.vrf.serializers import NestedVRFSerializer
from netbox_cmdb.models.interface import (
    DeviceInterface,
    Link,
    LogicalInterface,
    PortLayout,
)


class NestedDeviceInterfaceSerializer(WritableNestedSerializer):
    class Meta:
        model = DeviceInterface
        fields = ["id", "name", "device"]


class DeviceInterfaceSerializer(ModelSerializer):
    device = CommonDeviceSerializer()
    display = SerializerMethodField(read_only=True)

    class Meta:
        model = DeviceInterface
        fields = "__all__"

    def get_display(self, obj):
        return str(obj)


class LogicalInterfaceSerializer(ModelSerializer):
    parent_interface = NestedDeviceInterfaceSerializer()
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    ipv4_address = NestedIPAddressSerializer(required=False, allow_null=True)
    ipv6_address = NestedIPAddressSerializer(required=False, allow_null=True)
    untagged_vlan = NestedVLANSerializer(required=False, allow_null=True)
    tagged_vlans = NestedVLANSerializer(required=False, many=True)
    native_vlan = NestedVLANSerializer(required=False, allow_null=True)

    display = SerializerMethodField(read_only=True)

    class Meta:
        model = LogicalInterface
        fields = "__all__"

    def get_display(self, obj):
        return str(obj)

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks.
        This is needed as we only accept an ID on creation/update and obviously don't need to validate uniqueness.
        """
        return []


class DeviceInterfaceLiteSerializer(ModelSerializer):
    class Meta:
        model = DeviceInterface
        fields = ("id", "name")


class LinkSerializer(ModelSerializer):
    interface_a = NestedDeviceInterfaceSerializer()
    interface_b = NestedDeviceInterfaceSerializer()

    display = SerializerMethodField(read_only=True)

    class Meta:
        model = Link
        fields = (
            "id",
            "interface_a",
            "interface_b",
            "state",
            "monitoring_state",
            "display",
        )

    def get_display(self, obj):
        return str(obj)

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks.
        This is needed as we only accept an ID on creation/update and obviously don't need to validate uniqueness.
        """
        return []


class PortLayoutSerializer(ModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    network_role = NestedDeviceRoleSerializer()
    display = SerializerMethodField(read_only=True)

    class Meta:
        model = PortLayout
        fields = "__all__"

    def get_display(self, obj):
        return str(obj)
