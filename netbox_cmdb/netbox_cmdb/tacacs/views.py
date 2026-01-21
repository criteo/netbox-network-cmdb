"""TACACS views."""

from netbox_cmdb import filtersets
from netbox_cmdb.api.tacacs.serializers import (
    TacacsReadSerializer,
    TacacsSerializer,
    TacacsServerReadSerializer,
    TacacsServerSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.models.tacacs import Tacacs, TacacsServer


class TacacsServerViewSet(CustomNetBoxModelViewSet):
    """
    CRUD for TACACS Server objects.
    """

    queryset = TacacsServer.objects.all()
    serializer_class = TacacsServerSerializer

    filterset_fields = [
        "server_address",
        "priority",
        "tcp_port",
    ]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TacacsServerReadSerializer
        return TacacsServerSerializer


class TacacsViewSet(CustomNetBoxModelViewSet):
    queryset = Tacacs.objects.all()
    serializer_class = TacacsSerializer

    filterset_fields = [
        "server_list",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TacacsReadSerializer
        return TacacsSerializer

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
