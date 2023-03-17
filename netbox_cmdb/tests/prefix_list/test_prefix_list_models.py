from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.forms import ValidationError
from django.test import TestCase
from netaddr import IPNetwork
from netbox_cmdb.models.prefix_list import PrefixList, PrefixListTerm


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


class ValidPrefixListTestCase(BaseTestCase):
    def test_valid_prefix_list_ipv4(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv4", device=self.device
        )
        PrefixListTerm.objects.create(
            prefix_list=prefix_list,
            sequence=10,
            decision="permit",
            prefix=IPNetwork("10.0.0.0/8"),
            ge=24,
            le=32,
        )

    def test_valid_prefix_list_ipv6(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv6", device=self.device
        )
        PrefixListTerm.objects.create(
            prefix_list=prefix_list,
            sequence=10,
            decision="permit",
            prefix=IPNetwork("2001:DB8::/32"),
            ge=48,
            le=128,
        )


class InvalidPrefixListTestCase(BaseTestCase):
    def test_ipv6_prefix_in_ipv4_prefix_list(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv4", device=self.device
        )
        with self.assertRaisesRegex(ValidationError, "Invalid IP prefix, IP version mismatch"):
            PrefixListTerm.objects.create(
                prefix_list=prefix_list,
                sequence=10,
                decision="permit",
                prefix=IPNetwork("2001:DB8::/32"),
            )

    def test_ipv4_prefix_in_ipv6_prefix_list(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv6", device=self.device
        )
        with self.assertRaisesRegex(ValidationError, "Invalid IP prefix, IP version mismatch"):
            PrefixListTerm.objects.create(
                prefix_list=prefix_list,
                sequence=10,
                decision="permit",
                prefix=IPNetwork("10.0.0.0/8"),
            )

    def test_ipv4_max_prefix_len(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv4", device=self.device
        )
        with self.assertRaisesRegex(ValidationError, "Invalid le value"):
            PrefixListTerm.objects.create(
                prefix_list=prefix_list,
                sequence=10,
                decision="permit",
                prefix=IPNetwork("10.0.0.0/8"),
                le=48,
            )

    def test_ipv6_max_prefix_len(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv6", device=self.device
        )
        with self.assertRaisesRegex(ValidationError, "Invalid ge value"):
            PrefixListTerm.objects.create(
                prefix_list=prefix_list,
                sequence=10,
                decision="permit",
                prefix=IPNetwork("2001:DB8::/32"),
                ge=200,
            )

    def test_le_lower_than_prefix_len(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv4", device=self.device
        )
        with self.assertRaisesRegex(ValidationError, "Invalid le value"):
            PrefixListTerm.objects.create(
                prefix_list=prefix_list,
                sequence=10,
                decision="permit",
                prefix=IPNetwork("10.0.0.0/8"),
                le=6,
            )

    def test_le_lower_than_ge(self):
        prefix_list = PrefixList.objects.create(
            name="PF-TEST", ip_version="ipv4", device=self.device
        )
        with self.assertRaisesRegex(
            ValidationError,
            "'Invalid values for le and ge, le should be lower than ge",
        ):
            PrefixListTerm.objects.create(
                prefix_list=prefix_list,
                sequence=10,
                decision="permit",
                prefix=IPNetwork("10.0.0.0/8"),
                le=10,
                ge=24,
            )
