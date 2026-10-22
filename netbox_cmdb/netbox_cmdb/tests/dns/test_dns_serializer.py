from netbox_cmdb.api.dns.serializers import DNSSerializer, DNSServerSerializer
from netbox_cmdb.models.dns import DNS, DNSServer
from netbox_cmdb.tests.common import BaseTestCase


class DNSSerializerCreate(BaseTestCase):

    def test_create_and_update_dns_servers(self):
        """
        Test creating DNSServers and assigning them to devices,
        including updating server_list for existing DNS.
        """

        # --- Create DNSServer 1 ---
        server_data1 = {"server_address": "10.10.10.1"}
        server_serializer1 = DNSServerSerializer(data=server_data1)
        assert server_serializer1.is_valid() is True
        server_serializer1.save()
        server1 = DNSServer.objects.get(server_address="10.10.10.1")

        # --- Create DNSServer 2 ---
        server_data2 = {"server_address": "10.10.10.2"}
        server_serializer2 = DNSServerSerializer(data=server_data2)
        assert server_serializer2.is_valid() is True
        server_serializer2.save()
        server2 = DNSServer.objects.get(server_address="10.10.10.2")

        # --- Create DNS for device1 using device ID ---
        dns_data1 = {"device": {"id": self.device1.pk}, "server_list": [server1.pk]}
        dns_serializer1 = DNSSerializer(data=dns_data1)
        assert dns_serializer1.is_valid() is True
        dns_serializer1.save()
        dns_obj1 = DNS.objects.get(device=self.device1)

        assert dns_obj1.device == self.device1
        assert dns_obj1.server_list.count() == 1
        assert dns_obj1.server_list.first() == server1

        # --- Create DNS for device2 using device ID with 2 servers ---
        dns_data2 = {"device": {"id": self.device2.pk}, "server_list": [server1.pk, server2.pk]}
        dns_serializer2 = DNSSerializer(data=dns_data2)
        assert dns_serializer2.is_valid() is True
        dns_serializer2.save()
        dns_obj2 = DNS.objects.get(device=self.device2)

        assert dns_obj2.server_list.count() == 2
        assert server1 in dns_obj2.server_list.all()
        assert server2 in dns_obj2.server_list.all()

        # --- Update existing DNS for device2 using device name ---
        dns_data_update = {"device": {"name": "router-test2"}, "server_list": [server1.pk]}
        # Get existing DNS instance
        dns_obj2 = DNS.objects.get(device=self.device2)
        dns_serializer_update = DNSSerializer(instance=dns_obj2, data=dns_data_update)
        assert dns_serializer_update.is_valid() is True
        dns_serializer_update.save()
        dns_obj2.refresh_from_db()

        assert dns_obj2.device == self.device2
        assert dns_obj2.server_list.count() == 1
        assert dns_obj2.server_list.first() == server1

    def test_upsert_without_server_list_preserves_the_servers(self):
        """A POST acts as an upsert: omitting server_list must not wipe an existing one."""

        server = DNSServer.objects.create(server_address="10.10.10.10")
        created = DNSSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [server.pk]}
        )
        assert created.is_valid() is True
        created.save()

        # Same device, no server_list: this goes through create() thanks to get_or_create().
        upserted = DNSSerializer(data={"device": {"id": self.device1.pk}})
        assert upserted.is_valid() is True
        dns = upserted.save()

        assert list(dns.server_list.all()) == [server]

    def test_upsert_with_a_server_list_replaces_the_servers(self):
        """When server_list is provided, it stays authoritative."""

        first = DNSServer.objects.create(server_address="10.10.10.10")
        second = DNSServer.objects.create(server_address="10.10.10.11")
        DNS.objects.create(device=self.device1).server_list.set([first])

        upserted = DNSSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [second.pk]}
        )
        assert upserted.is_valid() is True
        dns = upserted.save()

        assert list(dns.server_list.all()) == [second]

    def test_update_without_server_list_preserves_the_servers(self):
        """The PATCH path keeps the same rule as the POST one."""

        server = DNSServer.objects.create(server_address="10.10.10.10")
        dns = DNS.objects.create(device=self.device1)
        dns.server_list.set([server])

        updated = DNSSerializer(
            instance=dns, data={"device": {"id": self.device1.pk}}, partial=True
        )
        assert updated.is_valid() is True
        updated.save()
        dns.refresh_from_db()

        assert list(dns.server_list.all()) == [server]

    def test_dropping_a_server_from_a_list_keeps_the_server(self):
        """server_list only holds references: replacing it must not delete any server."""

        first = DNSServer.objects.create(server_address="10.10.10.10")
        second = DNSServer.objects.create(server_address="10.10.10.11")
        dns = DNS.objects.create(device=self.device1)
        dns.server_list.set([first, second])

        updated = DNSSerializer(
            instance=dns,
            data={"device": {"id": self.device1.pk}, "server_list": [second.pk]},
        )
        assert updated.is_valid() is True
        updated.save()

        assert list(dns.server_list.all()) == [second]
        assert DNSServer.objects.filter(pk=first.pk).exists() is True

    def test_duplicate_server_addresses_are_rejected(self):
        """SONiC keys DNS_NAMESERVER by address, it cannot be stored twice."""

        DNSServer.objects.create(server_address="10.10.10.1")
        serializer = DNSServerSerializer(data={"server_address": "10.10.10.1"})
        assert serializer.is_valid() is False
        assert "server_address" in serializer.errors

    def test_a_server_can_be_shared_by_several_devices(self):
        """The unique address is a global constraint, not a per-device one."""

        server = DNSServer.objects.create(server_address="10.10.10.1")

        for device in (self.device1, self.device2):
            serializer = DNSSerializer(
                data={"device": {"id": device.pk}, "server_list": [server.pk]}
            )
            assert serializer.is_valid() is True
            serializer.save()

        assert DNS.objects.get(device=self.device1).server_list.first() == server
        assert DNS.objects.get(device=self.device2).server_list.first() == server

    def test_server_name_is_optional(self):
        serializer = DNSServerSerializer(data={"server_address": "10.10.10.1"})
        assert serializer.is_valid() is True
        server = serializer.save()

        assert server.name == ""
        assert str(server) == "10.10.10.1"

    def test_server_name_is_stored_and_shown(self):
        serializer = DNSServerSerializer(
            data={"name": "dns1.example.com", "server_address": "10.10.10.1"}
        )
        assert serializer.is_valid() is True
        server = serializer.save()

        assert server.name == "dns1.example.com"
        assert str(server) == "dns1.example.com (10.10.10.1)"

    def test_server_name_is_not_unique(self):
        """SONiC identifies servers by address only, the name is a label."""

        DNSServer.objects.create(name="dns", server_address="10.10.10.1")
        serializer = DNSServerSerializer(data={"name": "dns", "server_address": "10.10.10.2"})

        assert serializer.is_valid() is True

    def test_at_most_three_servers_per_device(self):
        """SONiC's DNS_NAMESERVER table holds at most 3 entries."""

        servers = [DNSServer.objects.create(server_address=f"10.10.10.{i}") for i in range(1, 5)]

        accepted = DNSSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [s.pk for s in servers[:3]]}
        )
        assert accepted.is_valid() is True, accepted.errors

        rejected = DNSSerializer(
            data={"device": {"id": self.device2.pk}, "server_list": [s.pk for s in servers]}
        )
        assert rejected.is_valid() is False
        assert "server_list" in rejected.errors
