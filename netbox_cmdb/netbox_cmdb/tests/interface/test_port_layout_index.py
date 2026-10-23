from dcim.models import DeviceRole, DeviceType, Manufacturer
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.forms import PortLayoutForm
from netbox_cmdb.models.interface import PortLayout


class PortLayoutIndexFormTestCase(TestCase):
    def setUp(self):
        manufacturer = Manufacturer.objects.create(name="Vendor", slug="vendor")
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Model", slug="model"
        )
        self.tor = DeviceRole.objects.create(name="ToR", slug="tor")

    def data(self, **overrides):
        return {
            "device_type": self.device_type.pk,
            "network_role": self.tor.pk,
            "name": "etp0",
            "label_name": "0",
            "logical_name": "to_leaf_01",
            "vendor_name": "Ethernet0",
            "vendor_short_name": "etp0",
            "vendor_long_name": "Ethernet0",
            **overrides,
        }

    def test_form_saves_index(self):
        form = PortLayoutForm(data=self.data(index="0"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().index, 0)

    def test_form_index_is_optional(self):
        form = PortLayoutForm(data=self.data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.save().index)

    def test_form_rejects_negative_index(self):
        form = PortLayoutForm(data=self.data(index="-1"))
        self.assertFalse(form.is_valid())
        self.assertIn("index", form.errors)


class PortLayoutIndexAPITestCase(APITestCase):
    user_permissions = (
        "netbox_cmdb.view_portlayout",
        "netbox_cmdb.add_portlayout",
        "netbox_cmdb.change_portlayout",
    )

    def setUp(self):
        super().setUp()
        manufacturer = Manufacturer.objects.create(name="Vendor", slug="vendor")
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Model", slug="model"
        )
        self.tor = DeviceRole.objects.create(name="ToR", slug="tor")
        self.url = reverse("plugins-api:netbox_cmdb-api:portlayout-list")

    def post(self, name, **fields):
        data = {
            "device_type": {"id": self.device_type.pk},
            "network_role": {"id": self.tor.pk},
            "name": name,
            "label_name": name,
            "logical_name": name,
            "vendor_name": name,
            "vendor_short_name": name,
            "vendor_long_name": name,
            **fields,
        }
        return self.client.post(self.url, data, format="json", **self.header)

    def test_create_with_and_without_index(self):
        response = self.post("etp0", index=0)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["index"], 0)

        response = self.post("etp1")
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["index"])

    def test_breakout_ports_share_the_parent_index(self):
        for name in ("etp0a", "etp0b"):
            response = self.post(name, index=0)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)

    def test_patch_index(self):
        port_id = self.post("etp0").data["id"]
        response = self.client.patch(
            reverse("plugins-api:netbox_cmdb-api:portlayout-detail", kwargs={"pk": port_id}),
            {"index": 3},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(PortLayout.objects.get(pk=port_id).index, 3)

    def test_ui_renders_index(self):
        port = PortLayout.objects.create(
            device_type=self.device_type,
            network_role=self.tor,
            name="etp0",
            label_name="0",
            logical_name="to_leaf_01",
            vendor_name="Ethernet0",
            vendor_short_name="etp0",
            vendor_long_name="Ethernet0",
            index=17,
        )
        client = Client()
        client.force_login(self.user)
        for url in (
            port.get_absolute_url(),
            reverse(
                "plugins:netbox_cmdb:portlayout_group",
                kwargs={"device_type_id": self.device_type.pk, "network_role_id": self.tor.pk},
            ),
        ):
            with self.subTest(url=url):
                response = client.get(url)
                self.assertHttpStatus(response, status.HTTP_200_OK)
                self.assertRegex(response.content.decode(), r"<td[^>]*>\s*17\s*</td>")
