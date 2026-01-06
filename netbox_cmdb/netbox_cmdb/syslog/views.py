"""Syslog views."""

from netbox_cmdb import filtersets
from netbox_cmdb.api.syslog.serializers import (
    SyslogServerSerializer,
    SyslogServerReadSerializer,
    SyslogReadSerializer,
    SyslogSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.syslog import Syslog, SyslogServer


class SyslogServerViewSet(CustomNetBoxModelViewSet):
    """
    CRUD for Syslog Server objects.
    """

    queryset = SyslogServer.objects.all()
    serializer_class = SyslogServerSerializer

    filterset_fields = ["server_address"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SyslogServerReadSerializer
        return SyslogServerSerializer


class SyslogViewSet(CustomNetBoxModelViewSet):
    queryset = Syslog.objects.all()
    serializer_class = SyslogSerializer

    filterset_fields = [
        "server_list",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SyslogReadSerializer
        return SyslogSerializer

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


