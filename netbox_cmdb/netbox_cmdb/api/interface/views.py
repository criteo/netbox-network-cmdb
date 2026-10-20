from netbox_cmdb import filtersets
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
    ] + filtersets.device_location_filterset


class LogicalInterfaceViewSet(CustomNetBoxModelViewSet):
    queryset = LogicalInterface.objects.all()
    serializer_class = LogicalInterfaceSerializer
    filterset_class = filtersets.LogicalInterfaceFilterSet


class LinkViewSet(CustomNetBoxModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    filterset_class = filtersets.LinkFilterSet


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
