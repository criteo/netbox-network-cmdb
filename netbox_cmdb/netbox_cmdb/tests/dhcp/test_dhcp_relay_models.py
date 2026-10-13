from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from utilities.testing import APITestCase

from netbox_cmdb.models.dhcp import DhcpRelayInterface, DhcpServer
from netbox_cmdb.tests.dhcp.common import create_logical_interface


class DhcpRelayInterfaceModelTestCase(APITestCase):

    def setUp(self):
        super().setUp()
        self.l3 = create_logical_interface()
        self.l2 = create_logical_interface(device_name="router-l2", port="Ethernet20", type="l2")

    def test_server_address_is_unique(self):
        DhcpServer.objects.create(server_address="10.1.8.67")
        with self.assertRaises(IntegrityError), transaction.atomic():
            DhcpServer.objects.create(server_address="10.1.8.67")

    def test_relay_on_a_l3_interface(self):
        relay = DhcpRelayInterface(logical_interface=self.l3)
        relay.full_clean()
        relay.save()
        self.assertEqual(str(relay), "router-test--Ethernet10.0--DhcpRelay")
        self.assertEqual(relay.device, self.l3.parent_interface.device)

    def test_relay_refused_on_a_non_l3_interface(self):
        with self.assertRaises(ValidationError) as raised:
            DhcpRelayInterface(logical_interface=self.l2).full_clean()
        self.assertIn("logical_interface", raised.exception.message_dict)

    def test_one_relay_per_logical_interface(self):
        DhcpRelayInterface.objects.create(logical_interface=self.l3)
        with self.assertRaises(IntegrityError), transaction.atomic():
            DhcpRelayInterface.objects.create(logical_interface=self.l3)

    def test_relay_is_deleted_with_its_logical_interface(self):
        DhcpRelayInterface.objects.create(logical_interface=self.l3)
        self.l3.delete()
        self.assertFalse(DhcpRelayInterface.objects.exists())

    def test_deleting_a_relay_keeps_the_servers(self):
        relay = DhcpRelayInterface.objects.create(logical_interface=self.l3)
        relay.server_list.add(DhcpServer.objects.create(server_address="10.1.8.67"))
        relay.delete()
        self.assertTrue(DhcpServer.objects.filter(server_address="10.1.8.67").exists())

    def test_logical_interface_keeps_its_l3_type_while_a_relay_is_set(self):
        DhcpRelayInterface.objects.create(logical_interface=self.l3)
        self.l3.refresh_from_db()
        self.l3.type = "l2"
        with self.assertRaises(ValidationError):
            self.l3.save()
