from netbox_cmdb.api.syslog.serializers import SyslogSerializer, SyslogServerSerializer
from netbox_cmdb.models.syslog import Syslog, SyslogServer
from netbox_cmdb.tests.common import BaseTestCase


class SyslogSerializerCreate(BaseTestCase):

    def test_create_and_update_syslog_servers(self):
        """
        Test creating SyslogServers and assigning them to devices,
        including updating server_list for existing Syslog.
        """

        # --- Create SyslogServer 1 ---
        server_data1 = {"server_address": "10.10.10.1"}
        server_serializer1 = SyslogServerSerializer(data=server_data1)
        assert server_serializer1.is_valid() is True
        server_serializer1.save()
        server1 = SyslogServer.objects.get(server_address="10.10.10.1")

        # --- Create SyslogServer 2 ---
        server_data2 = {"server_address": "10.10.10.2"}
        server_serializer2 = SyslogServerSerializer(data=server_data2)
        assert server_serializer2.is_valid() is True
        server_serializer2.save()
        server2 = SyslogServer.objects.get(server_address="10.10.10.2")

        # --- Create Syslog for device1 using device ID ---
        syslog_data1 = {"device": {"id": self.device1.pk}, "server_list": [server1.pk]}
        syslog_serializer1 = SyslogSerializer(data=syslog_data1)
        assert syslog_serializer1.is_valid() is True
        syslog_serializer1.save()
        syslog_obj1 = Syslog.objects.get(device=self.device1)

        assert syslog_obj1.device == self.device1
        assert syslog_obj1.server_list.count() == 1
        assert syslog_obj1.server_list.first() == server1

        # --- Create Syslog for device2 using device ID with 2 servers ---
        syslog_data2 = {"device": {"id": self.device2.pk}, "server_list": [server1.pk, server2.pk]}
        syslog_serializer2 = SyslogSerializer(data=syslog_data2)
        assert syslog_serializer2.is_valid() is True
        syslog_serializer2.save()
        syslog_obj2 = Syslog.objects.get(device=self.device2)

        assert syslog_obj2.server_list.count() == 2
        assert server1 in syslog_obj2.server_list.all()
        assert server2 in syslog_obj2.server_list.all()

        # --- Update existing Syslog for device2 using device name ---
        syslog_data_update = {"device": {"name": "router-test2"}, "server_list": [server1.pk]}
        # Get existing Syslog instance
        syslog_obj2 = Syslog.objects.get(device=self.device2)
        syslog_serializer_update = SyslogSerializer(instance=syslog_obj2, data=syslog_data_update)
        assert syslog_serializer_update.is_valid() is True
        syslog_serializer_update.save()
        syslog_obj2.refresh_from_db()

        assert syslog_obj2.device == self.device2
        assert syslog_obj2.server_list.count() == 1
        assert syslog_obj2.server_list.first() == server1

    def test_upsert_without_server_list_preserves_the_servers(self):
        """A POST acts as an upsert: omitting server_list must not wipe an existing one."""

        server = SyslogServer.objects.create(server_address="10.10.10.10")
        created = SyslogSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [server.pk]}
        )
        assert created.is_valid() is True
        created.save()

        # Same device, no server_list: this goes through create() thanks to get_or_create().
        upserted = SyslogSerializer(data={"device": {"id": self.device1.pk}})
        assert upserted.is_valid() is True
        syslog = upserted.save()

        assert list(syslog.server_list.all()) == [server]

    def test_upsert_with_a_server_list_replaces_the_servers(self):
        """When server_list is provided, it stays authoritative."""

        first = SyslogServer.objects.create(server_address="10.10.10.10")
        second = SyslogServer.objects.create(server_address="10.10.10.11")
        Syslog.objects.create(device=self.device1).server_list.set([first])

        upserted = SyslogSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [second.pk]}
        )
        assert upserted.is_valid() is True
        syslog = upserted.save()

        assert list(syslog.server_list.all()) == [second]

    def test_update_without_server_list_preserves_the_servers(self):
        """The PATCH path keeps the same rule as the POST one."""

        server = SyslogServer.objects.create(server_address="10.10.10.10")
        syslog = Syslog.objects.create(device=self.device1)
        syslog.server_list.set([server])

        updated = SyslogSerializer(
            instance=syslog, data={"device": {"id": self.device1.pk}}, partial=True
        )
        assert updated.is_valid() is True
        updated.save()
        syslog.refresh_from_db()

        assert list(syslog.server_list.all()) == [server]

    def test_dropping_a_server_from_a_list_keeps_the_server(self):
        """server_list only holds references: replacing it must not delete any server."""

        first = SyslogServer.objects.create(server_address="10.10.10.10")
        second = SyslogServer.objects.create(server_address="10.10.10.11")
        syslog = Syslog.objects.create(device=self.device1)
        syslog.server_list.set([first, second])

        updated = SyslogSerializer(
            instance=syslog,
            data={"device": {"id": self.device1.pk}, "server_list": [second.pk]},
        )
        assert updated.is_valid() is True
        updated.save()

        assert list(syslog.server_list.all()) == [second]
        assert SyslogServer.objects.filter(pk=first.pk).exists() is True

    def test_duplicate_server_addresses_are_rejected(self):
        """SONiC keys SYSLOG_SERVER by address, it cannot be stored twice."""

        SyslogServer.objects.create(server_address="10.10.10.1")
        serializer = SyslogServerSerializer(data={"server_address": "10.10.10.1"})
        assert serializer.is_valid() is False
        assert "server_address" in serializer.errors

    def test_a_server_can_be_shared_by_several_devices(self):
        """The unique address is a global constraint, not a per-device one."""

        server = SyslogServer.objects.create(server_address="10.10.10.1")

        for device in (self.device1, self.device2):
            serializer = SyslogSerializer(
                data={"device": {"id": device.pk}, "server_list": [server.pk]}
            )
            assert serializer.is_valid() is True
            serializer.save()

        assert Syslog.objects.get(device=self.device1).server_list.first() == server
        assert Syslog.objects.get(device=self.device2).server_list.first() == server
