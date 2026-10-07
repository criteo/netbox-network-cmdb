from django.urls import reverse
from utilities.testing import TestCase

from netbox_cmdb.forms import NTPForm
from netbox_cmdb.models.ntp import NTP, NTPServer
from netbox_cmdb.tests.common import BaseTestCase


class NTPViewsTestCase(TestCase):
    """The plugin UI pages render and write NTP objects."""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        # Reuse the device fixtures of the serializer tests.
        BaseTestCase.setUp(self)

    def test_list_views_render(self):
        server = NTPServer.objects.create(server_address="10.0.0.123")
        NTP.objects.create(device=self.device1).server_list.set([server])

        for name in ("ntp_list", "ntpserver_list"):
            response = self.client.get(reverse(f"plugins:netbox_cmdb:{name}"))
            self.assertHttpStatus(response, 200)
            self.assertContains(response, "10.0.0.123")

    def test_add_views_render(self):
        for name in ("ntp_add", "ntpserver_add"):
            response = self.client.get(reverse(f"plugins:netbox_cmdb:{name}"))
            self.assertHttpStatus(response, 200)

    def test_create_server_through_the_ui(self):
        response = self.client.post(
            reverse("plugins:netbox_cmdb:ntpserver_add"),
            {"name": "ntp1.example.com", "server_address": "10.0.0.123"},
        )

        self.assertHttpStatus(response, 302)
        assert NTPServer.objects.get(server_address="10.0.0.123").name == "ntp1.example.com"

    def test_list_views_show_the_server_name(self):
        server = NTPServer.objects.create(name="ntp1.example.com", server_address="10.0.0.123")
        NTP.objects.create(device=self.device1).server_list.set([server])

        for name in ("ntp_list", "ntpserver_list"):
            response = self.client.get(reverse(f"plugins:netbox_cmdb:{name}"))
            self.assertHttpStatus(response, 200)
            self.assertContains(response, "ntp1.example.com")

    def test_form_links_a_device_to_several_servers(self):
        first = NTPServer.objects.create(server_address="10.0.0.123")
        second = NTPServer.objects.create(server_address="10.0.0.124")

        form = NTPForm(data={"device": self.device1.pk, "server_list": [first.pk, second.pk]})
        assert form.is_valid() is True, form.errors
        ntp = form.save()

        assert set(ntp.server_list.all()) == {first, second}

    def test_form_rejects_a_second_configuration_for_a_device(self):
        """One NTP configuration per device, servers are added to its server_list."""
        NTP.objects.create(device=self.device1)

        form = NTPForm(data={"device": self.device1.pk, "server_list": []})
        assert form.is_valid() is False
        assert "device" in form.errors

    def test_delete_view(self):
        ntp = NTP.objects.create(device=self.device1)

        response = self.client.post(
            reverse("plugins:netbox_cmdb:ntp_delete", kwargs={"pk": ntp.pk}), {"confirm": True}
        )

        self.assertHttpStatus(response, 302)
        assert NTP.objects.filter(pk=ntp.pk).exists() is False
