"""Route Policy serializers."""

from rest_framework.serializers import ModelSerializer, ValidationError

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.models.bgp_community_list import BGPCommunityList, BGPCommunityListTerm


class BGPCommunityListTermSerializer(ModelSerializer):
    class Meta:
        model = BGPCommunityListTerm
        fields = ["sequence", "community"]


class BGPCommunityListSerializer(ModelSerializer):
    device = CommonDeviceSerializer()
    terms = BGPCommunityListTermSerializer(many=True, source="bgp_community_list_term")

    class Meta:
        model = BGPCommunityList
        fields = "__all__"

    def _validate_terms(self, terms_data):
        if len(terms_data) < 1:
            raise ValidationError(
                {
                    "detail": "input is not valid, you must have at least one term in your bgp-community-list."
                }
            )

    def create(self, validated_data):
        terms_data = validated_data.pop("bgp_community_list_term")
        self._validate_terms(terms_data)

        # we create the bgp community list first
        bgp_community_list = BGPCommunityList.objects.create(**validated_data)

        # then we create terms, and associate it to the newly created bgp community list
        for term_data in terms_data:
            BGPCommunityListTerm.objects.create(bgp_community_list=bgp_community_list, **term_data)
        return bgp_community_list

    def update(self, instance, validated_data):
        terms_data = validated_data.pop("bgp_community_list_term")
        self._validate_terms(terms_data)

        # get current bgp community list terms
        bgp_com_list_terms = list(BGPCommunityListTerm.objects.filter(bgp_community_list=instance))
        term_mapping = {term.sequence: term for term in bgp_com_list_terms}
        data_mapping = {term["sequence"]: term for term in terms_data}

        instance.name = validated_data.get("name", instance.name)
        instance.device = validated_data.get("device", instance.device)
        instance.save()

        for term_data in terms_data:
            term, created = BGPCommunityListTerm.objects.get_or_create(
                bgp_community_list=instance,
                sequence=term_data["sequence"],
                defaults=term_data,
            )
            if not created:
                term.community = term_data.get("community", term.community)
                term.save()

        # removing extra terms
        for term_sequence, term in term_mapping.items():
            if term_sequence not in data_mapping:
                term.delete()

        return instance
