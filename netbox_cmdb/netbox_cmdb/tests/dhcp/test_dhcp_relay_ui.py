from django.test import Client
from django.urls import reverse
from utilities.testing import APITestCase

from netbox_cmdb.filtersets import DhcpRelayInterfaceFilterSet
from netbox_cmdb.forms import DhcpRelayInterfaceForm
from netbox_cmdb.models.dhcp import DhcpRelayInterface, DhcpServer
from netbox_cmdb.tests.dhcp.common import create_logical_interface


class DhcpRelayInterfaceUITestCase(APITestCase):
    user_permissions = (
        "netbox_cmdb.view_dhcprelayinterface",
        "netbox_cmdb.view_dhcpserver",
        "netbox_cmdb.view_logicalinterface",
    )

    def setUp(self):
        super().setUp()
        self.l3 = create_logical_interface(device_name="router-test1")
        self.l2 = create_logical_interface(device_name="router-test2", port="Ethernet20", type="l2")
        self.server = DhcpServer.objects.create(server_address="10.1.8.67")

    def test_form_creates_a_relay(self):
        form = DhcpRelayInterfaceForm(
            data={"logical_interface": self.l3.pk, "server_list": [self.server.pk]}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(set(form.save().server_list.all()), {self.server})

    def test_form_only_offers_l3_interfaces(self):
        form = DhcpRelayInterfaceForm(
            data={"logical_interface": self.l2.pk, "server_list": [self.server.pk]}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("logical_interface", form.errors)

    def test_views_render(self):
        relay = DhcpRelayInterface.objects.create(logical_interface=self.l3)
        relay.server_list.set([self.server])
        client = Client()
        client.force_login(self.user)

        response = client.get(reverse("plugins:netbox_cmdb:dhcprelayinterface_list"))
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "router-test1")
        self.assertContains(response, "10.1.8.67")

        response = client.get(reverse("plugins:netbox_cmdb:dhcpserver_list"))
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "10.1.8.67")

    def test_search(self):
        other = create_logical_interface(device_name="router-other", port="Ethernet30")
        DhcpRelayInterface.objects.create(logical_interface=self.l3)
        DhcpRelayInterface.objects.create(logical_interface=other)

        def search(value):
            return set(
                DhcpRelayInterfaceFilterSet(
                    {"q": value}, DhcpRelayInterface.objects.all()
                ).qs.values_list("logical_interface__parent_interface__name", flat=True)
            )

        self.assertEqual(search("router-other"), {"Ethernet30"})
        self.assertEqual(search("Ethernet"), {"Ethernet10", "Ethernet30"})
