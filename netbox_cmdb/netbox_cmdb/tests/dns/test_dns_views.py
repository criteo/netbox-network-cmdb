from django.urls import reverse
from utilities.testing import TestCase

from netbox_cmdb.forms import DNSForm
from netbox_cmdb.models.dns import DNS, DNSServer
from netbox_cmdb.tests.common import BaseTestCase


class DNSViewsTestCase(TestCase):
    """The plugin UI pages render and write DNS objects."""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        # Reuse the device fixtures of the serializer tests.
        BaseTestCase.setUp(self)

    def test_list_views_render(self):
        server = DNSServer.objects.create(server_address="10.0.0.123")
        DNS.objects.create(device=self.device1).server_list.set([server])

        for name in ("dns_list", "dnsserver_list"):
            response = self.client.get(reverse(f"plugins:netbox_cmdb:{name}"))
            self.assertHttpStatus(response, 200)
            self.assertContains(response, "10.0.0.123")

    def test_add_views_render(self):
        for name in ("dns_add", "dnsserver_add"):
            response = self.client.get(reverse(f"plugins:netbox_cmdb:{name}"))
            self.assertHttpStatus(response, 200)

    def test_create_server_through_the_ui(self):
        response = self.client.post(
            reverse("plugins:netbox_cmdb:dnsserver_add"),
            {"name": "dns1.example.com", "server_address": "10.0.0.123"},
        )

        self.assertHttpStatus(response, 302)
        assert DNSServer.objects.get(server_address="10.0.0.123").name == "dns1.example.com"

    def test_list_views_show_the_server_name(self):
        server = DNSServer.objects.create(name="dns1.example.com", server_address="10.0.0.123")
        DNS.objects.create(device=self.device1).server_list.set([server])

        for name in ("dns_list", "dnsserver_list"):
            response = self.client.get(reverse(f"plugins:netbox_cmdb:{name}"))
            self.assertHttpStatus(response, 200)
            self.assertContains(response, "dns1.example.com")

    def test_form_links_a_device_to_several_servers(self):
        first = DNSServer.objects.create(server_address="10.0.0.123")
        second = DNSServer.objects.create(server_address="10.0.0.124")

        form = DNSForm(data={"device": self.device1.pk, "server_list": [first.pk, second.pk]})
        assert form.is_valid() is True, form.errors
        dns = form.save()

        assert set(dns.server_list.all()) == {first, second}

    def test_form_rejects_a_second_configuration_for_a_device(self):
        """One DNS configuration per device, servers are added to its server_list."""
        DNS.objects.create(device=self.device1)

        form = DNSForm(data={"device": self.device1.pk, "server_list": []})
        assert form.is_valid() is False
        assert "device" in form.errors

    def test_delete_view(self):
        dns = DNS.objects.create(device=self.device1)

        response = self.client.post(
            reverse("plugins:netbox_cmdb:dns_delete", kwargs={"pk": dns.pk}), {"confirm": True}
        )

        self.assertHttpStatus(response, 302)
        assert DNS.objects.filter(pk=dns.pk).exists() is False

    def test_form_rejects_more_than_three_servers(self):
        servers = [DNSServer.objects.create(server_address=f"10.0.0.{i}") for i in range(1, 5)]

        form = DNSForm(data={"device": self.device1.pk, "server_list": [s.pk for s in servers]})
        assert form.is_valid() is False
        assert "server_list" in form.errors
