from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.test import Client
from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.forms import LogicalInterfaceForm
from netbox_cmdb.models import DeviceInterface, LogicalInterface


class LogicalInterfaceUITestCase(APITestCase):
    user_permissions = ("netbox_cmdb.view_logicalinterface",)

    def setUp(self):
        super().setUp()
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device = Device.objects.create(
            name="router-test",
            device_role=DeviceRole.objects.create(name="role-test", slug="role-test"),
            device_type=DeviceType.objects.create(
                manufacturer=manufacturer, model="model-test", slug="model-test"
            ),
            site=site,
        )
        self.device_interface = DeviceInterface.objects.create(name="etp1", device=device)

    def test_form_use_ipv6_link_local_only(self):
        data = {
            "parent_interface": self.device_interface.pk,
            "index": 1,
            "enabled": True,
            "state": "staging",
            "monitoring_state": "disabled",
            "type": "l3",
        }
        form = LogicalInterfaceForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(form.save().use_ipv6_link_local_only)

        form = LogicalInterfaceForm(data={**data, "index": 2, "use_ipv6_link_local_only": True})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save().use_ipv6_link_local_only)

    def test_ui_renders_use_ipv6_link_local_only(self):
        logical_interface = LogicalInterface.objects.create(
            index=1,
            parent_interface=self.device_interface,
            type="l3",
            use_ipv6_link_local_only=True,
        )
        client = Client()
        client.force_login(self.user)

        response = client.get(logical_interface.get_absolute_url())
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertContains(response, "IPv6 link-local only")

        response = client.get(reverse("plugins:netbox_cmdb:logicalinterface_list"))
        self.assertHttpStatus(response, status.HTTP_200_OK)
