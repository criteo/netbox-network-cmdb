from netbox_cmdb.api.ntp.serializers import NTPSerializer, NTPServerSerializer
from netbox_cmdb.models.ntp import NTP, NTPServer
from netbox_cmdb.tests.common import BaseTestCase


class NTPSerializerCreate(BaseTestCase):

    def test_create_and_update_ntp_servers(self):
        """
        Test creating NTPServers and assigning them to devices,
        including updating server_list for existing NTP.
        """

        # --- Create NTPServer 1 ---
        server_data1 = {"server_address": "10.10.10.1"}
        server_serializer1 = NTPServerSerializer(data=server_data1)
        assert server_serializer1.is_valid() is True
        server_serializer1.save()
        server1 = NTPServer.objects.get(server_address="10.10.10.1")

        # --- Create NTPServer 2 ---
        server_data2 = {"server_address": "10.10.10.2"}
        server_serializer2 = NTPServerSerializer(data=server_data2)
        assert server_serializer2.is_valid() is True
        server_serializer2.save()
        server2 = NTPServer.objects.get(server_address="10.10.10.2")

        # --- Create NTP for device1 using device ID ---
        ntp_data1 = {"device": {"id": self.device1.pk}, "server_list": [server1.pk]}
        ntp_serializer1 = NTPSerializer(data=ntp_data1)
        assert ntp_serializer1.is_valid() is True
        ntp_serializer1.save()
        ntp_obj1 = NTP.objects.get(device=self.device1)

        assert ntp_obj1.device == self.device1
        assert ntp_obj1.server_list.count() == 1
        assert ntp_obj1.server_list.first() == server1

        # --- Create NTP for device2 using device ID with 2 servers ---
        ntp_data2 = {"device": {"id": self.device2.pk}, "server_list": [server1.pk, server2.pk]}
        ntp_serializer2 = NTPSerializer(data=ntp_data2)
        assert ntp_serializer2.is_valid() is True
        ntp_serializer2.save()
        ntp_obj2 = NTP.objects.get(device=self.device2)

        assert ntp_obj2.server_list.count() == 2
        assert server1 in ntp_obj2.server_list.all()
        assert server2 in ntp_obj2.server_list.all()

        # --- Update existing NTP for device2 using device name ---
        ntp_data_update = {"device": {"name": "router-test2"}, "server_list": [server1.pk]}
        # Get existing NTP instance
        ntp_obj2 = NTP.objects.get(device=self.device2)
        ntp_serializer_update = NTPSerializer(instance=ntp_obj2, data=ntp_data_update)
        assert ntp_serializer_update.is_valid() is True
        ntp_serializer_update.save()
        ntp_obj2.refresh_from_db()

        assert ntp_obj2.device == self.device2
        assert ntp_obj2.server_list.count() == 1
        assert ntp_obj2.server_list.first() == server1

    def test_upsert_without_server_list_preserves_the_servers(self):
        """A POST acts as an upsert: omitting server_list must not wipe an existing one."""

        server = NTPServer.objects.create(server_address="10.10.10.10")
        created = NTPSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [server.pk]}
        )
        assert created.is_valid() is True
        created.save()

        # Same device, no server_list: this goes through create() thanks to get_or_create().
        upserted = NTPSerializer(data={"device": {"id": self.device1.pk}})
        assert upserted.is_valid() is True
        ntp = upserted.save()

        assert list(ntp.server_list.all()) == [server]

    def test_upsert_with_a_server_list_replaces_the_servers(self):
        """When server_list is provided, it stays authoritative."""

        first = NTPServer.objects.create(server_address="10.10.10.10")
        second = NTPServer.objects.create(server_address="10.10.10.11")
        NTP.objects.create(device=self.device1).server_list.set([first])

        upserted = NTPSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [second.pk]}
        )
        assert upserted.is_valid() is True
        ntp = upserted.save()

        assert list(ntp.server_list.all()) == [second]

    def test_update_without_server_list_preserves_the_servers(self):
        """The PATCH path keeps the same rule as the POST one."""

        server = NTPServer.objects.create(server_address="10.10.10.10")
        ntp = NTP.objects.create(device=self.device1)
        ntp.server_list.set([server])

        updated = NTPSerializer(
            instance=ntp, data={"device": {"id": self.device1.pk}}, partial=True
        )
        assert updated.is_valid() is True
        updated.save()
        ntp.refresh_from_db()

        assert list(ntp.server_list.all()) == [server]

    def test_dropping_a_server_from_a_list_keeps_the_server(self):
        """server_list only holds references: replacing it must not delete any server."""

        first = NTPServer.objects.create(server_address="10.10.10.10")
        second = NTPServer.objects.create(server_address="10.10.10.11")
        ntp = NTP.objects.create(device=self.device1)
        ntp.server_list.set([first, second])

        updated = NTPSerializer(
            instance=ntp,
            data={"device": {"id": self.device1.pk}, "server_list": [second.pk]},
        )
        assert updated.is_valid() is True
        updated.save()

        assert list(ntp.server_list.all()) == [second]
        assert NTPServer.objects.filter(pk=first.pk).exists() is True

    def test_duplicate_server_addresses_are_rejected(self):
        """SONiC keys NTP_SERVER by address, it cannot be stored twice."""

        NTPServer.objects.create(server_address="10.10.10.1")
        serializer = NTPServerSerializer(data={"server_address": "10.10.10.1"})
        assert serializer.is_valid() is False
        assert "server_address" in serializer.errors

    def test_a_server_can_be_shared_by_several_devices(self):
        """The unique address is a global constraint, not a per-device one."""

        server = NTPServer.objects.create(server_address="10.10.10.1")

        for device in (self.device1, self.device2):
            serializer = NTPSerializer(
                data={"device": {"id": device.pk}, "server_list": [server.pk]}
            )
            assert serializer.is_valid() is True
            serializer.save()

        assert NTP.objects.get(device=self.device1).server_list.first() == server
        assert NTP.objects.get(device=self.device2).server_list.first() == server

    def test_server_name_is_optional(self):
        serializer = NTPServerSerializer(data={"server_address": "10.10.10.1"})
        assert serializer.is_valid() is True
        server = serializer.save()

        assert server.name == ""
        assert str(server) == "10.10.10.1"

    def test_server_name_is_stored_and_shown(self):
        serializer = NTPServerSerializer(
            data={"name": "ntp1.example.com", "server_address": "10.10.10.1"}
        )
        assert serializer.is_valid() is True
        server = serializer.save()

        assert server.name == "ntp1.example.com"
        assert str(server) == "ntp1.example.com (10.10.10.1)"

    def test_server_name_is_not_unique(self):
        """SONiC identifies servers by address only, the name is a label."""

        NTPServer.objects.create(name="ntp", server_address="10.10.10.1")
        serializer = NTPServerSerializer(data={"name": "ntp", "server_address": "10.10.10.2"})

        assert serializer.is_valid() is True
