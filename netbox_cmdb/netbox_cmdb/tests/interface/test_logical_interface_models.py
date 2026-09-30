from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from ipam.models import IPAddress
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.filtersets import LogicalInterfaceFilterSet
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

    def test_use_ipv6_link_local_only_defaults_to_false(self):
        device_interface = DeviceInterface.objects.get(name="etp1")
        logical_interface = LogicalInterface.objects.create(
            index=4, parent_interface=device_interface, type="l3"
        )
        self.assertFalse(logical_interface.use_ipv6_link_local_only)

    def test_use_ipv6_link_local_only_is_independent_of_ipv6_address(self):
        """The flag can be set with or without a global IPv6 address."""
        device_interface = DeviceInterface.objects.get(name="etp1")
        ipv6_address = IPAddress.objects.create(address="2001:db8::1/64")

        without_address = LogicalInterface.objects.create(
            index=5, parent_interface=device_interface, type="l3", use_ipv6_link_local_only=True
        )
        with_address = LogicalInterface.objects.create(
            index=6,
            parent_interface=device_interface,
            type="l3",
            ipv6_address=ipv6_address,
            use_ipv6_link_local_only=True,
        )
        for logical_interface in (without_address, with_address):
            logical_interface.refresh_from_db()
            self.assertTrue(logical_interface.use_ipv6_link_local_only)

    def test_filter_on_use_ipv6_link_local_only(self):
        device_interface = DeviceInterface.objects.get(name="etp1")
        link_local_only = LogicalInterface.objects.create(
            index=7, parent_interface=device_interface, type="l3", use_ipv6_link_local_only=True
        )
        LogicalInterface.objects.create(index=8, parent_interface=device_interface, type="l3")

        filterset = LogicalInterfaceFilterSet(
            {"use_ipv6_link_local_only": "true"}, queryset=LogicalInterface.objects.all()
        )
        self.assertEqual(list(filterset.qs), [link_local_only])


class LogicalInterfaceAPITestCase(APITestCase):
    user_permissions = (
        "netbox_cmdb.view_logicalinterface",
        "netbox_cmdb.add_logicalinterface",
        "netbox_cmdb.change_logicalinterface",
    )

    def setUp(self):
        super().setUp()
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device = Device.objects.create(
            name="router-test",
            device_role=DeviceRole.objects.create(name="role-test", slug="role-test"),
            device_type=DeviceType.objects.create(
                manufacturer=manufacturer, model="model-test", slug="model-test"
            ),
            site=site,
        )
        self.device_interface = DeviceInterface.objects.create(name="etp1", device=device)
        self.url = reverse("plugins-api:netbox_cmdb-api:logicalinterface-list")

    def test_use_ipv6_link_local_only(self):
        data = {"parent_interface": {"id": self.device_interface.pk}, "index": 1, "type": "l3"}
        response = self.client.post(self.url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertFalse(response.data["use_ipv6_link_local_only"])

        detail_url = reverse(
            "plugins-api:netbox_cmdb-api:logicalinterface-detail", args=[response.data["id"]]
        )
        response = self.client.patch(
            detail_url, {"use_ipv6_link_local_only": True}, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertTrue(response.data["use_ipv6_link_local_only"])
        self.assertTrue(LogicalInterface.objects.get().use_ipv6_link_local_only)
