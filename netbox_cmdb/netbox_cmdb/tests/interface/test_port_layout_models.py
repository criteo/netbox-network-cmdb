from dcim.models import DeviceRole, DeviceType, Manufacturer
from django.test import TestCase

from netbox_cmdb.models.interface import PortLayout


class PortLayoutTestCase(TestCase):
    def setUp(self):
        """Set up test data for PortLayout tests."""
        # Create manufacturer
        self.manufacturer = Manufacturer.objects.create(name="Vendor", slug="vendor")

        # Create device type (hardware model)
        self.device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer, model="Model", slug="model"
        )

        # Create device role (network role) - ToR
        self.device_role = DeviceRole.objects.create(name="ToR", slug="ToR")

    def test_create_port_layout_with_specified_mapping(self):
        """Test creating a PortLayout with the exact mapping specified by the user."""
        port_layout = PortLayout.objects.create(
            device_type=self.device_type,
            network_role=self.device_role,
            name="etp1",
            vendor_name="1",
            vendor_short_name="etp1",
            vendor_long_name="Ethernet0",
            label_name="1",
            logical_name="to_leaf_01",
        )

        # Verify the PortLayout was created successfully
        self.assertIsNotNone(port_layout.id)
        self.assertEqual(port_layout.device_type, self.device_type)
        self.assertEqual(port_layout.network_role, self.device_role)
        self.assertEqual(port_layout.name, "etp1")
        self.assertEqual(port_layout.vendor_name, "1")
        self.assertEqual(port_layout.vendor_short_name, "etp1")
        self.assertEqual(port_layout.vendor_long_name, "Ethernet0")
        self.assertEqual(port_layout.label_name, "1")
        self.assertEqual(port_layout.logical_name, "to_leaf_01")
