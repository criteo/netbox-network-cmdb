from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.models import ManagementRoute
from netbox_cmdb.tests.management_route.common import create_management_interface


class ManagementRouteAPITestCase(APITestCase):
    """Exercise the management-routes endpoint end to end, through the router and the viewset."""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        self.url = reverse("plugins-api:netbox_cmdb-api:managementroute-list")
        self.mgmt = create_management_interface(device_name="router-test1")
        self.other = create_management_interface(
            device_name="router-test2", address="192.0.2.11/24"
        )

    def _detail_url(self, route):
        return reverse(
            "plugins-api:netbox_cmdb-api:managementroute-detail", kwargs={"pk": route.pk}
        )

    def _post(self, data):
        return self.client.post(self.url, data, format="json", **self.header)

    def test_create_static_default_route(self):
        response = self._post(
            {
                "logical_interface": self.mgmt.pk,
                "kind": "static",
                "prefix": "0.0.0.0/0",
                "next_hop": "192.0.2.1",
            }
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        route = ManagementRoute.objects.get(logical_interface=self.mgmt)
        self.assertEqual(str(route.prefix), "0.0.0.0/0")
        self.assertEqual(str(route.next_hop), "192.0.2.1")

    def test_create_with_a_nested_logical_interface(self):
        response = self._post(
            {
                "logical_interface": {
                    "index": 0,
                    "parent_interface__name": "mgmt0",
                    "parent_interface__device__name": "router-test2",
                },
                "kind": "forced",
                "prefix": "198.51.100.0/24",
            }
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        route = ManagementRoute.objects.get()
        self.assertEqual(route.logical_interface, self.other)
        self.assertEqual(route.next_hop, None)

    def test_read_nests_the_logical_interface(self):
        route = ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="static", prefix="0.0.0.0/0", next_hop="192.0.2.1"
        )

        response = self.client.get(self._detail_url(route), format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data["prefix"], "0.0.0.0/0")
        self.assertEqual(response.data["next_hop"], "192.0.2.1")
        self.assertEqual(response.data["display"], "router-test1--mgmt0.0--static--0.0.0.0/0")
        logical_interface = response.data["logical_interface"]
        self.assertEqual(logical_interface["id"], self.mgmt.pk)
        self.assertEqual(logical_interface["index"], 0)
        self.assertEqual(logical_interface["name"], "mgmt0.0")
        self.assertEqual(logical_interface["parent_interface"]["name"], "mgmt0")
        self.assertEqual(logical_interface["parent_interface"]["device"]["name"], "router-test1")

    def test_filter_by_device_name(self):
        for mgmt in (self.mgmt, self.other):
            ManagementRoute.objects.create(
                logical_interface=mgmt, kind="forced", prefix="198.51.100.0/24"
            )

        response = self.client.get(
            f"{self.url}?logical_interface__parent_interface__device__name=router-test2",
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(
            [
                r["logical_interface"]["parent_interface"]["device"]["name"]
                for r in response.data["results"]
            ],
            ["router-test2"],
        )

    def test_filter_by_site_and_kind(self):
        ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="static", prefix="0.0.0.0/0", next_hop="192.0.2.1"
        )
        ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="forced", prefix="198.51.100.0/24"
        )

        response = self.client.get(
            f"{self.url}?logical_interface__parent_interface__device__site__name=SiteTest&kind=forced",
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual([r["prefix"] for r in response.data["results"]], ["198.51.100.0/24"])

        response = self.client.get(
            f"{self.url}?logical_interface__parent_interface__device__site__name=OtherSite",
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_static_route_requires_a_next_hop(self):
        response = self._post(
            {"logical_interface": self.mgmt.pk, "kind": "static", "prefix": "0.0.0.0/0"}
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("next_hop", response.data)

    def test_next_hop_must_be_in_the_interface_subnet(self):
        response = self._post(
            {
                "logical_interface": self.mgmt.pk,
                "kind": "static",
                "prefix": "0.0.0.0/0",
                "next_hop": "10.0.0.1",
            }
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("must be in the subnet", str(response.data["next_hop"]))

    def test_forced_route_rejects_a_next_hop(self):
        response = self._post(
            {
                "logical_interface": self.mgmt.pk,
                "kind": "forced",
                "prefix": "198.51.100.0/24",
                "next_hop": "192.0.2.1",
            }
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("next_hop", response.data)

    def test_duplicate_is_rejected(self):
        ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="forced", prefix="198.51.100.0/24"
        )

        response = self._post(
            {"logical_interface": self.mgmt.pk, "kind": "forced", "prefix": "198.51.100.0/24"}
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", str(response.data))
        self.assertEqual(ManagementRoute.objects.count(), 1)

    def test_patch_the_next_hop(self):
        route = ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="static", prefix="0.0.0.0/0", next_hop="192.0.2.1"
        )

        response = self.client.patch(
            self._detail_url(route), {"next_hop": "192.0.2.2"}, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(str(ManagementRoute.objects.get(pk=route.pk).next_hop), "192.0.2.2")

        response = self.client.patch(
            self._detail_url(route), {"next_hop": "10.0.0.1"}, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        route = ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="forced", prefix="198.51.100.0/24"
        )

        response = self.client.delete(self._detail_url(route), **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ManagementRoute.objects.filter(pk=route.pk).exists())
