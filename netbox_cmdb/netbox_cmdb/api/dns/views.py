"""DNS views."""

from netbox_cmdb import filtersets
from netbox_cmdb.api.dns.serializers import (
    DNSReadSerializer,
    DNSSerializer,
    DNSServerReadSerializer,
    DNSServerSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.dns import DNS, DNSServer


class DNSServerViewSet(CustomNetBoxModelViewSet):
    """
    CRUD for DNS Server objects.
    """

    queryset = DNSServer.objects.all()
    serializer_class = DNSServerSerializer

    filterset_fields = ["name", "server_address"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return DNSServerReadSerializer
        return DNSServerSerializer


class DNSViewSet(CustomNetBoxModelViewSet):
    queryset = DNS.objects.all()
    serializer_class = DNSSerializer

    filterset_fields = [
        "server_list",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return DNSReadSerializer
        return DNSSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        server_list = serializer.validated_data.get("server_list")
        if server_list is not None:
            obj.server_list.set(server_list)

    def perform_update(self, serializer):
        obj = serializer.save()
        server_list = serializer.validated_data.get("server_list")
        if server_list is not None:
            obj.server_list.set(server_list)
