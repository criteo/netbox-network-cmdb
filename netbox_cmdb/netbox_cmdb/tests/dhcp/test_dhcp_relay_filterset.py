from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.filtersets import DhcpRelayInterfaceFilterSet
from netbox_cmdb.models import LogicalInterface
from netbox_cmdb.models.dhcp import DhcpRelayInterface, DhcpServer
from netbox_cmdb.tests.interface.test_interface_filterset import create_topology


def create_relays():
    """Create the topology of create_topology(), with a DHCP relay on every logical interface."""
    create_topology()
    server = DhcpServer.objects.create(server_address="198.51.100.1")
    for logical_interface in LogicalInterface.objects.all():
        relay = DhcpRelayInterface.objects.create(logical_interface=logical_interface)
        relay.server_list.add(server)


class DhcpRelayDeviceLocationFilterSetTestCase(TestCase):
    """DHCP relays are filtered by location under the same names as the other models."""

    @classmethod
    def setUpTestData(cls):
        create_relays()

    def test_relays_by_location(self):
        for params in [
            {"device__site__name": ["DC1"]},
            {"logical_interface__parent_interface__device__site__name": ["DC1"]},
        ]:
            queryset = DhcpRelayInterfaceFilterSet(params, DhcpRelayInterface.objects.all()).qs
            self.assertEqual(
                sorted(relay.device.name for relay in queryset),
                ["dc1-spine", "dc1-tor"],
                params,
            )


class DhcpRelayDeviceLocationAPITestCase(APITestCase):
    """The DHCP relay endpoint accepts the device location filters."""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        create_relays()

    def test_endpoint(self):
        url = reverse("plugins-api:netbox_cmdb-api:dhcprelayinterface-list")
        for params, want in [
            ({"device__site__name": "DC2"}, 1),
            ({"device__site__name": "DC4"}, 0),
            ({"logical_interface__parent_interface__device__site__name": "DC1"}, 2),
            ({"logical_interface__parent_interface__device__name": "dc3-tor"}, 1),
        ]:
            response = self.client.get(url, params, **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], want, params)
