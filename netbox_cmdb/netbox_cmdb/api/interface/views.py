from netbox_cmdb.api.interface.serializers import (
    DeviceInterfaceSerializer,
    LinkSerializer,
    LogicalInterfaceSerializer,
    PortLayoutSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.interface import (
    DeviceInterface,
    Link,
    LogicalInterface,
    PortLayout,
)


class DeviceInterfaceViewSet(CustomNetBoxModelViewSet):
    queryset = DeviceInterface.objects.all()
    serializer_class = DeviceInterfaceSerializer
    filterset_fields = [
        "id",
        "name",
        "device__id",
        "device__name",
        "enabled",
        "state",
        "monitoring_state",
        "autonegotiation",
        "speed",
        "fec",
    ]


class LogicalInterfaceViewSet(CustomNetBoxModelViewSet):
    queryset = LogicalInterface.objects.all()
    serializer_class = LogicalInterfaceSerializer
    filterset_fields = [
        "id",
        "index",
        "parent_interface__id",
        "parent_interface__name",
        "parent_interface__device__name",
        "enabled",
        "state",
        "monitoring_state",
        "mtu",
        "type",
        "vrf__id",
        "vrf__name",
        "ipv4_address__id",
        "ipv6_address__id",
        "mode",
        "untagged_vlan__id",
        "native_vlan__id",
    ]


class LinkViewSet(CustomNetBoxModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    filterset_fields = [
        "id",
        "interface_a__id",
        "interface_a__name",
        "interface_a__device__name",
        "interface_b__id",
        "interface_b__name",
        "interface_b__device__name",
        "state",
        "monitoring_state",
    ]


class PortLayoutViewSet(CustomNetBoxModelViewSet):
    queryset = PortLayout.objects.all()
    serializer_class = PortLayoutSerializer
    filterset_fields = [
        "id",
        "device_type__id",
        "device_type__model",
        "network_role__id",
        "network_role__name",
        "name",
        "label_name",
        "logical_name",
        "vendor_name",
        "vendor_short_name",
        "vendor_long_name",
    ]
