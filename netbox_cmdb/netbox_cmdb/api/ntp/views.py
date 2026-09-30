"""NTP views."""

from netbox_cmdb import filtersets
from netbox_cmdb.api.ntp.serializers import (
    NTPReadSerializer,
    NTPSerializer,
    NTPServerReadSerializer,
    NTPServerSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.ntp import NTP, NTPServer


class NTPServerViewSet(CustomNetBoxModelViewSet):
    """
    CRUD for NTP Server objects.
    """

    queryset = NTPServer.objects.all()
    serializer_class = NTPServerSerializer

    filterset_fields = ["name", "server_address"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return NTPServerReadSerializer
        return NTPServerSerializer


class NTPViewSet(CustomNetBoxModelViewSet):
    queryset = NTP.objects.all()
    serializer_class = NTPSerializer

    filterset_fields = [
        "server_list",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return NTPReadSerializer
        return NTPSerializer

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
