from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.models.sonic_role_mapping import SonicRoleMapping
from netbox_cmdb.tests.common import BaseTestCase


class SonicRoleMappingAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        # Reuse the device fixtures of the other CMDB tests.
        BaseTestCase.setUp(self)
        self.url = reverse("plugins-api:netbox_cmdb-api:sonicrolemapping-list")
        self.role = self.device1.device_role

    def test_create_role_mapping(self):
        response = self.client.post(
            self.url,
            {"device_role": self.role.pk, "sonic_type": "LeafRouter"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        assert SonicRoleMapping.objects.get(device_role=self.role).sonic_type == "LeafRouter"

    def test_read_nests_the_device_role(self):
        SonicRoleMapping.objects.create(device_role=self.role, sonic_type="ToRRouter")

        response = self.client.get(self.url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        [mapping] = response.data["results"]
        assert mapping["device_role"]["name"] == self.role.name
        assert mapping["sonic_type"] == "ToRRouter"

    def test_filter_by_device_role_name(self):
        SonicRoleMapping.objects.create(device_role=self.role, sonic_type="ToRRouter")

        response = self.client.get(f"{self.url}?device_role__name=unknown", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        assert response.data["results"] == []

    def test_a_role_can_only_be_mapped_once(self):
        SonicRoleMapping.objects.create(device_role=self.role, sonic_type="ToRRouter")

        response = self.client.post(
            self.url,
            {"device_role": {"name": self.role.name}, "sonic_type": "LeafRouter"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_unknown_sonic_type_is_rejected(self):
        response = self.client.post(
            self.url,
            {"device_role": self.role.pk, "sonic_type": "NotASonicType"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        assert "sonic_type" in response.data

    def test_sonic_types_outside_the_supported_subset_are_rejected(self):
        """BackEndToRRouter is valid for SONiC but not supported by the CMDB yet."""
        response = self.client.post(
            self.url,
            {"device_role": self.role.pk, "sonic_type": "BackEndToRRouter"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        assert "sonic_type" in response.data

    def test_sonic_type_defaults_to_not_provisioned(self):
        response = self.client.post(
            self.url, {"device_role": self.role.pk}, format="json", **self.header
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        assert response.data["sonic_type"] == "not-provisioned"

    def test_patch_updates_the_sonic_type(self):
        mapping = SonicRoleMapping.objects.create(device_role=self.role, sonic_type="ToRRouter")

        response = self.client.patch(
            reverse(
                "plugins-api:netbox_cmdb-api:sonicrolemapping-detail", kwargs={"pk": mapping.pk}
            ),
            {"sonic_type": "SpineRouter"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        mapping.refresh_from_db()
        assert mapping.sonic_type == "SpineRouter"
