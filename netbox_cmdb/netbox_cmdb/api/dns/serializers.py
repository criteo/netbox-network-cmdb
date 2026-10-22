"""DNS serializers."""

from dcim.models import Device
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.constants import MAX_DNS_SERVERS_PER_DEVICE
from netbox_cmdb.models.dns import DNS, DNSServer


class DNSServerSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    """

    class Meta:
        model = DNSServer
        fields = "__all__"


class DNSServerReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    class Meta:
        model = DNSServer
        fields = "__all__"


class DNSSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    One DNS configuration per device, with up to MAX_DNS_SERVERS_PER_DEVICE DNS servers.
    """

    device = CommonDeviceSerializer()

    # Writable list of FK (PK list)
    server_list = serializers.PrimaryKeyRelatedField(
        many=True, queryset=DNSServer.objects.all(), required=False
    )

    class Meta:
        model = DNS
        fields = "__all__"

    def validate_server_list(self, value):
        if len(value) > MAX_DNS_SERVERS_PER_DEVICE:
            raise serializers.ValidationError(
                f"You cannot select more than {MAX_DNS_SERVERS_PER_DEVICE} DNS Servers."
            )
        return value

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
        dns, _ = DNS.objects.get_or_create(device=device)

        if servers is not None:
            dns.server_list.set(servers)
        return dns

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

        # Unconditional, as NTP does: it refreshes last_updated even when only the
        # server list changed, keeping the change log honest.
        instance.save()

        if servers is not None:
            instance.server_list.set(servers)

        return instance


class DNSReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    device = CommonDeviceSerializer()
    server_list = DNSServerReadSerializer(many=True)

    class Meta:
        model = DNS
        fields = "__all__"
