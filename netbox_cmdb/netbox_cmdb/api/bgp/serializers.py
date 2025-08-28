from django.core.exceptions import ValidationError
from django.db.models import Q
from ipam.api.nested_serializers import NestedIPAddressSerializer
from netbox.api.serializers import WritableNestedSerializer
from rest_framework import serializers
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    SerializerMethodField,
)
from tenancy.api.nested_serializers import NestedTenantSerializer

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.choices import AssetMonitoringStateChoices
from netbox_cmdb.constants import BGP_MAX_ASN, BGP_MIN_ASN
from netbox_cmdb.models.bgp import (
    ASN,
    AfiSafi,
    Aggregate,
    BGPGlobal,
    BGPPeerGroup,
    BGPSession,
    BGPSessionCommon,
    DeviceBGPSession,
    GlobalAfiSafi,
    RedistributedNetwork,
)
from netbox_cmdb.models.circuit import Circuit
from netbox_cmdb.models.route_policy import RoutePolicy


class AsnSerializer(WritableNestedSerializer):
    class Meta:
        model = ASN
        fields = ["id", "number", "organization_name"]


class AvailableAsnSerializer(ModelSerializer):
    min_asn = IntegerField(max_value=BGP_MAX_ASN, min_value=BGP_MIN_ASN)
    max_asn = IntegerField(max_value=BGP_MAX_ASN, min_value=BGP_MIN_ASN)

    class Meta:
        model = ASN
        fields = ["organization_name", "min_asn", "max_asn"]


class NestedAggregateSerializer(ModelSerializer):
    class Meta:
        model = Aggregate
        fields = ["id", "prefix"]


class NestedRedistributedNetworkSerializer(ModelSerializer):
    class Meta:
        model = RedistributedNetwork
        fields = ["id", "prefix"]


class NestedGlobalAfiSafiSerializer(ModelSerializer):
    aggregates = NestedAggregateSerializer(required=False, many=True, allow_null=True)
    redistributed_networks = NestedRedistributedNetworkSerializer(
        required=False, many=True, allow_null=True
    )

    class Meta:
        model = GlobalAfiSafi
        fields = ["id", "afi_safi_name", "aggregates", "redistributed_networks"]


class BGPGlobalSerializer(ModelSerializer):
    device = CommonDeviceSerializer()
    local_asn = AsnSerializer(
        required=True,
    )
    afi_safis = NestedGlobalAfiSafiSerializer(required=False, many=True, allow_null=True)

    class Meta:
        model = BGPGlobal
        fields = "__all__"

    def create(self, validated_data):
        afi_safis_data = validated_data.pop("afi_safis", [])

        bgp_global = BGPGlobal.objects.create(**validated_data)

        for afi_safi_data in afi_safis_data:
            aggregates_data = afi_safi_data.pop("aggregates", [])
            redistributed_networks_data = afi_safi_data.pop("redistributed_networks", [])

            global_afi_safi = GlobalAfiSafi.objects.create(bgp_global=bgp_global, **afi_safi_data)

            for aggregate_data in aggregates_data:
                Aggregate.objects.create(global_afi_safi=global_afi_safi, **aggregate_data)

            for redistributed_network_data in redistributed_networks_data:
                RedistributedNetwork.objects.create(
                    global_afi_safi=global_afi_safi, **redistributed_network_data
                )

        return bgp_global

    def update(self, instance, validated_data):
        afi_safis_data = validated_data.pop("afi_safis", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if afi_safis_data is not None:
            existing_afi_safis = {
                afi_safi.afi_safi_name: afi_safi for afi_safi in instance.afi_safis.all()
            }

            updated_afi_safi_names = set()

            for afi_safi_data in afi_safis_data:
                afi_safi_name = afi_safi_data["afi_safi_name"]
                updated_afi_safi_names.add(afi_safi_name)

                aggregates_data = afi_safi_data.pop("aggregates", [])
                redistributed_networks_data = afi_safi_data.pop("redistributed_networks", [])

                if afi_safi_name in existing_afi_safis:
                    global_afi_safi = existing_afi_safis[afi_safi_name]
                else:
                    global_afi_safi = GlobalAfiSafi.objects.create(
                        bgp_global=instance, **afi_safi_data
                    )

                # Update aggregates - replace all existing ones
                global_afi_safi.aggregates.all().delete()
                for aggregate_data in aggregates_data:
                    Aggregate.objects.create(global_afi_safi=global_afi_safi, **aggregate_data)

                # Update redistributed networks - replace all existing ones
                global_afi_safi.redistributed_networks.all().delete()
                for redistributed_network_data in redistributed_networks_data:
                    RedistributedNetwork.objects.create(
                        global_afi_safi=global_afi_safi, **redistributed_network_data
                    )

            # Delete AFI/SAFIs that are no longer present
            for afi_safi_name, afi_safi in existing_afi_safis.items():
                if afi_safi_name not in updated_afi_safi_names:
                    afi_safi.delete()

        return instance


class BGPSessionCommonSerializer(ModelSerializer):
    class Meta:
        model = BGPSessionCommon


class RoutePolicySerializer(WritableNestedSerializer):
    class Meta:
        model = RoutePolicy
        fields = ["id", "name", "description"]


class NestedAfiSafiSerializer(ModelSerializer):
    route_policy_in = RoutePolicySerializer(required=False, many=False, allow_null=True)
    route_policy_out = RoutePolicySerializer(required=False, many=False, allow_null=True)

    class Meta:
        model = AfiSafi
        fields = ["id", "route_policy_in", "route_policy_out", "afi_safi_name"]


class BGPPeerGroupSerializer(BGPSessionCommonSerializer):
    local_asn = AsnSerializer(required=False, allow_null=True)
    remote_asn = AsnSerializer(
        required=False,
    )
    device = CommonDeviceSerializer()
    route_policy_in = RoutePolicySerializer(
        required=False,
        many=False,
        allow_null=True,
    )
    route_policy_out = RoutePolicySerializer(
        required=False,
        many=False,
        allow_null=True,
    )

    class Meta:
        model = BGPPeerGroup
        fields = "__all__"

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks.
        This is needed as we only accept an ID on creation/update and obviously don't need to validate uniqueness.
        """
        return []


class LiteBGPPeerGroupSerializer(BGPPeerGroupSerializer, WritableNestedSerializer):
    class Meta:
        model = BGPPeerGroup
        fields = ["id", "name", "device"]


class BGPASNSerializer(ModelSerializer):
    def validate(self, attrs):
        if ASN.objects.filter(
            number=attrs["number"], organization_name=attrs.get("organization_name")
        ).exists():
            raise serializers.ValidationError(
                {"error": "ASN with this Number and Organization Name already exists."}
            )
        return attrs

    class Meta:
        model = ASN
        fields = "__all__"


class DeviceBGPSessionSerializer(ModelSerializer):
    local_address = NestedIPAddressSerializer(many=False)
    device = CommonDeviceSerializer()
    peer_group = LiteBGPPeerGroupSerializer(required=False, many=False, allow_null=True)
    local_asn = AsnSerializer(many=False, allow_null=True)
    afi_safis = NestedAfiSafiSerializer(required=False, many=True, allow_null=True)
    route_policy_in = RoutePolicySerializer(required=False, many=False, allow_null=True)
    route_policy_out = RoutePolicySerializer(required=False, many=False, allow_null=True)

    display = SerializerMethodField(read_only=True)

    class Meta:
        model = DeviceBGPSession
        fields = "__all__"

    def get_display(self, obj):
        return str(obj)


class CircuitSerializer(ModelSerializer):
    class Meta:
        model = Circuit
        fields = "__all__"


class BGPSessionSerializer(ModelSerializer):
    peer_a = DeviceBGPSessionSerializer(many=False)
    peer_b = DeviceBGPSessionSerializer(many=False)
    tenant = NestedTenantSerializer(required=False, many=False)
    display = SerializerMethodField(read_only=True)

    def get_display(self, obj):
        return str(obj)

    def create(self, validated_data):
        peers_data = {}
        for peer in ["a", "b"]:
            peers_data[f"peer_{peer}"] = validated_data.pop(f"peer_{peer}")

        afi_safis = {}
        device_bgp_session = {}
        for peer, peer_data in peers_data.items():
            afi_safis[peer] = peer_data.pop("afi_safis")
            device_bgp_session[peer] = DeviceBGPSession.objects.create(**peer_data)
            for afi_safi in afi_safis[peer]:
                AfiSafi.objects.create(device_bgp_session=device_bgp_session[peer], **afi_safi)

        bgp_session = BGPSession.objects.create(
            peer_a=device_bgp_session["peer_a"],
            peer_b=device_bgp_session["peer_b"],
            state=validated_data.get("state"),
            monitoring_state=validated_data.get(
                "monitoring_state", AssetMonitoringStateChoices.DISABLED
            ),
            password=validated_data.get("password"),
            circuit=validated_data.get("circuit"),
            tenant=validated_data.get("tenant"),
        )

        return bgp_session

    def update(self, instance, validated_data):
        peers_data = {}
        afi_safis_data = {}
        for peer in ["a", "b"]:
            peers_data[f"peer_{peer}"] = validated_data.pop(f"peer_{peer}")

        instance.state = validated_data.get("state", instance.state)
        instance.monitoring_state = validated_data.get(
            "monitoring_state", instance.monitoring_state
        )
        instance.password = validated_data.get("password", instance.password)
        instance.circuit = validated_data.get("circuit", instance.circuit)
        instance.tenant = validated_data.get("tenant", instance.tenant)
        instance.save()
        # get peers
        bgp_peers = {}
        bgp_peers["peer_a"] = DeviceBGPSession.objects.get(peer_a=instance)
        bgp_peers["peer_b"] = DeviceBGPSession.objects.get(peer_b=instance)
        for peer, peer_instance in bgp_peers.items():
            # pop afi safi data for later creation/update
            afi_safis_data[peer] = peers_data[peer].pop("afi_safis", None)

            # update peer instance with provided data
            peer_instance.device = peers_data[peer].get("device", peer_instance.device)
            peer_instance.enabled = peers_data[peer].get("enabled", peer_instance.enabled)
            peer_instance.local_address = peers_data[peer].get(
                "local_address", peer_instance.local_address
            )
            peer_instance.peer_group = peers_data[peer].get("peer_group", peer_instance.peer_group)
            peer_instance.local_asn = peers_data[peer].get("local_asn", peer_instance.local_asn)
            peer_instance.description = peers_data[peer].get(
                "description", peer_instance.description
            )
            peer_instance.maximum_prefixes = peers_data[peer].get(
                "maximum_prefixes", peer_instance.maximum_prefixes
            )
            peer_instance.enforce_first_as = peers_data[peer].get(
                "enforce_first_as", peer_instance.enforce_first_as
            )
            peer_instance.route_policy_in = peers_data[peer].get(
                "route_policy_in", peer_instance.route_policy_in
            )
            peer_instance.route_policy_out = peers_data[peer].get(
                "route_policy_out", peer_instance.route_policy_out
            )
            peer_instance.save()

            # handle safi
            if afi_safis_data[peer] is None:
                # useful for PATCH requests: if the field is empty, we don't change anything
                continue

            # get current list of afi safi
            current_afi_safis = list(AfiSafi.objects.filter(device_bgp_session=peer_instance))
            current_afi_safi_mapping = {
                afi_safi.afi_safi_name: afi_safi for afi_safi in current_afi_safis
            }
            target_afi_safi_mapping = {
                afi_safi["afi_safi_name"]: afi_safi for afi_safi in afi_safis_data[peer]
            }
            for afi_safi_data in afi_safis_data[peer]:
                afi_safi, created = AfiSafi.objects.get_or_create(
                    device_bgp_session=peer_instance,
                    afi_safi_name=afi_safi_data["afi_safi_name"],
                    defaults=afi_safi_data,
                )
                if not created:
                    # if object is already existing, we only modify the remaining attributes and save the object
                    afi_safi.route_policy_in = afi_safi_data.get(
                        "route_policy_in", afi_safi.route_policy_in
                    )
                    afi_safi.route_policy_out = afi_safi_data.get(
                        "route_policy_out", afi_safi.route_policy_out
                    )
                    afi_safi.save()

            # removing extra afi safi
            for name, afi_safi in current_afi_safi_mapping.items():
                # if existing afi safi is not present in provided data, we remove it
                if name not in target_afi_safi_mapping:
                    afi_safi.delete()

        return instance

    def validate(self, attrs):
        # Check for a duplicate BGP session (same devices / ips).
        errors = []
        if BGPSession.objects.exclude(pk=getattr(self.instance, "id", None)).filter(
            Q(
                peer_a__device=attrs["peer_a"]["device"],
                peer_a__local_address=attrs["peer_a"]["local_address"],
                peer_b__device=attrs["peer_b"]["device"],
                peer_b__local_address=attrs["peer_b"]["local_address"],
            )
            | Q(
                peer_a__device__name=attrs["peer_b"]["device"],
                peer_a__local_address=attrs["peer_b"]["local_address"],
                peer_b__device__name=attrs["peer_a"]["device"],
                peer_b__local_address=attrs["peer_a"]["local_address"],
            )
        ):
            error = serializers.ValidationError(
                "A BGP session already exists between these 2 devices and IP addresses."
            )
            errors.append(error)

        # Check if all dependencies are on the same device
        for peer in ["peer_a", "peer_b"]:
            try:
                DeviceBGPSession.validate_device_consistency(
                    attrs[peer]["device"],
                    attrs[peer].get("peer_group"),
                    attrs[peer].get("route_policy_in"),
                    attrs[peer].get("route_policy_out"),
                )
            except ValidationError as error:
                errors.append(error)

            for safi in attrs[peer].get("afi_safis", []):
                try:
                    AfiSafi.validate_device_consistency(
                        attrs[peer]["device"],
                        safi.get("route_policy_in"),
                        safi.get("route_policy_out"),
                    )
                except ValidationError as error:
                    errors.append(error)

        if errors:
            raise serializers.ValidationError({"errors": ValidationError(errors).messages})

        return super().validate(attrs)

    class Meta:
        model = BGPSession
        fields = "__all__"
