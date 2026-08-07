from django.core.exceptions import ValidationError as DjangoValidationError

from netbox_cmdb.api.tacacs.serializers import (
    TacacsSerializer,
    TacacsServerSerializer,
)
from netbox_cmdb.forms import TacacsAdminForm, TacacsForm
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

    def test_passkey_too_short_is_rejected_by_the_api(self):
        """A passkey shorter than MIN_TACACS_PASSKEY_LENGTH must be refused."""

        serializer = TacacsSerializer(
            data={
                "device": {"id": self.device1.pk},
                "passkey": "short",
            }
        )
        assert serializer.is_valid() is False
        assert "passkey" in serializer.errors

    def test_passkey_can_be_omitted(self):
        """passkey is optional: omitting it must not trigger the length check."""

        serializer = TacacsSerializer(data={"device": {"id": self.device1.pk}})
        assert serializer.is_valid() is True

    def test_passkey_too_short_is_rejected_by_the_model(self):
        """Tacacs.clean() enforces the same rule for the plugin UI and the Django admin."""

        tacacs = Tacacs(device=self.device1, passkey="short")
        with self.assertRaises(DjangoValidationError) as ctx:
            tacacs.full_clean()
        assert "passkey" in ctx.exception.error_dict

    def test_upsert_without_server_list_preserves_the_servers(self):
        """A POST acts as an upsert: omitting server_list must not wipe an existing one."""

        server = TacacsServer.objects.create(server_address="10.10.10.10", priority=1)
        created = TacacsSerializer(
            data={
                "device": {"id": self.device1.pk},
                "passkey": "Passkey1",
                "server_list": [server.pk],
            }
        )
        assert created.is_valid() is True
        created.save()

        # Same device, passkey only: this goes through create() thanks to get_or_create().
        upserted = TacacsSerializer(data={"device": {"id": self.device1.pk}, "passkey": "Passkey2"})
        assert upserted.is_valid() is True
        tacacs = upserted.save()

        assert tacacs.passkey == "Passkey2"
        assert list(tacacs.server_list.all()) == [server]

    def test_upsert_with_a_server_list_replaces_the_servers(self):
        """When server_list is provided, it stays authoritative."""

        first = TacacsServer.objects.create(server_address="10.10.10.10", priority=1)
        second = TacacsServer.objects.create(server_address="10.10.10.11", priority=2)
        Tacacs.objects.create(device=self.device1).server_list.set([first])

        upserted = TacacsSerializer(
            data={"device": {"id": self.device1.pk}, "server_list": [second.pk]}
        )
        assert upserted.is_valid() is True
        tacacs = upserted.save()

        assert list(tacacs.server_list.all()) == [second]

    def test_duplicate_server_addresses_are_rejected(self):
        """An address identifies a single server, it cannot be stored twice."""

        TacacsServer.objects.create(server_address="10.20.20.1", priority=1, tcp_port=49)
        serializer = TacacsServerSerializer(
            data={"server_address": "10.20.20.1", "priority": 2, "tcp_port": 49}
        )
        assert serializer.is_valid() is False
        assert "server_address" in serializer.errors

    def test_duplicate_priorities_are_rejected_by_the_api(self):
        """Two servers of a same device sharing a priority leaves the failover undefined."""

        first = TacacsServer.objects.create(server_address="10.20.20.1", priority=1)
        second = TacacsServer.objects.create(server_address="10.20.20.2", priority=1)
        serializer = TacacsSerializer(
            data={
                "device": {"id": self.device1.pk},
                "server_list": [first.pk, second.pk],
            }
        )
        assert serializer.is_valid() is False
        assert "server_list" in serializer.errors

    def test_distinct_priorities_are_accepted_by_the_api(self):
        """The nominal SONiC case: one server per priority."""

        first = TacacsServer.objects.create(server_address="10.10.10.10", priority=1)
        second = TacacsServer.objects.create(server_address="10.10.10.11", priority=2)
        serializer = TacacsSerializer(
            data={
                "device": {"id": self.device1.pk},
                "server_list": [first.pk, second.pk],
            }
        )
        assert serializer.is_valid() is True

    def test_duplicate_priorities_are_rejected_by_the_forms(self):
        """Both ModelForm based surfaces enforce the rule the API enforces."""

        first = TacacsServer.objects.create(server_address="10.20.20.1", priority=1)
        second = TacacsServer.objects.create(server_address="10.20.20.2", priority=1)
        data = {
            "device": self.device1.pk,
            "server_list": [first.pk, second.pk],
        }

        for form_class in (TacacsForm, TacacsAdminForm):
            form = form_class(data=data)
            assert form.is_valid() is False, f"{form_class.__name__} should reject duplicates"
            assert "server_list" in form.errors
