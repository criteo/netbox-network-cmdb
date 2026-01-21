from netbox_cmdb.api.tacacs.serializers import (
    TacacsSerializer,
    TacacsServerSerializer,
)
from netbox_cmdb.models.tacacs import Tacacs, TacacsServer
from netbox_cmdb.tests.common import BaseTestCase


class TacacsSerializerCreate(BaseTestCase):

    def test_create_and_update_tacacs_servers(self):
        """
        Test creating TacacsServers and assigning them to devices,
        including updating server_list for existing Tacacs.
        """

        # --- Create TacacsServer 1 ---
        server_data1 = {
            "server_address": "10.20.20.1",
            "priority": 1,
            "tcp_port": 49,
        }
        server_serializer1 = TacacsServerSerializer(data=server_data1)
        assert server_serializer1.is_valid() is True
        server_serializer1.save()
        server1 = TacacsServer.objects.get(server_address="10.20.20.1")

        # --- Create TacacsServer 2 ---
        server_data2 = {
            "server_address": "10.20.20.2",
            "priority": 2,
            "tcp_port": 49,
        }
        server_serializer2 = TacacsServerSerializer(data=server_data2)
        assert server_serializer2.is_valid() is True
        server_serializer2.save()
        server2 = TacacsServer.objects.get(server_address="10.20.20.2")

        # --- Create Tacacs for device1 using device ID ---
        tacacs_data1 = {
            "device": {"id": self.device1.pk},
            "passkey": "secret-device1",
            "server_list": [server1.pk],
        }
        tacacs_serializer1 = TacacsSerializer(data=tacacs_data1)
        assert tacacs_serializer1.is_valid() is True
        tacacs_serializer1.save()
        tacacs_obj1 = Tacacs.objects.get(device=self.device1)

        assert tacacs_obj1.device == self.device1
        assert tacacs_obj1.passkey == "secret-device1"
        assert tacacs_obj1.server_list.count() == 1
        assert tacacs_obj1.server_list.first() == server1

        # --- Create Tacacs for device2 using device ID with 2 servers ---
        tacacs_data2 = {
            "device": {"id": self.device2.pk},
            "passkey": "secret-device2",
            "server_list": [server1.pk, server2.pk],
        }
        tacacs_serializer2 = TacacsSerializer(data=tacacs_data2)
        assert tacacs_serializer2.is_valid() is True
        tacacs_serializer2.save()
        tacacs_obj2 = Tacacs.objects.get(device=self.device2)

        assert tacacs_obj2.server_list.count() == 2
        assert server1 in tacacs_obj2.server_list.all()
        assert server2 in tacacs_obj2.server_list.all()

        # --- Update existing Tacacs for device2 using device name ---
        tacacs_data_update = {
            "device": {"name": "router-test2"},
            "passkey": "secret-updated",
            "server_list": [server1.pk],
        }

        # Get existing Tacacs instance
        tacacs_obj2 = Tacacs.objects.get(device=self.device2)
        tacacs_serializer_update = TacacsSerializer(
            instance=tacacs_obj2,
            data=tacacs_data_update,
        )
        assert tacacs_serializer_update.is_valid() is True
        tacacs_serializer_update.save()
        tacacs_obj2.refresh_from_db()

        assert tacacs_obj2.device == self.device2
        assert tacacs_obj2.passkey == "secret-updated"
        assert tacacs_obj2.server_list.count() == 1
        assert tacacs_obj2.server_list.first() == server1
