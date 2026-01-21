"""TACACS serializers."""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.models.tacacs import Tacacs, TacacsServer


class TacacsServerSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    """

    class Meta:
        model = TacacsServer
        fields = "__all__"


class TacacsServerReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    class Meta:
        model = TacacsServer
        fields = "__all__"


class TacacsSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    """

    device = CommonDeviceSerializer(read_only=True)

    # Writable list of FK (PK list)
    server_list = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TacacsServer.objects.all(),
        required=False,
    )

    class Meta:
        model = Tacacs
        fields = "__all__"


class TacacsReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    device = CommonDeviceSerializer()
    server_list = TacacsServerReadSerializer(many=True)

    class Meta:
        model = Tacacs
        fields = "__all__"
