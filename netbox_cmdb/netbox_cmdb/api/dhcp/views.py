"""DHCP relay views."""

from netbox_cmdb import filtersets
from netbox_cmdb.api.dhcp.serializers import (
    DhcpRelayInterfaceReadSerializer,
    DhcpRelayInterfaceSerializer,
    DhcpServerReadSerializer,
    DhcpServerSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.dhcp import DhcpRelayInterface, DhcpServer


class DhcpServerViewSet(CustomNetBoxModelViewSet):
    """
    CRUD for DHCP Server objects.
    """

    queryset = DhcpServer.objects.all()
    serializer_class = DhcpServerSerializer

    filterset_fields = ["server_address"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return DhcpServerReadSerializer
        return DhcpServerSerializer


class DhcpRelayInterfaceViewSet(CustomNetBoxModelViewSet):
    queryset = DhcpRelayInterface.objects.select_related(
        "logical_interface__parent_interface__device"
    ).prefetch_related("server_list")
    serializer_class = DhcpRelayInterfaceSerializer

    filterset_class = filtersets.DhcpRelayInterfaceFilterSet

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return DhcpRelayInterfaceReadSerializer
        return DhcpRelayInterfaceSerializer
