"""Route Policy serializers."""
from netbox.api.serializers import WritableNestedSerializer
from rest_framework.serializers import ModelSerializer, ValidationError

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.models.bgp_community_list import BGPCommunityList
from netbox_cmdb.models.prefix_list import PrefixList
from netbox_cmdb.models.route_policy import RoutePolicy, RoutePolicyTerm


class NestedBgpCommunityListSerializer(WritableNestedSerializer):
    class Meta:
        model = BGPCommunityList
        fields = ["id", "device", "name"]

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks.
        This is needed as we only accept an ID on creation/update and obviously don't need to validate uniqueness.
        """
        return []


class NestedPrefixListSerializer(WritableNestedSerializer):
    class Meta:
        model = PrefixList
        fields = ["id", "device", "name"]

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks.
        This is needed as we only accept an ID on creation/update and obviously don't need to validate uniqueness.
        """
        return []


class RoutePolicyTermSerializer(ModelSerializer):
    from_bgp_community_list = NestedBgpCommunityListSerializer(
        required=False, many=False, allow_null=True
    )
    from_prefix_list = NestedPrefixListSerializer(required=False, many=False, allow_null=True)

    class Meta:
        model = RoutePolicyTerm
        fields = [
            "description",
            "sequence",
            "decision",
            "from_bgp_community",
            "from_bgp_community_list",
            "from_prefix_list",
            "from_source_protocol",
            "from_route_type",
            "from_local_pref",
            "set_local_pref",
            "set_community",
            "set_origin",
            "set_metric",
            "set_large_community",
            "set_as_path_prepend",
            "set_next_hop",
        ]


class WritableRoutePolicySerializer(ModelSerializer):
    device = CommonDeviceSerializer()

    terms = RoutePolicyTermSerializer(many=True, source="route_policy_term")

    class Meta:
        model = RoutePolicy
        fields = ["id", "name", "device", "description", "terms"]

    def _validate_terms(self, terms_data):
        if len(terms_data) < 1:
            raise ValidationError(
                {
                    "detail": "input is not valid, you must have at least one term in your route policy."
                }
            )

    def create(self, validated_data):
        terms_data = validated_data.pop("route_policy_term")
        self._validate_terms(terms_data)
        # we create the route policy first
        route_policy = RoutePolicy.objects.create(**validated_data)

        # then we create terms, and associate it to the newly created route policy
        for term_data in terms_data:
            RoutePolicyTerm.objects.create(route_policy=route_policy, **term_data)
        return route_policy

    def update(self, instance, validated_data):
        terms_data = validated_data.pop("route_policy_term")
        self._validate_terms(terms_data)

        # get current route policy terms
        rp_terms = list(RoutePolicyTerm.objects.filter(route_policy=instance))
        term_mapping = {term.sequence: term for term in rp_terms}
        data_mapping = {term["sequence"]: term for term in terms_data}

        instance.name = validated_data.get("name", instance.name)
        instance.device = validated_data.get("device", instance.device)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        for term_data in terms_data:
            term, created = RoutePolicyTerm.objects.get_or_create(
                route_policy=instance,
                sequence=term_data["sequence"],
                defaults=term_data,
            )
            if not created:
                term.decision = term_data.get("decision", term.decision)
                term.description = term_data.get("description", term.description)
                term.from_bgp_community = term_data.get(
                    "from_bgp_community", term.from_bgp_community
                )
                term.from_bgp_community_list = term_data.get(
                    "from_bgp_community_list", term.from_bgp_community_list
                )
                term.from_prefix_list = term_data.get("from_prefix_list", term.from_prefix_list)
                term.from_source_protocol = term_data.get(
                    "from_source_protocol", term.from_source_protocol
                )
                term.from_route_type = term_data.get("from_route_type", term.from_route_type)
                term.from_local_pref = term_data.get("from_local_pref", term.from_local_pref)
                term.set_local_pref = term_data.get("set_local_pref", term.set_local_pref)
                term.set_community = term_data.get("set_community", term.set_community)
                term.set_origin = term_data.get("set_origin", term.set_origin)
                term.set_metric = term_data.get("set_metric", term.set_metric)
                term.set_large_community = term_data.get(
                    "set_large_community", term.set_large_community
                )
                term.set_as_path_prepend = term_data.get(
                    "set_as_path_prepend", term.set_as_path_prepend
                )
                term.set_next_hop = term_data.get("set_next_hop", term.set_next_hop)
                term.save()

        # removing extra terms
        for term_sequence, term in term_mapping.items():
            if term_sequence not in data_mapping:
                term.delete()

        return instance
