"""NTP serializers."""

from dcim.models import Device
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.models.ntp import NTP, NTPServer


class NTPServerSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    """

    class Meta:
        model = NTPServer
        fields = "__all__"


class NTPServerReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    class Meta:
        model = NTPServer
        fields = "__all__"


class NTPSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    One NTP configuration per device, with multiple NTP servers.
    """

    device = CommonDeviceSerializer()

    # Writable list of FK (PK list)
    server_list = serializers.PrimaryKeyRelatedField(
        many=True, queryset=NTPServer.objects.all(), required=False
    )

    class Meta:
        model = NTP
        fields = "__all__"

    def create(self, validated_data):
        # None and not [], as a POST acts as an upsert: an omitted server_list must leave the
        # servers of an existing configuration untouched, the way update() does.
        servers = validated_data.pop("server_list", None)
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

        # A POST on a device that already holds a configuration updates it, one per device.
        ntp, _ = NTP.objects.get_or_create(device=device)

        if servers is not None:
            ntp.server_list.set(servers)
        return ntp

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

        # Unconditional, as Tacacs does: it refreshes last_updated even when only the
        # server list changed, keeping the change log honest.
        instance.save()

        if servers is not None:
            instance.server_list.set(servers)

        return instance


class NTPReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    device = CommonDeviceSerializer()
    server_list = NTPServerReadSerializer(many=True)

    class Meta:
        model = NTP
        fields = "__all__"
