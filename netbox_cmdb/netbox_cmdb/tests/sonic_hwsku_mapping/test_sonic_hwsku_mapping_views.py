from django.urls import reverse
from utilities.testing import TestCase

from netbox_cmdb.models.sonic_hwsku_mapping import SonicHwskuMapping
from netbox_cmdb.tests.common import BaseTestCase


class SonicHwskuMappingViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        # Reuse the device fixtures of the other CMDB tests.
        BaseTestCase.setUp(self)
        self.device_type = self.device1.device_type

    def test_list_view_renders(self):
        SonicHwskuMapping.objects.create(device_type=self.device_type, hwsku="ACS-MSN2700")

        response = self.client.get(reverse("plugins:netbox_cmdb:sonichwskumapping_list"))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "ACS-MSN2700")

    def test_add_view_renders(self):
        response = self.client.get(reverse("plugins:netbox_cmdb:sonichwskumapping_add"))

        self.assertHttpStatus(response, 200)

    def test_create_mapping_through_the_ui(self):
        response = self.client.post(
            reverse("plugins:netbox_cmdb:sonichwskumapping_add"),
            {"device_type": self.device_type.pk, "hwsku": "ACS-MSN2700"},
        )

        self.assertHttpStatus(response, 302)
        assert SonicHwskuMapping.objects.get(device_type=self.device_type).hwsku == "ACS-MSN2700"

    def test_delete_view(self):
        mapping = SonicHwskuMapping.objects.create(
            device_type=self.device_type, hwsku="ACS-MSN2700"
        )

        response = self.client.post(
            reverse("plugins:netbox_cmdb:sonichwskumapping_delete", kwargs={"pk": mapping.pk}),
            {"confirm": True},
        )

        self.assertHttpStatus(response, 302)
        assert SonicHwskuMapping.objects.exists() is False
