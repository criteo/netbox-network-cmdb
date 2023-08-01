from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.test import TestCase
from ipam.models.ip import IPAddress
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models.tenants import Tenant

from netbox_cmdb.filtersets import BGPSessionFilterSet
from netbox_cmdb.models.bgp import ASN, BGPSession, DeviceBGPSession


class BGPSessionTestCase(TestCase, NetBoxModelFilterSet):
    queryset = BGPSession.objects.all()
    filterset = BGPSessionFilterSet

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="model-test", slug="model-test"
        )
        device_role = DeviceRole.objects.create(name="role-test", slug="role-test")
        devices = [
            Device(name="router1", device_role=device_role, device_type=device_type, site=site),
            Device(name="router2", device_role=device_role, device_type=device_type, site=site),
            Device(name="router3", device_role=device_role, device_type=device_type, site=site),
            Device(name="router4", device_role=device_role, device_type=device_type, site=site),
        ]
        Device.objects.bulk_create(devices)

        tenants = [
            Tenant(name="tenant1", slug="tenant1"),
            Tenant(name="tenant2", slug="tenant2"),
            Tenant(name="tenant3", slug="tenant3"),
            Tenant(name="tenant4", slug="tenant4"),
        ]
        Tenant.objects.bulk_create(tenants)

        asns = [
            ASN(number="1", organization_name="router1"),
            ASN(number="2", organization_name="router2"),
            ASN(number="3", organization_name="router3"),
            ASN(number="4", organization_name="router4"),
        ]
        ASN.objects.bulk_create(asns)

        ip_addresses = [
            IPAddress(address="10.0.0.1/32"),
            IPAddress(address="10.0.0.2/32"),
            IPAddress(address="10.0.0.3/32"),
            IPAddress(address="10.0.0.4/32"),
        ]
        IPAddress.objects.bulk_create(ip_addresses)

        device_bgp_sessions = [
            DeviceBGPSession(device=devices[0], local_address=ip_addresses[0]),
            DeviceBGPSession(device=devices[1], local_address=ip_addresses[1]),
            DeviceBGPSession(device=devices[2], local_address=ip_addresses[2]),
            DeviceBGPSession(device=devices[3], local_address=ip_addresses[3]),
        ]
        DeviceBGPSession.objects.bulk_create(device_bgp_sessions)

        bgp_sessions = [
            BGPSession(
                state="production",
                peer_a=device_bgp_sessions[0],
                peer_b=device_bgp_sessions[1],
                tenant=tenants[0],
            ),
            BGPSession(
                state="production",
                peer_a=device_bgp_sessions[0],
                peer_b=device_bgp_sessions[2],
                tenant=tenants[1],
            ),
            BGPSession(
                state="production",
                peer_a=device_bgp_sessions[0],
                peer_b=device_bgp_sessions[3],
                tenant=tenants[2],
            ),
            BGPSession(
                state="production",
                peer_a=device_bgp_sessions[1],
                peer_b=device_bgp_sessions[2],
                tenant=tenants[3],
            ),
            BGPSession(
                state="production",
                peer_a=device_bgp_sessions[1],
                peer_b=device_bgp_sessions[3],
                tenant=tenants[0],
            ),
        ]
        BGPSession.objects.bulk_create(bgp_sessions)

    def test_device(self):
        params = {"device": ["router1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"device": ["router1", "router2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"device": ["router3", "router4"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_local_address(self):
        params = {"local_address": ["10.0.0.1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"local_address": ["10.0.0.1", "10.0.0.2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"local_address": ["10.0.0.3", "10.0.0.4"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_tenant(self):
        tenant = Tenant.objects.all().first()
        params = {"tenant": [tenant.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant_id": [tenant.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
