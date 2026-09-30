from netbox_cmdb.models.sonic_role_mapping import SonicRoleMapping
from netbox_cmdb.tests.common import BaseTestCase


class SonicRoleMappingModelTestCase(BaseTestCase):
    def test_mapping_defaults_to_not_provisioned(self):
        mapping = SonicRoleMapping.objects.create(device_role=self.device1.device_role)

        assert mapping.sonic_type == "not-provisioned"

    def test_devices_of_a_same_role_share_the_mapping(self):
        SonicRoleMapping.objects.create(
            device_role=self.device1.device_role, sonic_type="LeafRouter"
        )

        for device in (self.device1, self.device2):
            assert device.device_role.sonic_role_mapping.sonic_type == "LeafRouter"

    def test_deleting_the_role_deletes_its_mapping(self):
        role = self.device1.device_role
        SonicRoleMapping.objects.create(device_role=role, sonic_type="ToRRouter")
        self.device1.delete()
        self.device2.delete()

        role.delete()

        assert SonicRoleMapping.objects.exists() is False
