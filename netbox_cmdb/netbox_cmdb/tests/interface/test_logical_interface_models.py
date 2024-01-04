from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.forms import ValidationError
from django.test import TestCase

from netbox_cmdb.models import VLAN, DeviceInterface, LogicalInterface


class BaseTestCase(TestCase):
    def setUp(self):
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="model-test", slug="model-test"
        )
        device_role = DeviceRole.objects.create(name="role-test", slug="role-test")
        device = Device.objects.create(
            name="router-test",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )

        DeviceInterface.objects.create(
            name="etp1",
            enabled=True,
            state="staging",
            monitoring_state="warning",
            device=device,
            autonegotiation=True,
            speed=100000,
            fec="rs",
            description="My device interface",
        )
        VLAN.objects.create(vid=1, name="VLAN 1", description="First VLAN")

    def test_valid_logical_interface(self):
        """Test that a logical interface can be created."""
        vlan = VLAN.objects.get(vid=1)
        device_interface = DeviceInterface.objects.get(name="etp1")

        logical_interface = LogicalInterface.objects.create(
            index=1,
            enabled=True,
            state="staging",
            monitoring_state="disabled",
            parent_interface=device_interface,
            mtu=1500,
            type="l3",
            description="My logical interface",
        )

        logical_interface.tagged_vlans.add(vlan)
        logical_interface.save()

    def test_invalid_logical_interface_untagged_and_tagged_vlans(self):
        """Test that a logical interface cannot have both tagged and untagged VLANs."""
        device_interface = DeviceInterface.objects.get(name="etp1")

        # Create VLAN instances
        vlan1 = VLAN.objects.create(vid=100, name="VLAN 100", description="First VLAN")
        vlan2 = VLAN.objects.create(vid=200, name="VLAN 200", description="Second VLAN")

        # Create a working LogicalInterface
        logical_interface = LogicalInterface.objects.create(
            index=2,
            enabled=True,
            state="staging",
            monitoring_state="disabled",
            parent_interface=device_interface,
            mtu=1500,
            type="l3",
            description="My logical interface",
        )

        # Set an untagged VLAN
        logical_interface.untagged_vlan = vlan1
        logical_interface.save()

        with self.assertRaisesRegex(
            ValidationError, "Untagged VLAN cannot be combined with tagged VLANs or native VLAN."
        ):
            # Add a tagged VLAN
            logical_interface.tagged_vlans.add(vlan2)
            logical_interface.save()

    def test_invalid_logical_interface_untagged_and_native_vlans(self):
        """Test that a logical interface cannot have both untagged and native VLANs."""
        device_interface = DeviceInterface.objects.get(name="etp1")

        vlan1 = VLAN.objects.create(vid=1000, name="VLAN 1000", description="First VLAN")
        vlan2 = VLAN.objects.create(vid=2000, name="VLAN 2000", description="Second VLAN")

        # Create a working LogicalInterface
        logical_interface = LogicalInterface.objects.create(
            index=3,
            enabled=True,
            state="staging",
            monitoring_state="disabled",
            parent_interface=device_interface,
            mtu=1500,
            type="l3",
            description="My logical interface",
        )

        # Set an untagged VLAN
        logical_interface.untagged_vlan = vlan1
        logical_interface.save()

        with self.assertRaisesRegex(
            ValidationError, "Untagged VLAN cannot be combined with tagged VLANs or native VLAN."
        ):
            # Set a native VLAN
            logical_interface.native_vlan = vlan2
            logical_interface.save()
