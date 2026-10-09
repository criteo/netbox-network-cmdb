from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.models.sonic_hwsku_mapping import SonicHwskuMapping
from netbox_cmdb.tests.common import BaseTestCase


class SonicHwskuMappingAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        # Reuse the device fixtures of the other CMDB tests.
        BaseTestCase.setUp(self)
        self.url = reverse("plugins-api:netbox_cmdb-api:sonichwskumapping-list")
        self.device_type = self.device1.device_type

    def test_create_hwsku_mapping(self):
        response = self.client.post(
            self.url,
            {"device_type": self.device_type.pk, "hwsku": "ACS-MSN2700"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        assert SonicHwskuMapping.objects.get(device_type=self.device_type).hwsku == "ACS-MSN2700"

    def test_read_nests_the_device_type(self):
        SonicHwskuMapping.objects.create(device_type=self.device_type, hwsku="ACS-MSN2700")

        response = self.client.get(self.url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        [mapping] = response.data["results"]
        assert mapping["device_type"]["model"] == self.device_type.model
        assert mapping["hwsku"] == "ACS-MSN2700"

    def test_filter_by_device_type_model(self):
        SonicHwskuMapping.objects.create(device_type=self.device_type, hwsku="ACS-MSN2700")

        response = self.client.get(f"{self.url}?device_type__model=unknown", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        assert response.data["results"] == []

    def test_a_device_type_can_only_be_mapped_once(self):
        SonicHwskuMapping.objects.create(device_type=self.device_type, hwsku="ACS-MSN2700")

        response = self.client.post(
            self.url,
            {"device_type": self.device_type.pk, "hwsku": "Mellanox-SN2700"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_hwsku_is_required(self):
        response = self.client.post(
            self.url, {"device_type": self.device_type.pk}, format="json", **self.header
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        assert "hwsku" in response.data

    def test_patch_updates_the_hwsku(self):
        mapping = SonicHwskuMapping.objects.create(
            device_type=self.device_type, hwsku="ACS-MSN2700"
        )

        response = self.client.patch(
            reverse(
                "plugins-api:netbox_cmdb-api:sonichwskumapping-detail", kwargs={"pk": mapping.pk}
            ),
            {"hwsku": "Mellanox-SN2700"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        mapping.refresh_from_db()
        assert mapping.hwsku == "Mellanox-SN2700"
