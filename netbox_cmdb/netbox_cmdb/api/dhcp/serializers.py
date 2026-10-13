"""DHCP relay serializers."""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from netbox_cmdb.api.interface.serializers import NestedLogicalInterfaceSerializer
from netbox_cmdb.models.dhcp import (
    DhcpRelayInterface,
    DhcpServer,
    dhcp_relay_interface_errors,
)


class DhcpServerSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    """

    class Meta:
        model = DhcpServer
        fields = "__all__"


class DhcpServerReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    class Meta:
        model = DhcpServer
        fields = "__all__"


class DhcpRelayInterfaceSerializer(ModelSerializer):
    """
    Serializer used for write/create/update operations.
    One DHCP relay configuration per l3 logical interface, with multiple DHCP servers.
    """

    logical_interface = NestedLogicalInterfaceSerializer()

    # Writable list of FK (PK list)
    server_list = serializers.PrimaryKeyRelatedField(
        many=True, queryset=DhcpServer.objects.all(), required=False
    )

    class Meta:
        model = DhcpRelayInterface
        fields = "__all__"

    def validate(self, attrs):
        # A PATCH only carries the changed fields, the others come from the stored relay.
        logical_interface = attrs.get(
            "logical_interface", getattr(self.instance, "logical_interface", None)
        )
        errors = dhcp_relay_interface_errors(logical_interface)
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        # None and not [], as a POST acts as an upsert: an omitted server_list must leave the
        # servers of an existing configuration untouched, the way update() does.
        servers = validated_data.pop("server_list", None)
        logical_interface = validated_data.pop("logical_interface")

        # A POST on a logical interface that already holds a relay updates it, one per interface.
        relay, _ = DhcpRelayInterface.objects.get_or_create(logical_interface=logical_interface)

        if servers is not None:
            relay.server_list.set(servers)
        return relay

    def update(self, instance, validated_data):
        servers = validated_data.pop("server_list", None)
        logical_interface = validated_data.pop("logical_interface", None)

        if logical_interface:
            instance.logical_interface = logical_interface

        instance.save()

        if servers is not None:
            instance.server_list.set(servers)

        return instance


class DhcpRelayInterfaceReadSerializer(ModelSerializer):
    """
    Serializer used for read operations.
    """

    logical_interface = NestedLogicalInterfaceSerializer()
    server_list = DhcpServerReadSerializer(many=True)

    class Meta:
        model = DhcpRelayInterface
        fields = "__all__"
