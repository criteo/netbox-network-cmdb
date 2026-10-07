from dcim.api.nested_serializers import (
    NestedDeviceRoleSerializer,
    NestedDeviceTypeSerializer,
)
from ipam.api.nested_serializers import NestedIPAddressSerializer
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import WritableNestedSerializer
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.api.vlan.serializers import NestedVLANSerializer
from netbox_cmdb.api.vrf.serializers import NestedVRFSerializer
from netbox_cmdb.models.interface import (
    DeviceInterface,
    Link,
    LogicalInterface,
    PortLayout,
    port_layout_lane_errors,
)
from netbox_cmdb.models.vlan import VLAN


class NestedDeviceInterfaceSerializer(WritableNestedSerializer):
    device = CommonDeviceSerializer(read_only=True)

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


class NestedLogicalInterfaceSerializer(WritableNestedSerializer):
    """A logical interface as referenced by other objects (e.g. management routes).

    On write, a PK or a dictionary of attributes identifying the logical interface
    (e.g. parent_interface__device__name + parent_interface__name + index).
    """

    parent_interface = NestedDeviceInterfaceSerializer(read_only=True)
    name = CharField(read_only=True)

    class Meta:
        model = LogicalInterface
        fields = ["id", "index", "name", "parent_interface"]


class LogicalInterfaceSerializer(ModelSerializer):
    parent_interface = NestedDeviceInterfaceSerializer()
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    ipv4_address = NestedIPAddressSerializer(required=False, allow_null=True)
    ipv6_address = NestedIPAddressSerializer(required=False, allow_null=True)
    untagged_vlan = NestedVLANSerializer(required=False, allow_null=True)
    # M2M: a writable nested serializer is not supported by DRF's default
    # create/update, use a PK-based field like NetBox core does for
    # dcim.Interface.tagged_vlans.
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVLANSerializer,
        required=False,
        many=True,
    )
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

    def validate(self, attrs):
        # A PATCH only carries the changed fields, the others come from the stored port.
        def current(field):
            if field in attrs:
                return attrs[field]
            return getattr(self.instance, field, None)

        errors = port_layout_lane_errors(
            current("device_type"),
            current("network_role"),
            current("name"),
            current("lanes"),
            exclude_pk=getattr(self.instance, "pk", None),
        )
        if errors:
            raise ValidationError({"lanes": errors})
        return attrs
