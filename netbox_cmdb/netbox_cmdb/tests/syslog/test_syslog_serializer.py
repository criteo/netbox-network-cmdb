from netbox_cmdb.api.syslog.serializers import (
    SyslogSerializer,
    SyslogServerSerializer,
)
from netbox_cmdb.models.syslog import Syslog, SyslogServer
from netbox_cmdb.tests.common import BaseTestCase


class SyslogSerializerCreate(BaseTestCase):

    def test_create_syslog_server_and_assign_to_device(self):
        """
        Create SyslogServer with only server_address,
        then create Syslog and assign servers to devices.
        """

        # Create a SyslogServer
        server_data = {
            "server_address": "10.10.10.1",
        }

        server_serializer = SyslogServerSerializer(data=server_data)
        assert server_serializer.is_valid() is True
        server_serializer.save()

        server_obj = SyslogServer.objects.get(server_address="10.10.10.1")

        assert server_obj.server_address == "10.10.10.1"

        # Create Syslog entry for a device
        syslog_data = {
            "device": self.device1.pk,
            "server_list": [server_obj.pk],
        }

        syslog_serializer = SyslogSerializer(data=syslog_data)
        assert syslog_serializer.is_valid() is True
        syslog_serializer.save()

        syslog_obj = Syslog.objects.get(device=self.device1)

        assert syslog_obj.device == self.device1
        assert syslog_obj.server_list.count() == 1
        assert syslog_obj.server_list.first() == server_obj

        # Create a second SyslogServer
        server_data2 = {
            "server_address": "10.10.10.2",
        }

        server_serializer2 = SyslogServerSerializer(data=server_data2)
        assert server_serializer2.is_valid() is True
        server_serializer2.save()

        server_obj2 = SyslogServer.objects.get(server_address="10.10.10.2")

        # Assign two servers to a second device
        syslog_data2 = {
            "device": self.device2.pk,
            "server_list": [server_obj.pk, server_obj2.pk],
        }

        syslog_serializer2 = SyslogSerializer(data=syslog_data2)
        assert syslog_serializer2.is_valid() is True
        syslog_serializer2.save()

        syslog_obj2 = Syslog.objects.get(device=self.device2)

        assert syslog_obj2.server_list.count() == 2
        assert server_obj in syslog_obj2.server_list.all()
        assert server_obj2 in syslog_obj2.server_list.all()
