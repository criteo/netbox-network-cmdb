from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from netbox_cmdb.models import ManagementRoute
from netbox_cmdb.models.management_route import ManagementRouteKindChoices
from netbox_cmdb.tests.management_route.common import create_management_interface


class ManagementRouteModelTestCase(TestCase):
    def setUp(self):
        self.mgmt = create_management_interface()

    def _route(self, **kwargs):
        values = {
            "logical_interface": self.mgmt,
            "kind": ManagementRouteKindChoices.STATIC,
            "prefix": "0.0.0.0/0",
            "next_hop": "192.0.2.1",
        }
        values.update(kwargs)
        return ManagementRoute(**values)

    def test_static_default_route(self):
        route = self._route()
        route.full_clean()
        route.save()

        route.refresh_from_db()
        self.assertEqual(str(route.prefix), "0.0.0.0/0")
        self.assertEqual(str(route.next_hop), "192.0.2.1")
        self.assertEqual(route.device, self.mgmt.parent_interface.device)
        self.assertEqual(str(route), "router-test--mgmt0.0--static--0.0.0.0/0")

    def test_forced_route(self):
        route = self._route(
            kind=ManagementRouteKindChoices.FORCED, prefix="198.51.100.0/24", next_hop=None
        )
        route.full_clean()
        route.save()

        self.assertEqual(ManagementRoute.objects.get(kind="forced").next_hop, None)

    def test_static_route_requires_a_next_hop(self):
        with self.assertRaises(ValidationError) as ctx:
            self._route(next_hop=None).full_clean()
        self.assertIn("next_hop", ctx.exception.error_dict)

    def test_forced_route_has_no_next_hop(self):
        with self.assertRaises(ValidationError) as ctx:
            self._route(
                kind=ManagementRouteKindChoices.FORCED,
                prefix="198.51.100.0/24",
                next_hop="192.0.2.1",
            ).full_clean()
        self.assertIn("next_hop", ctx.exception.error_dict)

    def test_next_hop_must_be_in_the_interface_subnet(self):
        with self.assertRaises(ValidationError) as ctx:
            self._route(next_hop="10.0.0.1").full_clean()
        self.assertIn("must be in the subnet", str(ctx.exception.error_dict["next_hop"][0]))

    def test_next_hop_cannot_be_the_interface_address(self):
        with self.assertRaises(ValidationError) as ctx:
            self._route(next_hop="192.0.2.10").full_clean()
        self.assertIn("next_hop", ctx.exception.error_dict)

    def test_interface_without_ipv4_address_is_rejected(self):
        mgmt = create_management_interface(device_name="router-noip", address=None)
        with self.assertRaises(ValidationError) as ctx:
            self._route(logical_interface=mgmt).full_clean()
        self.assertIn("logical_interface", ctx.exception.error_dict)

    def test_ipv6_is_not_supported(self):
        with self.assertRaises(ValidationError) as ctx:
            self._route(prefix="::/0", next_hop="2001:db8::1").full_clean()
        self.assertIn("prefix", ctx.exception.error_dict)
        self.assertIn("next_hop", ctx.exception.error_dict)

    def test_duplicate_is_rejected(self):
        self._route().save()

        with self.assertRaises(ValidationError) as ctx:
            self._route(next_hop="192.0.2.2").full_clean()
        self.assertIn("already exists", str(ctx.exception))

        with transaction.atomic(), self.assertRaises(IntegrityError):
            self._route(next_hop="192.0.2.2").save()

    def test_updating_a_route_does_not_conflict_with_itself(self):
        route = self._route()
        route.save()

        route.next_hop = "192.0.2.2"
        route.full_clean()
        route.save()

        self.assertEqual(str(ManagementRoute.objects.get(pk=route.pk).next_hop), "192.0.2.2")

    def test_same_prefix_on_two_devices(self):
        other = create_management_interface(device_name="router-other", address="192.0.2.11/24")
        self._route().save()
        route = self._route(logical_interface=other)
        route.full_clean()
        route.save()

        self.assertEqual(ManagementRoute.objects.count(), 2)

    def test_routes_are_deleted_with_the_interface(self):
        self._route().save()
        self.mgmt.delete()
        self.assertEqual(ManagementRoute.objects.count(), 0)
