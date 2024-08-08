from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.test import TestCase
from ipam.models.ip import IPAddress
from tenancy.models.tenants import Tenant

from netbox_cmdb.models.bgp import ASN


class BaseTestCase(TestCase):
    def setUp(self):
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="model-test", slug="model-test"
        )
        device_role = DeviceRole.objects.create(name="role-test", slug="role-test")
        self.device1 = Device.objects.create(
            name="router-test1",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )
        self.asn1 = ASN.objects.create(number="1", organization_name="router-test1")
        self.ip_address1 = IPAddress.objects.create(address="10.0.0.1/32")
        self.device2 = Device.objects.create(
            name="router-test2",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )
        self.asn2 = ASN.objects.create(number="2", organization_name="router-test2")
        self.ip_address2 = IPAddress.objects.create(address="10.0.0.2/32")
        self.tenant = Tenant.objects.create(name="tenant1", slug="tenant1")
