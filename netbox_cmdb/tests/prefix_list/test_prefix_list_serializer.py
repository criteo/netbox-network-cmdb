from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.test import TestCase
from netbox_cmdb.api.prefix_list.serializers import PrefixListSerializer
from netbox_cmdb.models.prefix_list import PrefixList, PrefixListTerm
from rest_framework.serializers import ValidationError


def validate(device, data):
    """Helper to validate that content of a prefix-list is conform."""

    terms_data = data.pop("terms")

    pf_expected = PrefixList(name="PF-TEST", device=device, ip_version="ipv4")
    pf_got = PrefixList.objects.get(name="PF-TEST")

    assert pf_got.name == pf_expected.name
    assert pf_got.device == pf_expected.device
    assert pf_got.ip_version == pf_expected.ip_version

    pf_terms_got = list(PrefixListTerm.objects.filter(prefix_list=pf_got).order_by("sequence"))
    assert len(pf_terms_got) == len(terms_data)

    pf_terms_expected = []
    for term_data in terms_data:
        pf_terms_expected.append(PrefixListTerm(prefix_list=pf_got, **term_data))

    for pf_term_got, pf_term_expected in zip(pf_terms_got, pf_terms_expected):
        assert pf_term_got.sequence == pf_term_expected.sequence
        assert pf_term_got.decision == pf_term_expected.decision
        assert str(pf_term_got.prefix) == str(pf_term_expected.prefix)
        assert pf_term_got.le == pf_term_expected.le
        assert pf_term_got.ge == pf_term_expected.ge


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


class PrefixListSerializerCreate(BaseTestCase):
    def test_prefix_list_creation(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 5,
                    "decision": "permit",
                    "prefix": "10.0.0.0/24",
                    "le": 32,
                },
                {
                    "sequence": 10,
                    "decision": "deny",
                    "prefix": "192.168.1.0/24",
                },
            ],
        }

        pf_serializer = PrefixListSerializer(data=data)
        assert pf_serializer.is_valid() == True

    def test_prefix_list_creation_with_empty_terms(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [],
        }

        pf_serializer = PrefixListSerializer(data=data)
        assert pf_serializer.is_valid() == True

        with self.assertRaisesRegex(
            ValidationError,
            "input is not valid, you must have at least one term in your prefix-list.",
        ):
            pf_serializer.save()

    def test_prefix_list_creation_without_terms(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
        }

        pf_serializer = PrefixListSerializer(data=data)
        assert pf_serializer.is_valid() == False


class PrefixListSerializerUpdate(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.prefix_list = PrefixList.objects.create(
            name="PF-TEST", device=self.device, ip_version="ipv4"
        )
        data_terms = [
            {
                "sequence": 5,
                "decision": "permit",
                "prefix": "10.0.0.0/24",
                "le": 32,
            },
            {
                "sequence": 10,
                "decision": "deny",
                "prefix": "192.168.1.0/24",
            },
        ]

        self.prefix_list_terms = PrefixListTerm.objects.bulk_create(
            [PrefixListTerm(prefix_list=self.prefix_list, **data_term) for data_term in data_terms]
        )

    def test_prefix_list_update_add_term(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 5,
                    "decision": "permit",
                    "prefix": "10.0.0.0/24",
                    "le": 32,
                },
                {
                    "sequence": 10,
                    "decision": "deny",
                    "prefix": "192.168.1.0/24",
                },
                {
                    "sequence": 15,
                    "decision": "deny",
                    "prefix": "192.168.2.0/24",
                },
            ],
        }
        pf_serializer = PrefixListSerializer(instance=self.prefix_list, data=data)
        assert pf_serializer.is_valid() == True
        pf_serializer.save()
        validate(self.device, data)

    def test_prefix_list_update_remove_term(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 5,
                    "decision": "permit",
                    "prefix": "10.0.0.0/24",
                    "le": 32,
                }
            ],
        }
        pf_serializer = PrefixListSerializer(instance=self.prefix_list, data=data)
        assert pf_serializer.is_valid() == True
        pf_serializer.save()
        validate(self.device, data)

    def test_prefix_list_update_replace_terms(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 6,
                    "decision": "permit",
                    "prefix": "10.0.0.0/24",
                    "le": 32,
                },
                {
                    "sequence": 15,
                    "decision": "deny",
                    "prefix": "10.1.1.0/24",
                    "le": 32,
                },
            ],
        }
        pf_serializer = PrefixListSerializer(instance=self.prefix_list, data=data)
        assert pf_serializer.is_valid() == True
        pf_serializer.save()
        validate(self.device, data)

    def test_prefix_list_update_attr_term(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [
                {
                    "sequence": 5,
                    "decision": "deny",  # changing it to deny
                    "prefix": "10.0.0.0/24",
                    "le": 32,
                },
                {
                    "sequence": 10,
                    "decision": "deny",
                    "prefix": "192.168.2.0/24",  # changing the prefix
                },
            ],
        }
        pf_serializer = PrefixListSerializer(instance=self.prefix_list, data=data)
        assert pf_serializer.is_valid() == True
        pf_serializer.save()
        validate(self.device, data)

    def test_prefix_list_update_no_terms(self):
        data = {
            "name": "PF-TEST",
            "device": {"name": "router-test"},
            "ip_version": "ipv4",
            "terms": [],
        }
        pf_serializer = PrefixListSerializer(instance=self.prefix_list, data=data)
        assert pf_serializer.is_valid() == True

        with self.assertRaisesRegex(
            ValidationError,
            "input is not valid, you must have at least one term in your prefix-list.",
        ):
            pf_serializer.save()
