from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.models.ntp import NTP, NTPServer


class NTPAPITestCase(APITestCase):
    """Exercise the NTP endpoints end to end, through the router and the viewsets."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="model-test", slug="model-test"
        )
        device_role = DeviceRole.objects.create(name="role-test", slug="role-test")
        cls.device1 = Device.objects.create(
            name="router-test1", device_role=device_role, device_type=device_type, site=site
        )
        cls.device2 = Device.objects.create(
            name="router-test2", device_role=device_role, device_type=device_type, site=site
        )

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        self.ntp_url = reverse("plugins-api:netbox_cmdb-api:ntp-list")
        self.server_url = reverse("plugins-api:netbox_cmdb-api:ntpserver-list")

    def test_create_server(self):
        response = self.client.post(
            self.server_url, {"server_address": "10.0.0.123"}, format="json", **self.header
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        assert NTPServer.objects.filter(server_address="10.0.0.123").exists() is True

    def test_create_server_with_a_name(self):
        response = self.client.post(
            self.server_url,
            {"name": "ntp1.example.com", "server_address": "10.0.0.123"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        assert NTPServer.objects.get(server_address="10.0.0.123").name == "ntp1.example.com"

    def test_filter_servers_by_name(self):
        NTPServer.objects.create(name="ntp1", server_address="10.0.0.123")
        NTPServer.objects.create(name="ntp2", server_address="10.0.0.124")

        response = self.client.get(f"{self.server_url}?name=ntp2", format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        assert [s["server_address"] for s in response.data["results"]] == ["10.0.0.124"]

    def test_create_duplicate_server_is_rejected(self):
        NTPServer.objects.create(server_address="10.0.0.123")

        response = self.client.post(
            self.server_url, {"server_address": "10.0.0.123"}, format="json", **self.header
        )

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_link_a_device_to_several_servers(self):
        first = NTPServer.objects.create(server_address="10.0.0.123")
        second = NTPServer.objects.create(server_address="2001:db8::123")

        response = self.client.post(
            self.ntp_url,
            {"device": {"name": self.device1.name}, "server_list": [first.pk, second.pk]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        ntp = NTP.objects.get(device=self.device1)
        assert set(ntp.server_list.all()) == {first, second}

    def test_read_nests_the_servers(self):
        server = NTPServer.objects.create(name="ntp1", server_address="10.0.0.123")
        ntp = NTP.objects.create(device=self.device1)
        ntp.server_list.set([server])

        response = self.client.get(
            reverse("plugins-api:netbox_cmdb-api:ntp-detail", kwargs={"pk": ntp.pk}),
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        assert response.data["device"]["name"] == self.device1.name
        assert [(s["name"], s["server_address"]) for s in response.data["server_list"]] == [
            ("ntp1", "10.0.0.123")
        ]

    def test_filter_by_device_name(self):
        server = NTPServer.objects.create(server_address="10.0.0.123")
        for device in (self.device1, self.device2):
            NTP.objects.create(device=device).server_list.set([server])

        response = self.client.get(
            f"{self.ntp_url}?device__name={self.device2.name}", format="json", **self.header
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        assert [r["device"]["name"] for r in response.data["results"]] == [self.device2.name]

    def test_patch_replaces_the_servers(self):
        first = NTPServer.objects.create(server_address="10.0.0.123")
        second = NTPServer.objects.create(server_address="10.0.0.124")
        ntp = NTP.objects.create(device=self.device1)
        ntp.server_list.set([first])

        response = self.client.patch(
            reverse("plugins-api:netbox_cmdb-api:ntp-detail", kwargs={"pk": ntp.pk}),
            {"server_list": [second.pk]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_200_OK)
        assert list(ntp.server_list.all()) == [second]

    def test_delete_configuration_keeps_the_servers(self):
        server = NTPServer.objects.create(server_address="10.0.0.123")
        ntp = NTP.objects.create(device=self.device1)
        ntp.server_list.set([server])

        response = self.client.delete(
            reverse("plugins-api:netbox_cmdb-api:ntp-detail", kwargs={"pk": ntp.pk}),
            **self.header,
        )

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        assert NTP.objects.filter(pk=ntp.pk).exists() is False
        assert NTPServer.objects.filter(pk=server.pk).exists() is True
