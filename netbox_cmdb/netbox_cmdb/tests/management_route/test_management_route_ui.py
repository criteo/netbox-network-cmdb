from django.test import Client
from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.filtersets import ManagementRouteFilterSet
from netbox_cmdb.forms import ManagementRouteForm
from netbox_cmdb.models import ManagementRoute
from netbox_cmdb.tests.management_route.common import create_management_interface


class ManagementRouteUITestCase(APITestCase):
    user_permissions = ("netbox_cmdb.view_managementroute", "netbox_cmdb.view_logicalinterface")

    def setUp(self):
        super().setUp()
        self.mgmt = create_management_interface()

    def _form_data(self, **kwargs):
        data = {
            "logical_interface": self.mgmt.pk,
            "kind": "static",
            "prefix": "0.0.0.0/0",
            "next_hop": "192.0.2.1",
        }
        data.update(kwargs)
        return data

    def test_form_creates_a_route(self):
        form = ManagementRouteForm(data=self._form_data())
        self.assertTrue(form.is_valid(), form.errors)
        route = form.save()
        self.assertEqual(str(route.next_hop), "192.0.2.1")

    def test_form_runs_the_model_validation(self):
        form = ManagementRouteForm(data=self._form_data(next_hop="10.0.0.1"))
        self.assertFalse(form.is_valid())
        self.assertIn("next_hop", form.errors)

        form = ManagementRouteForm(data=self._form_data(kind="forced", prefix="198.51.100.0/24"))
        self.assertFalse(form.is_valid())
        self.assertIn("next_hop", form.errors)

    def test_views_render(self):
        route = ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="static", prefix="0.0.0.0/0", next_hop="192.0.2.1"
        )
        ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="forced", prefix="198.51.100.0/24"
        )
        client = Client()
        client.force_login(self.user)

        response = client.get(route.get_absolute_url())
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertContains(response, "192.0.2.1")
        self.assertContains(response, "mgmt0.0")

        response = client.get(reverse("plugins:netbox_cmdb:managementroute_list"))
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertContains(response, "0.0.0.0/0")
        self.assertContains(response, "198.51.100.0/24")

        # the routes are listed on the logical interface page
        response = client.get(self.mgmt.get_absolute_url())
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertContains(response, "Management Routes")
        self.assertContains(response, "198.51.100.0/24")

    def test_search(self):
        other = create_management_interface(device_name="router-other", address="192.0.2.11/24")
        ManagementRoute.objects.create(
            logical_interface=self.mgmt, kind="static", prefix="0.0.0.0/0", next_hop="192.0.2.1"
        )
        ManagementRoute.objects.create(
            logical_interface=other, kind="forced", prefix="198.51.100.0/24"
        )

        def search(value):
            return set(
                ManagementRouteFilterSet(
                    {"q": value}, ManagementRoute.objects.all()
                ).qs.values_list("prefix", flat=True)
            )

        self.assertEqual({str(p) for p in search("router-other")}, {"198.51.100.0/24"})
        self.assertEqual({str(p) for p in search("mgmt0")}, {"0.0.0.0/0", "198.51.100.0/24"})
        # a destination matches the routes covering it, the default route covers everything
        self.assertEqual({str(p) for p in search("198.51.100.1")}, {"0.0.0.0/0", "198.51.100.0/24"})
        self.assertEqual({str(p) for p in search("8.8.8.8")}, {"0.0.0.0/0"})
