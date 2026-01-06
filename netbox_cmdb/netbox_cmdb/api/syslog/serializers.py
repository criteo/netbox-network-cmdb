"""Syslog serializers."""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.models.syslog import Syslog, SyslogServer


class SyslogServerSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    """
    class Meta:
        model = SyslogServer
        fields = "__all__"


class SyslogServerReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """
    class Meta:
        model = SyslogServer
        fields = "__all__"


class SyslogSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    """

    device = CommonDeviceSerializer(read_only=True)

    # Writable list of FK (PK list)
    server_list = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SyslogServer.objects.all(),
        required=False
    )

    class Meta:
        model = Syslog
        fields = "__all__"


class SyslogReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    device = CommonDeviceSerializer()
    server_list = SyslogServerReadSerializer(many=True)

    class Meta:
        model = Syslog
        fields = "__all__"

