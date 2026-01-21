"""TACACS serializers."""

from dcim.models import Device
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
    One TACACS configuration per device, with multiple TACACS servers.
    """

    device = CommonDeviceSerializer()

    # Writable list of FK (PK list)
    server_list = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TacacsServer.objects.all(),
        required=False,
    )

    class Meta:
        model = Tacacs
        fields = "__all__"

    def create(self, validated_data):
        servers = validated_data.pop("server_list", [])
        device_data = validated_data.pop("device")

        # If Device is already an object, use it
        if isinstance(device_data, Device):
            device = device_data
        # If it's a Dict with 'id' or 'name'
        elif isinstance(device_data, dict):
            if "id" in device_data:
                device = Device.objects.get(pk=device_data["id"])
            elif "name" in device_data:
                device = Device.objects.get(name=device_data["name"])
            else:
                raise serializers.ValidationError("Device must have 'id' or 'name'.")
        else:
            raise serializers.ValidationError("Invalid device data")

        tacacs, created = Tacacs.objects.get_or_create(
            device=device,
            defaults={
                "passkey": validated_data.get("passkey"),
            },
        )

        # Update passkey if provided
        if "passkey" in validated_data:
            tacacs.passkey = validated_data["passkey"]
            tacacs.save()

        tacacs.server_list.set(servers)
        return tacacs

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

        # Update passkey if provided
        if "passkey" in validated_data:
            instance.passkey = validated_data["passkey"]

        instance.save()

        if servers is not None:
            instance.server_list.set(servers)

        return instance


class TacacsReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    device = CommonDeviceSerializer()
    server_list = TacacsServerReadSerializer(many=True)

    class Meta:
        model = Tacacs
        fields = "__all__"
