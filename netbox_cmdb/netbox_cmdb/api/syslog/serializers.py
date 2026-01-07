"""Syslog serializers."""

from dcim.models import Device
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
    One Syslog configuration per device, with multiple Syslog servers.
    """

    device = CommonDeviceSerializer()

    # Writable list of FK (PK list)
    server_list = serializers.PrimaryKeyRelatedField(
        many=True, queryset=SyslogServer.objects.all(), required=False
    )

    class Meta:
        model = Syslog
        fields = "__all__"

    def create(self, validated_data):
        servers = validated_data.pop("server_list", [])
        device_data = validated_data.pop("device")

        # If Device is already an object, use it
        if isinstance(device_data, Device):
            device = device_data
        # Elif it's a Dict with 'id' or 'name'
        elif isinstance(device_data, dict):
            if "id" in device_data:
                device = Device.objects.get(pk=device_data["id"])
            elif "name" in device_data:
                device = Device.objects.get(name=device_data["name"])
            else:
                raise serializers.ValidationError("Device must have 'id' or 'name'.")
        else:
            raise serializers.ValidationError("Invalid device data")

        syslog, created = Syslog.objects.get_or_create(device=device)
        syslog.server_list.set(servers)
        return syslog

    def update(self, instance, validated_data):
        servers = validated_data.pop("server_list", None)
        device_data = validated_data.pop("device", None)

        if device_data:
            if isinstance(device_data, Device):
                instance.device = device_data
            elif isinstance(device_data, dict):
                if "id" in device_data:
                    instance.device = Device.objects.get(pk=device_data["id"])
                elif "name" in device_data:
                    instance.device = Device.objects.get(name=device_data["name"])
                else:
                    raise serializers.ValidationError("Device must have 'id' or 'name'.")
            else:
                raise serializers.ValidationError("Invalid device data")
            instance.save()

        if servers is not None:
            instance.server_list.set(servers)

        return instance


class SyslogReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    device = CommonDeviceSerializer()
    server_list = SyslogServerReadSerializer(many=True)

    class Meta:
        model = Syslog
        fields = "__all__"
