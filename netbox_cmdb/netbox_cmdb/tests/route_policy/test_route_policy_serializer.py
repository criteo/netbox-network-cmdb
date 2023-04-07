from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.test import TestCase
from netaddr import IPNetwork
from rest_framework.exceptions import ErrorDetail
from rest_framework.serializers import ValidationError

from netbox_cmdb.api.route_policy.serializers import WritableRoutePolicySerializer
from netbox_cmdb.models.bgp_community_list import BGPCommunityList, BGPCommunityListTerm
from netbox_cmdb.models.prefix_list import PrefixList, PrefixListTerm
from netbox_cmdb.models.route_policy import RoutePolicy, RoutePolicyTerm


def validate(device, data):
    """Helper to validate that content is conform."""

    terms_data = data.pop("terms")

    rp_expected = RoutePolicy(name="RM-TEST", device=device)
    rp_got = RoutePolicy.objects.get(name="RM-TEST")

    assert rp_got.name == rp_expected.name
    assert rp_got.device == rp_expected.device

    rp_terms_got = list(RoutePolicyTerm.objects.filter(route_policy=rp_got).order_by("sequence"))
    assert len(rp_terms_got) == len(terms_data)

    rp_terms_expected = []
    for term_data in terms_data:
        # get the real object from the pk
        if term_data.get("from_bgp_community_list"):
            term_data["from_bgp_community_list"] = BGPCommunityList.objects.get(
                pk=term_data["from_bgp_community_list"]
            )
        if term_data.get("from_prefix_list"):
            term_data["from_prefix_list"] = PrefixList.objects.get(pk=term_data["from_prefix_list"])

        rp_terms_expected.append(RoutePolicyTerm(route_policy=rp_got, **term_data))

    for rp_term_got, rp_term_expected in zip(rp_terms_got, rp_terms_expected):
        assert rp_term_got.sequence == rp_term_expected.sequence
        assert rp_term_got.decision == rp_term_expected.decision
        assert rp_term_got.from_bgp_community == rp_term_expected.from_bgp_community
        assert rp_term_got.from_bgp_community_list == rp_term_expected.from_bgp_community_list
        assert rp_term_got.from_prefix_list == rp_term_expected.from_prefix_list
        assert rp_term_got.from_source_protocol == rp_term_expected.from_source_protocol
        assert rp_term_got.from_route_type == rp_term_expected.from_route_type
        assert rp_term_got.from_local_pref == rp_term_expected.from_local_pref
        assert rp_term_got.set_local_pref == rp_term_expected.set_local_pref
        assert rp_term_got.set_community == rp_term_expected.set_community
        assert rp_term_got.set_origin == rp_term_expected.set_origin
        assert rp_term_got.set_metric == rp_term_expected.set_metric
        assert rp_term_got.set_large_community == rp_term_expected.set_large_community
        assert rp_term_got.set_as_path_prepend == rp_term_expected.set_as_path_prepend
        assert str(rp_term_got.set_next_hop) == str(rp_term_expected.set_next_hop)


class BaseTestCase(TestCase):
    def setUp(self):
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="model-test", slug="model-test"
        )
        device_role = DeviceRole.objects.create(name="role-test", slug="role-test")
        self.device = Device.objects.create(
            name="router-test",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )
        self.prefix_list = PrefixList.objects.create(
            name="PF-TEST", device=self.device, ip_version="ipv4"
        )
        self.prefix_list_term = PrefixListTerm.objects.create(
            prefix_list=self.prefix_list,
            sequence=5,
            prefix=IPNetwork("10.0.0.0/8"),
        )
        self.bgp_community_list = BGPCommunityList.objects.create(
            name="CL-TEST", device=self.device
        )
        self.bgp_community_list_term = BGPCommunityListTerm.objects.create(
            bgp_community_list=self.bgp_community_list,
            sequence=5,
            community="64666:123",
        )

        self.device2 = Device.objects.create(
            name="router-test-bis",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )
        self.prefix_list2 = PrefixList.objects.create(
            name="PF-TEST", device=self.device2, ip_version="ipv4"
        )
        self.prefix_list_term2 = PrefixListTerm.objects.create(
            prefix_list=self.prefix_list2,
            sequence=5,
            prefix=IPNetwork("10.0.0.0/8"),
        )
        self.bgp_community_list2 = BGPCommunityList.objects.create(
            name="CL-TEST", device=self.device2
        )
        self.bgp_community_list_term2 = BGPCommunityListTerm.objects.create(
            bgp_community_list=self.bgp_community_list2,
            sequence=5,
            community="64666:123",
        )


class WritableRoutePolicySerializerCreate(BaseTestCase):
    def test_route_policy_creation(self):
        bgp_com_list = BGPCommunityList.objects.get(device=self.device, name="CL-TEST")
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "decision": "permit",
                    "from_bgp_community_list": bgp_com_list.pk,
                    "set_local_pref": 100,
                }
            ],
        }

        route_policy_serializer = WritableRoutePolicySerializer(data=data)
        assert route_policy_serializer.is_valid() == True

    def test_route_policy_creation_with_empty_terms(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "terms": [],
        }

        route_policy_serializer = WritableRoutePolicySerializer(data=data)
        assert route_policy_serializer.is_valid() == True

        with self.assertRaisesRegex(
            ValidationError,
            "input is not valid, you must have at least one term in your route policy.",
        ):
            route_policy_serializer.save()

    def test_route_policycreation_without_terms(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
        }

        route_policy_serializer = WritableRoutePolicySerializer(data=data)
        assert route_policy_serializer.is_valid() == False


class WritableRoutePolicySerializerUpdate(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.route_policy = RoutePolicy.objects.create(name="RM-TEST", device=self.device)
        data_terms = [
            {
                "sequence": 5,
                "decision": "permit",
                "from_bgp_community_list": self.bgp_community_list,
                "set_local_pref": 100,
            },
            {
                "sequence": 10,
                "decision": "permit",
                "from_prefix_list": self.prefix_list,
                "set_local_pref": 200,
            },
        ]

        self.route_policy_terms = RoutePolicyTerm.objects.bulk_create(
            [
                RoutePolicyTerm(route_policy=self.route_policy, **data_term)
                for data_term in data_terms
            ]
        )

    def test_route_policy_update_add_term(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "decision": "permit",
                    "from_bgp_community_list": self.bgp_community_list.pk,
                    "set_local_pref": 100,
                },
                {
                    "sequence": 10,
                    "decision": "permit",
                    "from_prefix_list": self.prefix_list.pk,
                    "set_local_pref": 200,
                },
                {
                    "sequence": 15,
                    "decision": "permit",
                    "set_next_hop": "10.0.0.1",
                },
            ],
        }
        route_policy_serializer = WritableRoutePolicySerializer(
            instance=self.route_policy, data=data
        )
        assert route_policy_serializer.is_valid() == True
        route_policy_serializer.save()
        validate(self.device, data)

    def test_route_policy_update_add_invalid_term(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "decision": "permit",
                    "from_bgp_community_list": self.bgp_community_list.pk,
                    "set_local_pref": 100,
                },
                {
                    "sequence": 10,
                    "decision": "permit",
                    "from_prefix_list": self.prefix_list.pk,
                    "set_local_pref": 200,
                },
                {
                    "sequence": 15,
                    "decision": "accept",
                    "set_next_hop": "abcd",
                },
            ],
        }
        route_policy_serializer = WritableRoutePolicySerializer(
            instance=self.route_policy, data=data
        )
        assert route_policy_serializer.is_valid() == False

    def test_route_policy_update_remove_term(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "decision": "permit",
                    "from_bgp_community_list": self.bgp_community_list.pk,
                    "set_local_pref": 100,
                }
            ],
        }
        route_policy_serializer = WritableRoutePolicySerializer(
            instance=self.route_policy, data=data
        )
        assert route_policy_serializer.is_valid() == True
        route_policy_serializer.save()
        validate(self.device, data)

    def test_route_policy_update_replace_terms(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 6,
                    "decision": "permit",
                    "from_bgp_community_list": self.bgp_community_list.pk,
                    "set_local_pref": 100,
                },
                {
                    "sequence": 11,
                    "decision": "permit",
                    "from_prefix_list": self.prefix_list.pk,
                    "set_local_pref": 200,
                },
            ],
        }
        route_policy_serializer = WritableRoutePolicySerializer(
            instance=self.route_policy, data=data
        )
        assert route_policy_serializer.is_valid() == True
        route_policy_serializer.save()
        validate(self.device, data)

    def test_route_policy_update_attr_term(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 5,
                    "decision": "deny",  # change to deny
                    "from_bgp_community_list": self.bgp_community_list.pk,
                    "set_local_pref": 100,
                },
                {
                    "sequence": 10,
                    "decision": "permit",
                    "from_prefix_list": self.prefix_list.pk,
                    "set_local_pref": 50,  # change local pref
                },
            ],
        }
        route_policy_serializer = WritableRoutePolicySerializer(
            instance=self.route_policy, data=data
        )
        assert route_policy_serializer.is_valid() == True
        route_policy_serializer.save()
        validate(self.device, data)

    def test_route_policy_update_set_bad_lists_attr_term(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 5,
                    "decision": "deny",
                    "from_bgp_community_list": self.bgp_community_list2.pk,
                    "set_local_pref": 100,
                },
                {
                    "sequence": 10,
                    "decision": "permit",
                    "from_prefix_list": self.prefix_list2.pk,
                },
            ],
        }
        route_policy_serializer = WritableRoutePolicySerializer(
            instance=self.route_policy, data=data
        )
        assert not route_policy_serializer.is_valid()
        assert route_policy_serializer.errors["errors"][0] == ErrorDetail(
            string="from_bgp_community_list is not on the same device",
            code="invalid",
        )
        assert route_policy_serializer.errors["errors"][1] == ErrorDetail(
            string="from_prefix_list is not on the same device",
            code="invalid",
        )

    def test_route_policy_update_no_terms(self):
        data = {
            "name": "RM-TEST",
            "device": {"name": "router-test"},
            "terms": [],
        }
        route_policy_serializer = WritableRoutePolicySerializer(
            instance=self.route_policy, data=data
        )
        assert route_policy_serializer.is_valid() == True

        with self.assertRaisesRegex(
            ValidationError,
            "input is not valid, you must have at least one term in your route policy.",
        ):
            route_policy_serializer.save()
