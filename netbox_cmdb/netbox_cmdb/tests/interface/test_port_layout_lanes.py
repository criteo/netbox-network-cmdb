from dcim.models import DeviceRole, DeviceType, Manufacturer
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from utilities.testing import APITestCase

from netbox_cmdb.api.interface.serializers import PortLayoutSerializer
from netbox_cmdb.models.interface import PortLayout


def full_layout():
    """32 ports of 4 lanes, the last 8 of them split into 4x1 or 2x2 lanes breakouts."""
    ports = {}
    for number in range(1, 33):
        lanes = list(range((number - 1) * 4, number * 4))
        if number <= 24:
            ports[f"etp{number}"] = lanes
        elif number % 2:
            for letter, lane in zip("abcd", lanes):
                ports[f"etp{number}{letter}"] = [lane]
        else:
            ports[f"etp{number}a"] = lanes[:2]
            ports[f"etp{number}b"] = lanes[2:]
    return ports


class PortLayoutLanesTestCase(TestCase):
    def setUp(self):
        manufacturer = Manufacturer.objects.create(name="Vendor", slug="vendor")
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Model", slug="model"
        )
        self.other_device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Other model", slug="other-model"
        )
        self.tor = DeviceRole.objects.create(name="ToR", slug="tor")
        self.spine = DeviceRole.objects.create(name="Spine", slug="spine")

    def build(self, name, lanes, device_type=None, network_role=None):
        return PortLayout(
            device_type=device_type or self.device_type,
            network_role=network_role or self.tor,
            name=name,
            label_name=name,
            logical_name=name,
            vendor_name=name,
            vendor_short_name=name,
            vendor_long_name=name,
            lanes=lanes,
        )

    def create(self, name, lanes, **kwargs):
        port = self.build(name, lanes, **kwargs)
        port.full_clean()
        port.save()
        return port

    def assertLaneError(self, port, message):
        with self.assertRaises(ValidationError) as context:
            port.full_clean()
        self.assertIn("lanes", context.exception.message_dict)
        self.assertTrue(
            any(message in error for error in context.exception.message_dict["lanes"]),
            context.exception.message_dict["lanes"],
        )

    def test_full_layout_is_valid(self):
        """Every port of a full layout with breakouts is accepted and renders back as is."""
        ports = full_layout()
        for name, lanes in ports.items():
            self.create(name, lanes)

        layout = PortLayout.objects.filter(device_type=self.device_type)
        self.assertEqual(layout.count(), len(ports))
        for name, lanes in ports.items():
            self.assertEqual(
                layout.get(name=name).lanes_display, ",".join(str(lane) for lane in lanes)
            )

    def test_lane_order_is_kept(self):
        """Lanes may start from 1 and be swapped by pair: etp1 is on 5-8."""
        self.create("etp1", [5, 6, 7, 8])
        self.create("etp2", [1, 2, 3, 4])
        self.create("etp3", [12, 11, 10, 9])

        self.assertEqual(PortLayout.objects.get(name="etp1").lanes, [5, 6, 7, 8])
        self.assertEqual(PortLayout.objects.get(name="etp2").lanes, [1, 2, 3, 4])
        self.assertEqual(PortLayout.objects.get(name="etp3").lanes_display, "12,11,10,9")

    def test_4x25g_breakout(self):
        """etp3 split in 4x25G: etp3a..etp3d each use one lane of 8-11."""
        for letter, lane in zip("abcd", range(8, 12)):
            self.create(f"etp3{letter}", [lane])

        self.assertLaneError(
            self.build("etp3", [8, 9, 10, 11]), "Lanes [8] are already used by etp3a."
        )

    def test_8_lanes_breakouts(self):
        """1x400G, 2x200G then 4x100G on the 8 lanes of a port."""
        port = self.create("etp1", list(range(8)))
        self.assertEqual(port.lanes, list(range(8)))
        port.delete()

        self.create("etp1a", [0, 1, 2, 3])
        self.create("etp1b", [4, 5, 6, 7])
        PortLayout.objects.filter(name__startswith="etp1").delete()

        for letter, first_lane in zip("abcd", range(0, 8, 2)):
            self.create(f"etp1{letter}", [first_lane, first_lane + 1])
        self.assertEqual(PortLayout.objects.filter(name__startswith="etp1").count(), 4)

    def test_breakout_ports_use_the_same_lane_count(self):
        self.create("etp1a", [0, 1, 2, 3])
        self.assertLaneError(
            self.build("etp1b", [4, 5]),
            "Breakout ports of etp1 must use the same number of lanes: etp1a uses 4, got 2.",
        )
        self.assertLaneError(
            self.build("ETP1B", [4, 5]), "Breakout ports of etp1 must use the same number"
        )

    def test_breakout_siblings_are_matched_on_the_parent_name(self):
        """etp10a is not a sibling of etp1a, nor is etp1 a breakout port."""
        self.create("etp1a", [0, 1])
        self.create("etp10a", [80, 81, 82, 83])
        self.create("etp1", [8, 9, 10, 11])

    def test_ports_without_lanes(self):
        """Existing ports have no lanes, they must stay valid and never collide."""
        port = PortLayout.objects.create(
            device_type=self.device_type,
            network_role=self.tor,
            name="etp1",
            label_name="1",
            logical_name="to_leaf_01",
            vendor_name="1",
            vendor_short_name="etp1",
            vendor_long_name="Ethernet0",
        )
        self.assertEqual(port.lanes, [])
        self.assertEqual(port.lanes_display, "")
        port.full_clean()

        self.create("etp2", [])
        self.create("etp3a", [16])
        self.create("etp3b", [])

    def test_overlapping_lanes(self):
        self.create("etp1", [0, 1, 2, 3])
        self.create("etp2", [4, 5, 6, 7])
        self.assertLaneError(
            self.build("etp3", [2, 3, 4, 5]), "Lanes [2, 3] are already used by etp1."
        )
        self.assertLaneError(
            self.build("etp3", [2, 3, 4, 5]), "Lanes [4, 5] are already used by etp2."
        )

    def test_lanes_are_unique_per_layout(self):
        """Another network role or hardware is another layout, it can reuse the lanes."""
        self.create("etp1", [0, 1, 2, 3])
        self.create("etp1", [0, 1, 2, 3], network_role=self.spine)
        self.create("etp1", [0, 1, 2, 3], device_type=self.other_device_type)

    def test_updating_a_port_keeps_its_lanes(self):
        port = self.create("etp1", [0, 1, 2, 3])
        port.logical_name = "to_spine_01"
        port.full_clean()
        port.save()

    def test_non_contiguous_lanes(self):
        for lanes in ([0, 1, 4, 5], [0, 2], [7, 5, 6, 3]):
            with self.subTest(lanes=lanes):
                self.assertLaneError(
                    self.build("etp1", lanes), f"Lanes must be contiguous, got {sorted(lanes)}."
                )

    def test_duplicated_lanes(self):
        self.assertLaneError(self.build("etp1", [0, 1, 1, 0]), "Lanes used more than once: [0, 1].")

    def test_lane_count(self):
        for lanes in ([0, 1, 2], list(range(16))):
            with self.subTest(lanes=lanes):
                self.assertLaneError(
                    self.build("etp1", lanes),
                    f"A port must use 1, 2, 4 or 8 lanes, got {len(lanes)}.",
                )


class PortLayoutLanesSurfacesTestCase(TestCase):
    """The API enforces the same lane rules as the model."""

    def setUp(self):
        manufacturer = Manufacturer.objects.create(name="Vendor", slug="vendor")
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Model", slug="model"
        )
        self.tor = DeviceRole.objects.create(name="ToR", slug="tor")
        self.etp1 = PortLayout.objects.create(
            device_type=self.device_type,
            network_role=self.tor,
            name="etp1",
            label_name="1",
            logical_name="to_leaf_01",
            vendor_name="1",
            vendor_short_name="etp1",
            vendor_long_name="Ethernet0",
            lanes=[0, 1, 2, 3],
        )

    def data(self, **kwargs):
        return {
            "device_type": {"id": self.device_type.pk},
            "network_role": {"id": self.tor.pk},
            "name": "etp2",
            "label_name": "2",
            "logical_name": "to_leaf_02",
            "vendor_name": "2",
            "vendor_short_name": "etp2",
            "vendor_long_name": "Ethernet4",
            **kwargs,
        }

    def test_serializer_create(self):
        serializer = PortLayoutSerializer(data=self.data(lanes=[4, 5, 6, 7]))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        port = serializer.save()
        self.assertEqual(port.lanes, [4, 5, 6, 7])
        context = {"request": APIRequestFactory().get("/")}
        self.assertEqual(PortLayoutSerializer(port, context=context).data["lanes"], [4, 5, 6, 7])

    def test_serializer_create_without_lanes(self):
        serializer = PortLayoutSerializer(data=self.data())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.save().lanes, [])

    def test_serializer_rejects_overlapping_lanes(self):
        serializer = PortLayoutSerializer(data=self.data(lanes=[3, 4, 5, 6]))
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            [str(error) for error in serializer.errors["lanes"]],
            ["Lanes [3] are already used by etp1."],
        )

    def test_serializer_partial_update(self):
        serializer = PortLayoutSerializer(self.etp1, data={"logical_name": "x"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        etp2 = PortLayoutSerializer(data=self.data(lanes=[4, 5, 6, 7]))
        self.assertTrue(etp2.is_valid(), etp2.errors)
        etp2 = etp2.save()
        serializer = PortLayoutSerializer(etp2, data={"lanes": [0, 1, 2, 3]}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("lanes", serializer.errors)


class PortLayoutLanesAPITestCase(APITestCase):
    user_permissions = (
        "netbox_cmdb.view_portlayout",
        "netbox_cmdb.add_portlayout",
        "netbox_cmdb.change_portlayout",
    )

    def setUp(self):
        super().setUp()
        manufacturer = Manufacturer.objects.create(name="Vendor", slug="vendor")
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Model", slug="model"
        )
        self.tor = DeviceRole.objects.create(name="ToR", slug="tor")
        self.url = reverse("plugins-api:netbox_cmdb-api:portlayout-list")

    def post(self, name, lanes):
        data = {
            "device_type": {"id": self.device_type.pk},
            "network_role": {"id": self.tor.pk},
            "name": name,
            "label_name": name,
            "logical_name": name,
            "vendor_name": name,
            "vendor_short_name": name,
            "vendor_long_name": name,
            "lanes": lanes,
        }
        return self.client.post(self.url, data, format="json", **self.header)

    def test_create_and_reject_overlap(self):
        response = self.post("etp1", [0, 1, 2, 3])
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["lanes"], [0, 1, 2, 3])

        response = self.post("etp2", [3, 4, 5, 6])
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["lanes"], ["Lanes [3] are already used by etp1."])
