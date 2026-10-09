from netbox_cmdb.models.sonic_hwsku_mapping import SonicHwskuMapping
from netbox_cmdb.tests.common import BaseTestCase


class SonicHwskuMappingModelTestCase(BaseTestCase):
    def test_devices_of_a_same_model_share_the_mapping(self):
        SonicHwskuMapping.objects.create(device_type=self.device1.device_type, hwsku="ACS-MSN2700")

        for device in (self.device1, self.device2):
            assert device.device_type.sonic_hwsku_mapping.hwsku == "ACS-MSN2700"

    def test_deleting_the_device_type_deletes_its_mapping(self):
        device_type = self.device1.device_type
        SonicHwskuMapping.objects.create(device_type=device_type, hwsku="ACS-MSN2700")
        self.device1.delete()
        self.device2.delete()

        device_type.delete()

        assert SonicHwskuMapping.objects.exists() is False
