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
