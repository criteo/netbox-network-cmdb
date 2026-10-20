from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.test import TestCase
from django.urls import reverse
from ipam.models import IPAddress
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.filtersets import (
    LinkFilterSet,
    LogicalInterfaceFilterSet,
    ManagementRouteFilterSet,
)
from netbox_cmdb.models import DeviceInterface, Link, LogicalInterface, ManagementRoute


def create_topology():
    """Create four devices in three sites, linked as dc1-tor <-> dc1-spine (both in DC1) and
    dc1-spine <-> dc2-tor (DC1 to DC2), dc3-tor being in no link.

    Each device has a logical interface on its management port, with a management route.
    """
    manufacturer = Manufacturer.objects.create(name="vendor", slug="vendor")
    device_type = DeviceType.objects.create(manufacturer=manufacturer, model="model", slug="model")
    device_role = DeviceRole.objects.create(name="role", slug="role")
    sites = {
        "DC1": Site.objects.create(name="DC1", slug="dc1"),
        "DC2": Site.objects.create(name="DC2", slug="dc2"),
        "DC3": Site.objects.create(name="DC3", slug="dc3"),
    }

    interfaces = {}
    for name, site in [
        ("dc1-tor", "DC1"),
        ("dc1-spine", "DC1"),
        ("dc2-tor", "DC2"),
        ("dc3-tor", "DC3"),
    ]:
        device = Device.objects.create(
            name=name, device_role=device_role, device_type=device_type, site=sites[site]
        )
        mgmt = DeviceInterface.objects.create(name="eth0", device=device)
        for port in ["to_peer_1", "to_peer_2"]:
            interfaces[(name, port)] = DeviceInterface.objects.create(name=port, device=device)

        logical_interface = LogicalInterface.objects.create(
            index=0,
            parent_interface=mgmt,
            type="l3",
            ipv4_address=IPAddress.objects.create(address=f"192.0.2.{len(interfaces)}/24"),
        )
        ManagementRoute.objects.create(
            logical_interface=logical_interface,
            kind="static",
            prefix="0.0.0.0/0",
            next_hop="192.0.2.254",
        )

    Link.objects.create(
        interface_a=interfaces[("dc1-tor", "to_peer_1")],
        interface_b=interfaces[("dc1-spine", "to_peer_1")],
    )
    Link.objects.create(
        interface_a=interfaces[("dc1-spine", "to_peer_2")],
        interface_b=interfaces[("dc2-tor", "to_peer_1")],
    )


class DeviceLocationFilterSetTestCase(TestCase):
    """Every model attached to a device is filtered by location under the same names."""

    @classmethod
    def setUpTestData(cls):
        create_topology()

    def _links(self, params):
        queryset = LinkFilterSet(params, Link.objects.all()).qs
        return sorted(
            (link.interface_a.device.name, link.interface_b.device.name) for link in queryset
        )

    def test_links_with_one_end_in_the_location(self):
        self.assertEqual(
            self._links({"device__site__name": ["DC2"]}),
            [("dc1-spine", "dc2-tor")],
        )
        self.assertEqual(
            self._links({"device__site__name": ["DC1"]}),
            [("dc1-spine", "dc2-tor"), ("dc1-tor", "dc1-spine")],
        )

    def test_links_in_any_of_the_locations(self):
        self.assertEqual(len(self._links({"device__site__name": ["DC2", "DC3"]})), 1)

    def test_links_without_end_in_the_location(self):
        self.assertEqual(self._links({"device__site__name": ["DC3"]}), [])

    def test_logical_interfaces_by_location(self):
        for params in [
            {"device__site__name": ["DC2"]},
            {"parent_interface__device__site__name": ["DC2"]},
        ]:
            queryset = LogicalInterfaceFilterSet(params, LogicalInterface.objects.all()).qs
            self.assertEqual(
                [li.parent_interface.device.name for li in queryset], ["dc2-tor"], params
            )

    def test_management_routes_by_location(self):
        for params in [
            {"device__site__name": ["DC1"]},
            {"logical_interface__parent_interface__device__site__name": ["DC1"]},
        ]:
            queryset = ManagementRouteFilterSet(params, ManagementRoute.objects.all()).qs
            self.assertEqual(
                sorted(route.logical_interface.parent_interface.device.name for route in queryset),
                ["dc1-spine", "dc1-tor"],
                params,
            )


class DeviceLocationAPITestCase(APITestCase):
    """The API endpoints accept the device location filters."""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        create_topology()

    def _count(self, endpoint, params):
        url = reverse(f"plugins-api:netbox_cmdb-api:{endpoint}-list")
        response = self.client.get(url, params, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        return response.data["count"]

    def test_endpoints(self):
        for endpoint, params, want in [
            ("link", {"device__site__name": "DC2"}, 1),
            ("link", {"device__site__name": "DC3"}, 0),
            ("link", {"interface_a__name": "to_peer_2"}, 1),
            ("logicalinterface", {"device__site__name": "DC1"}, 2),
            ("logicalinterface", {"parent_interface__device__site__name": "DC1"}, 2),
            ("managementroute", {"device__site__name": "DC3"}, 1),
            (
                "managementroute",
                {"logical_interface__parent_interface__device__name": "dc2-tor"},
                1,
            ),
        ]:
            self.assertEqual(self._count(endpoint, params), want, (endpoint, params))
