from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.models.dhcp import DhcpRelayInterface, DhcpServer
from netbox_cmdb.tests.dhcp.common import create_logical_interface


class DhcpRelayInterfaceAPITestCase(APITestCase):
    """Exercise the dhcp-server and dhcp-relay-interface endpoints through router and viewsets."""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        self.server_url = reverse("plugins-api:netbox_cmdb-api:dhcpserver-list")
        self.url = reverse("plugins-api:netbox_cmdb-api:dhcprelayinterface-list")
        self.l3 = create_logical_interface(device_name="router-test1")
        self.l2 = create_logical_interface(device_name="router-test2", port="Ethernet20", type="l2")
        self.server1 = DhcpServer.objects.create(server_address="10.1.8.67")
        self.server2 = DhcpServer.objects.create(server_address="10.1.8.68")

    def _detail_url(self, relay):
        return reverse(
            "plugins-api:netbox_cmdb-api:dhcprelayinterface-detail", kwargs={"pk": relay.pk}
        )

    def _post(self, data):
        return self.client.post(self.url, data, format="json", **self.header)

    def test_create_server_and_reject_a_duplicate_address(self):
        response = self.client.post(
            self.server_url, {"server_address": "10.1.8.69"}, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        response = self.client.post(
            self.server_url, {"server_address": "10.1.8.69"}, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_create_relay_with_servers(self):
        response = self._post(
            {
                "logical_interface": self.l3.pk,
                "server_list": [self.server1.pk, self.server2.pk],
            }
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        relay = DhcpRelayInterface.objects.get(logical_interface=self.l3)
        self.assertEqual(set(relay.server_list.all()), {self.server1, self.server2})

    def test_create_with_a_nested_logical_interface(self):
        response = self._post(
            {
                "logical_interface": {
                    "index": 0,
                    "parent_interface__name": "Ethernet10",
                    "parent_interface__device__name": "router-test1",
                },
                "server_list": [self.server1.pk],
            }
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DhcpRelayInterface.objects.get().logical_interface, self.l3)

    def test_relay_refused_on_a_non_l3_interface(self):
        response = self._post({"logical_interface": self.l2.pk, "server_list": [self.server1.pk]})

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("logical_interface", response.json())
        self.assertFalse(DhcpRelayInterface.objects.exists())

    def test_post_on_an_existing_relay_updates_it(self):
        relay = DhcpRelayInterface.objects.create(logical_interface=self.l3)
        relay.server_list.set([self.server1])

        # an omitted server_list leaves the servers untouched
        response = self._post({"logical_interface": self.l3.pk})
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DhcpRelayInterface.objects.count(), 1)
        self.assertEqual(set(relay.server_list.all()), {self.server1})

        # a given one replaces it
        response = self._post({"logical_interface": self.l3.pk, "server_list": [self.server2.pk]})
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(set(relay.server_list.all()), {self.server2})

    def test_patch_the_servers(self):
        relay = DhcpRelayInterface.objects.create(logical_interface=self.l3)
        relay.server_list.set([self.server1])

        response = self.client.patch(
            self._detail_url(relay),
            {"server_list": [self.server1.pk, self.server2.pk]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(set(relay.server_list.all()), {self.server1, self.server2})

    def test_read_nests_interface_and_servers(self):
        relay = DhcpRelayInterface.objects.create(logical_interface=self.l3)
        relay.server_list.set([self.server1])

        response = self.client.get(self._detail_url(relay), format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["logical_interface"]["parent_interface"]["name"], "Ethernet10")
        self.assertEqual([s["server_address"] for s in body["server_list"]], ["10.1.8.67"])

    def test_filter_by_device_and_port(self):
        DhcpRelayInterface.objects.create(logical_interface=self.l3)

        def count(query):
            response = self.client.get(f"{self.url}?{query}", format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            return response.json()["count"]

        self.assertEqual(count("logical_interface__parent_interface__device__name=router-test1"), 1)
        self.assertEqual(count("logical_interface__parent_interface__device__name=router-test2"), 0)
        self.assertEqual(count("logical_interface__parent_interface__name=Ethernet10"), 1)
