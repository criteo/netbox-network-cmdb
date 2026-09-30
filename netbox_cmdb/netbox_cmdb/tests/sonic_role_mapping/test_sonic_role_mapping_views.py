from django.urls import reverse
from utilities.testing import TestCase

from netbox_cmdb.models.sonic_role_mapping import SonicRoleMapping
from netbox_cmdb.tests.common import BaseTestCase


class SonicRoleMappingViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        # Reuse the device fixtures of the other CMDB tests.
        BaseTestCase.setUp(self)
        self.role = self.device1.device_role

    def test_list_view_renders(self):
        SonicRoleMapping.objects.create(device_role=self.role, sonic_type="ToRRouter")

        response = self.client.get(reverse("plugins:netbox_cmdb:sonicrolemapping_list"))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "ToRRouter")

    def test_add_view_renders(self):
        response = self.client.get(reverse("plugins:netbox_cmdb:sonicrolemapping_add"))

        self.assertHttpStatus(response, 200)

    def test_create_mapping_through_the_ui(self):
        response = self.client.post(
            reverse("plugins:netbox_cmdb:sonicrolemapping_add"),
            {"device_role": self.role.pk, "sonic_type": "LeafRouter"},
        )

        self.assertHttpStatus(response, 302)
        assert SonicRoleMapping.objects.get(device_role=self.role).sonic_type == "LeafRouter"

    def test_delete_view(self):
        mapping = SonicRoleMapping.objects.create(device_role=self.role, sonic_type="ToRRouter")

        response = self.client.post(
            reverse("plugins:netbox_cmdb:sonicrolemapping_delete", kwargs={"pk": mapping.pk}),
            {"confirm": True},
        )

        self.assertHttpStatus(response, 302)
        assert SonicRoleMapping.objects.exists() is False
