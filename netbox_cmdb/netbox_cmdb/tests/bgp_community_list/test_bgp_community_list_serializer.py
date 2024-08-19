from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.test import TestCase
from rest_framework.serializers import ValidationError

from netbox_cmdb.api.bgp_community_list.serializers import BGPCommunityListSerializer
from netbox_cmdb.models.bgp_community_list import BGPCommunityList, BGPCommunityListTerm


def validate(device, data):
    """Helper to validate that content is conform."""

    terms_data = data.pop("terms")

    cl_expected = BGPCommunityList(name="CL-TEST", device=device)
    cl_got = BGPCommunityList.objects.get(name="CL-TEST")

    assert cl_got.name == cl_expected.name
    assert cl_got.device == cl_expected.device

    cl_terms_got = list(
        BGPCommunityListTerm.objects.filter(bgp_community_list=cl_got).order_by("sequence")
    )
    assert len(cl_terms_got) == len(terms_data)

    cl_terms_expected = []
    for term_data in terms_data:
        cl_terms_expected.append(BGPCommunityListTerm(bgp_community_list=cl_got, **term_data))

    for cl_term_got, cl_term_expected in zip(cl_terms_got, cl_terms_expected):
        assert cl_term_got.sequence == cl_term_expected.sequence
        assert cl_term_got.community == cl_term_expected.community


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


class BGPCommunityListSerializerCreate(BaseTestCase):
    def test_bgp_community_list_creation(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "community": "64512:1000",
                },
                {
                    "sequence": 10,
                    "community": "64512:2000",
                },
            ],
        }

        bgp_com_list_serializer = BGPCommunityListSerializer(data=data)
        assert bgp_com_list_serializer.is_valid() is True

    def test_bgp_community_list_creation_with_empty_terms(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
            "terms": [],
        }

        bgp_com_list_serializer = BGPCommunityListSerializer(data=data)
        assert bgp_com_list_serializer.is_valid() is True

        with self.assertRaisesRegex(
            ValidationError,
            "input is not valid, you must have at least one term in your bgp-community-list.",
        ):
            bgp_com_list_serializer.save()

    def test_bgp_community_list_creation_without_terms(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
        }

        bgp_com_list_serializer = BGPCommunityListSerializer(data=data)
        assert bgp_com_list_serializer.is_valid() is False


class BGPCommunityListSerializerUpdate(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.prefix_list = BGPCommunityList.objects.create(name="CL-TEST", device=self.device)
        data_terms = [
            {
                "sequence": 5,
                "community": "64512:1000",
            },
            {
                "sequence": 10,
                "community": "64512:2000",
            },
        ]

        self.prefix_list_terms = BGPCommunityListTerm.objects.bulk_create(
            [
                BGPCommunityListTerm(bgp_community_list=self.prefix_list, **data_term)
                for data_term in data_terms
            ]
        )

    def test_bgp_community_list_update_add_term(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "community": "64512:1000",
                },
                {
                    "sequence": 10,
                    "community": "64512:2000",
                },
                {
                    "sequence": 15,
                    "community": "64512:666",
                },
            ],
        }
        bgp_com_list_serializer = BGPCommunityListSerializer(instance=self.prefix_list, data=data)
        assert bgp_com_list_serializer.is_valid() is True
        bgp_com_list_serializer.save()
        validate(self.device, data)

    def test_bgp_community_list_update_remove_term(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "community": "64512:1000",
                }
            ],
        }
        bgp_com_list_serializer = BGPCommunityListSerializer(instance=self.prefix_list, data=data)
        assert bgp_com_list_serializer.is_valid() is True
        bgp_com_list_serializer.save()
        validate(self.device, data)

    def test_bgp_community_list_update_replace_terms(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
            "terms": [
                {
                    "sequence": 5,
                    "community": "64512:1000",
                },
                {
                    "sequence": 10,
                    "community": "64512:2000",
                },
            ],
        }
        bgp_com_list_serializer = BGPCommunityListSerializer(instance=self.prefix_list, data=data)
        assert bgp_com_list_serializer.is_valid() is True
        bgp_com_list_serializer.save()
        validate(self.device, data)

    def test_bgp_community_list_update_attr_term(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 5,
                    "community": "64512:1000",
                },
                {
                    "sequence": 10,
                    "community": "64512:3000",  # changing value
                },
            ],
        }
        bgp_com_list_serializer = BGPCommunityListSerializer(instance=self.prefix_list, data=data)
        assert bgp_com_list_serializer.is_valid() is True
        bgp_com_list_serializer.save()
        validate(self.device, data)

    def test_bgp_community_list_update_no_terms(self):
        data = {
            "name": "CL-TEST",
            "device": {"name": "router-test"},
            "terms": [],
        }
        bgp_com_list_serializer = BGPCommunityListSerializer(instance=self.prefix_list, data=data)
        assert bgp_com_list_serializer.is_valid() is True

        with self.assertRaisesRegex(
            ValidationError,
            "input is not valid, you must have at least one term in your bgp-community-list.",
        ):
            bgp_com_list_serializer.save()
