from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.test import TestCase
from ipam.models import IPAddress

from netbox_cmdb.choices import AssetMonitoringStateChoices, AssetStateChoices
from netbox_cmdb.models.interface import DeviceInterface, Link, LogicalInterface
from netbox_cmdb.models.vrf import VRF


class InterfaceTopologyTestCase(TestCase):
    def setUp(self):
        """Set up test data for interface topology tests."""
        # Create site
        self.site = Site.objects.create(name="SiteTest", slug="site-test")

        # Create manufacturer
        self.manufacturer = Manufacturer.objects.create(name="vendor", slug="vendor")

        # Create device type
        self.device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer, model="Model", slug="model"
        )

        # Create device roles
        self.device_role_tor = DeviceRole.objects.create(name="ToR", slug="tor")
        self.device_role_leaf = DeviceRole.objects.create(name="Leaf", slug="leaf")

        # Create devices
        self.device_tor = Device.objects.create(
            name="TOR-01",
            device_role=self.device_role_tor,
            device_type=self.device_type,
            site=self.site,
        )

        self.device_leaf = Device.objects.create(
            name="LEAF-01",
            device_role=self.device_role_leaf,
            device_type=self.device_type,
            site=self.site,
        )

        # Create VRF
        self.vrf = VRF.objects.create(name="PROD")

        # Create IP addresses
        self.ipv4_ra = IPAddress.objects.create(address="192.168.1.0/31")
        self.ipv4_sp = IPAddress.objects.create(address="192.168.1.1/31")
        self.ipv6_ra = IPAddress.objects.create(address="2001:db8::100/127")
        self.ipv6_sp = IPAddress.objects.create(address="2001:db8::101/127")

    def test_create_interface_topology_ra_to_sp(self):
        """Test creating the complete interface topology between L3-TOR and L3-LEAF devices."""

        # Create DeviceInterface for ToR (id=1)
        device_interface_tor = DeviceInterface.objects.create(
            name="etp1",
            enabled=True,
            state=AssetStateChoices.STATE_PRODUCTION,
            monitoring_state=AssetMonitoringStateChoices.CRITICAL,
            device=self.device_tor,
            autonegotiation=True,
            speed=100000,
            fec="rs",
            description="TOR interface to LEAF",
        )

        # Create DeviceInterface for Leaf (id=2)
        device_interface_leaf = DeviceInterface.objects.create(
            name="etp3",
            enabled=True,
            state=AssetStateChoices.STATE_PRODUCTION,
            monitoring_state=AssetMonitoringStateChoices.CRITICAL,
            device=self.device_leaf,
            autonegotiation=True,
            speed=100000,
            description="LEAF interface to TOR",
        )

        # Create LogicalInterface for ToR (id=1)
        logical_interface_ra = LogicalInterface.objects.create(
            index=0,
            enabled=True,
            state=AssetStateChoices.STATE_PRODUCTION,
            monitoring_state=AssetMonitoringStateChoices.CRITICAL,
            parent_interface=device_interface_tor,
            mtu=9216,
            type="l3",
            vrf=self.vrf,
            ipv4_address=self.ipv4_ra,
            ipv6_address=self.ipv6_ra,
            mode="tagged",
            description="TOR logical interface to LEAF",
        )

        # Create LogicalInterface for Leaf (id=2)
        logical_interface_sp = LogicalInterface.objects.create(
            index=0,
            enabled=True,
            state=AssetStateChoices.STATE_PRODUCTION,
            monitoring_state=AssetMonitoringStateChoices.CRITICAL,
            parent_interface=device_interface_leaf,
            mtu=9216,
            type="l3",
            vrf=self.vrf,
            ipv4_address=self.ipv4_sp,
            ipv6_address=self.ipv6_sp,
            mode="tagged",
            description="LEAF logical interface to TOR",
        )

        # Create Link between the LogicalInterfaces
        link = Link.objects.create(
            interface_a=device_interface_tor,
            interface_b=device_interface_leaf,
            state=AssetStateChoices.STATE_PRODUCTION,
            monitoring_state=AssetMonitoringStateChoices.CRITICAL,
        )

        # Verify all objects were created successfully
        self.assertIsNotNone(device_interface_tor.id)
        self.assertIsNotNone(device_interface_leaf.id)
        self.assertIsNotNone(logical_interface_ra.id)
        self.assertIsNotNone(logical_interface_sp.id)
        self.assertIsNotNone(link.id)

        # Verify DeviceInterface configurations
        self.assertEqual(device_interface_tor.name, "etp1")
        self.assertEqual(device_interface_tor.speed, 100000)
        self.assertEqual(device_interface_tor.autonegotiation, True)
        self.assertEqual(device_interface_tor.device, self.device_tor)

        self.assertEqual(device_interface_leaf.name, "etp3")
        self.assertEqual(device_interface_leaf.speed, 100000)
        self.assertEqual(device_interface_leaf.autonegotiation, True)
        self.assertEqual(device_interface_leaf.device, self.device_leaf)

        # Verify LogicalInterface configurations
        self.assertEqual(logical_interface_ra.index, 0)
        self.assertEqual(logical_interface_ra.parent_interface, device_interface_tor)
        self.assertEqual(logical_interface_ra.mtu, 9216)
        self.assertEqual(logical_interface_ra.type, "l3")
        self.assertEqual(logical_interface_ra.vrf, self.vrf)
        self.assertEqual(logical_interface_ra.ipv4_address, self.ipv4_ra)
        self.assertEqual(logical_interface_ra.ipv6_address, self.ipv6_ra)

        self.assertEqual(logical_interface_sp.index, 0)
        self.assertEqual(logical_interface_sp.parent_interface, device_interface_leaf)
        self.assertEqual(logical_interface_sp.mtu, 9216)
        self.assertEqual(logical_interface_sp.type, "l3")
        self.assertEqual(logical_interface_sp.vrf, self.vrf)
        self.assertEqual(logical_interface_sp.ipv4_address, self.ipv4_sp)
        self.assertEqual(logical_interface_sp.ipv6_address, self.ipv6_sp)

        # Verify Link configuration
        self.assertEqual(link.interface_a, device_interface_tor)
        self.assertEqual(link.interface_b, device_interface_leaf)
        self.assertEqual(link.state, AssetStateChoices.STATE_PRODUCTION)

        # Verify string representations
        self.assertEqual(str(device_interface_tor), f"{self.device_tor.name}--etp1")
        self.assertEqual(str(device_interface_leaf), f"{self.device_leaf.name}--etp3")
        self.assertEqual(str(logical_interface_ra), f"{device_interface_tor.name}--0")
        self.assertEqual(str(logical_interface_sp), f"{device_interface_leaf.name}--0")
        self.assertEqual(str(link), f"{device_interface_tor} <--> {device_interface_leaf}")

        # Verify relationships
        self.assertEqual(device_interface_tor.device, self.device_tor)
        self.assertEqual(device_interface_leaf.device, self.device_leaf)
        self.assertEqual(logical_interface_ra.parent_interface, device_interface_tor)
        self.assertEqual(logical_interface_sp.parent_interface, device_interface_leaf)
        self.assertEqual(link.interface_a, device_interface_tor)
        self.assertEqual(link.interface_b, device_interface_leaf)
