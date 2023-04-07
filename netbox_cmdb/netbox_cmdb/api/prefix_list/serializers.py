"""Prefix list serializers."""
from rest_framework.serializers import ModelSerializer, ValidationError

from netbox_cmdb.api.common_serializers import CommonDeviceSerializer
from netbox_cmdb.models.prefix_list import PrefixList, PrefixListTerm


class PrefixListTermSerializer(ModelSerializer):
    """Prefix List Term serializer."""

    class Meta:  # pylint: disable=missing-docstring
        model = PrefixListTerm
        fields = ["sequence", "prefix", "le", "ge"]


class PrefixListSerializer(ModelSerializer):
    """Prefix List serializer."""

    device = CommonDeviceSerializer()
    terms = PrefixListTermSerializer(many=True, source="prefix_list_term")

    class Meta:  # pylint: disable=missing-docstring
        model = PrefixList
        fields = ["id", "name", "device", "ip_version", "terms"]

    def _validate_terms(self, terms_data):
        if len(terms_data) < 1:
            raise ValidationError(
                {
                    "detail": "input is not valid, you must have at least one term in your prefix-list."
                }
            )

    def create(self, validated_data):
        terms_data = validated_data.pop("prefix_list_term")
        self._validate_terms(terms_data)
        # we create the prefix list first
        prefix_list = PrefixList.objects.create(**validated_data)

        # then we create terms, and associate it to the newly created prefix list
        for term_data in terms_data:
            PrefixListTerm.objects.create(prefix_list=prefix_list, **term_data)
        return prefix_list

    def update(self, instance, validated_data):
        terms_data = validated_data.pop("prefix_list_term")
        self._validate_terms(terms_data)

        # get current prefix list terms
        pf_terms = list(PrefixListTerm.objects.filter(prefix_list=instance))
        term_mapping = {term.sequence: term for term in pf_terms}
        data_mapping = {term["sequence"]: term for term in terms_data}

        instance.name = validated_data.get("name", instance.name)
        instance.device = validated_data.get("device", instance.device)
        instance.ip_version = validated_data.get("ip_version", instance.ip_version)
        instance.save()

        for term_data in terms_data:
            term, created = PrefixListTerm.objects.get_or_create(
                prefix_list=instance, sequence=term_data["sequence"], defaults=term_data
            )
            if not created:
                term.prefix = term_data.get("prefix", term.prefix)
                term.le = term_data.get("le", term.le)
                term.ge = term_data.get("ge", term.ge)
                term.save()

        # removing extra terms
        for term_sequence, term in term_mapping.items():
            if term_sequence not in data_mapping:
                term.delete()

        return instance
