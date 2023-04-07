from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models.ip import IPAddress
from netaddr import IPNetwork
from rest_framework.exceptions import ErrorDetail
from tenancy.models.tenants import Tenant

from netbox_cmdb.api.bgp.serializers import BGPGlobalSerializer, BGPSessionSerializer
from netbox_cmdb.models.bgp import ASN, AfiSafi, BGPGlobal, BGPSession, DeviceBGPSession
from netbox_cmdb.models.bgp_community_list import BGPCommunityList, BGPCommunityListTerm
from netbox_cmdb.models.prefix_list import PrefixList, PrefixListTerm
from netbox_cmdb.models.route_policy import RoutePolicy, RoutePolicyTerm


class BaseTestCase(TestCase):
    def setUp(self):
        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="model-test", slug="model-test"
        )
        device_role = DeviceRole.objects.create(name="role-test", slug="role-test")
        self.device1 = Device.objects.create(
            name="router-test1",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )
        self.asn1 = ASN.objects.create(number="1", organization_name="router-test1")
        self.ip_address1 = IPAddress.objects.create(address="10.0.0.1/32")
        self.device2 = Device.objects.create(
            name="router-test2",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )
        self.asn2 = ASN.objects.create(number="2", organization_name="router-test2")
        self.ip_address2 = IPAddress.objects.create(address="10.0.0.2/32")
        self.tenant = Tenant.objects.create(name="tenant1", slug="tenant1")


class BGPGlobalSerializerCreate(BaseTestCase):
    def test_create(self):
        data = {
            "device": self.device1.pk,
            "local_asn": self.asn1.pk,
            "router_id": "192.0.2.1",
            "ebgp_administrative_distance": 20,
            "ibgp_administrative_distance": 170,
            "graceful_restart": True,
            "graceful_restart_time": 240,
            "ecmp": True,
            "ecmp_maximum_paths": 128,
        }
        bgp_global_serializer = BGPGlobalSerializer(data=data)
        assert bgp_global_serializer.is_valid() == True
        bgp_global_serializer.save()

        global_conf = BGPGlobal.objects.get(device__name="router-test1")

        assert global_conf.device_id == 5
        assert global_conf.local_asn_id == 5
        assert global_conf.ebgp_administrative_distance == 20
        assert global_conf.ibgp_administrative_distance == 170
        assert global_conf.graceful_restart == True
        assert global_conf.graceful_restart_time == 240
        assert global_conf.ecmp == True
        assert global_conf.ecmp_maximum_paths == 128


class BGPGlobalSerializerUpdate(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.global_conf1 = BGPGlobal.objects.create(
            device=self.device1,
            local_asn=self.asn1,
            router_id="192.0.2.1",
            ebgp_administrative_distance=20,
            ibgp_administrative_distance=170,
            graceful_restart=True,
            graceful_restart_time=240,
            ecmp=True,
            ecmp_maximum_paths=128,
        )

    def test_already_existing(self):
        data = {
            "device": self.device1.pk,
            "local_asn": self.asn1.pk,
            "router_id": "192.0.2.1",
            "ebgp_administrative_distance": 170,
            "ibgp_administrative_distance": 170,
            "graceful_restart": True,
            "graceful_restart_time": 240,
            "ecmp": True,
            "ecmp_maximum_paths": 128,
        }
        bgp_global_serializer = BGPGlobalSerializer(data=data)
        assert bgp_global_serializer.is_valid() == True
        self.assertRaises(IntegrityError, bgp_global_serializer.save)

    def test_update(self):
        data = {
            "device": self.device1.pk,
            "local_asn": self.asn1.pk,
            "router_id": "192.0.2.1",
            "ebgp_administrative_distance": 170,
            "ibgp_administrative_distance": 170,
            "graceful_restart": True,
            "graceful_restart_time": 240,
            "ecmp": True,
            "ecmp_maximum_paths": 128,
        }
        bgp_global_serializer = BGPGlobalSerializer(instance=self.global_conf1, data=data)
        assert bgp_global_serializer.is_valid() == True
        bgp_global_serializer.save()

        global_conf = BGPGlobal.objects.get(device__name="router-test1")
        assert global_conf.ebgp_administrative_distance == 170


class BGPSessionSerializerCreate(BaseTestCase):
    def test_bgp_session_creation(self):
        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv4-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv4-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "active",
            "password": "1234",
            "tenant": self.tenant.pk,
        }

        bgp_session_serializer = BGPSessionSerializer(data=data)
        assert bgp_session_serializer.is_valid() == True
        bgp_session_serializer.save()


class BGPSessionSerializerUpdate(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.device_bgp_session1 = DeviceBGPSession.objects.create(
            device=self.device1, local_asn=self.asn1, local_address=self.ip_address1
        )
        self.device_bgp_session2 = DeviceBGPSession.objects.create(
            device=self.device2, local_asn=self.asn2, local_address=self.ip_address2
        )
        self.bgp_session = BGPSession.objects.create(
            peer_a=self.device_bgp_session1,
            peer_b=self.device_bgp_session2,
            status="active",
            password="test",
            tenant=self.tenant,
        )
        self.prefix_list1 = PrefixList.objects.create(
            name="PF-TEST", device=self.device1, ip_version="ipv4"
        )
        self.prefix_list2 = PrefixList.objects.create(
            name="PF-TEST", device=self.device2, ip_version="ipv4"
        )
        self.prefix_list_term1 = PrefixListTerm.objects.create(
            prefix_list=self.prefix_list1,
            sequence=5,
            decision="permit",
            prefix=IPNetwork("10.0.0.0/8"),
        )
        self.prefix_list_term2 = PrefixListTerm.objects.create(
            prefix_list=self.prefix_list2,
            sequence=5,
            decision="permit",
            prefix=IPNetwork("10.0.0.0/8"),
        )

        self.bgp_community_list1 = BGPCommunityList.objects.create(
            name="CL-TEST", device=self.device1
        )
        self.bgp_community_list_term1 = BGPCommunityListTerm.objects.create(
            bgp_community_list=self.bgp_community_list1,
            sequence=5,
            decision="permit",
            community="64666:123",
        )
        self.bgp_community_list2 = BGPCommunityList.objects.create(
            name="CL-TEST", device=self.device2
        )
        self.bgp_community_list_term2 = BGPCommunityListTerm.objects.create(
            bgp_community_list=self.bgp_community_list2,
            sequence=5,
            decision="permit",
            community="64666:123",
        )

        self.route_policy1 = RoutePolicy.objects.create(name="RM-TEST", device=self.device1)
        self.route_policy2 = RoutePolicy.objects.create(name="RM-TEST", device=self.device2)

        data_terms1 = [
            {
                "sequence": 5,
                "decision": "permit",
                "from_bgp_community_list": self.bgp_community_list1,
                "set_local_pref": 100,
            },
            {
                "sequence": 10,
                "decision": "permit",
                "from_prefix_list": self.prefix_list1,
                "set_local_pref": 200,
            },
        ]

        self.route_policy_terms1 = RoutePolicyTerm.objects.bulk_create(
            [
                RoutePolicyTerm(route_policy=self.route_policy1, **data_term)
                for data_term in data_terms1
            ]
        )

        data_terms2 = [
            {
                "sequence": 5,
                "decision": "permit",
                "from_bgp_community_list": self.bgp_community_list2,
                "set_local_pref": 100,
            },
            {
                "sequence": 10,
                "decision": "permit",
                "from_prefix_list": self.prefix_list2,
                "set_local_pref": 200,
            },
        ]

        self.route_policy_terms2 = RoutePolicyTerm.objects.bulk_create(
            [
                RoutePolicyTerm(route_policy=self.route_policy2, **data_term)
                for data_term in data_terms2
            ]
        )

    def test_bgp_session_add__existing_session(self):
        """Adding a BGP session already existing (same devices/IP addresses).
        This test must raise a validation error."""
        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv4-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv4-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "active",
            "password": "1234",
        }
        bgp_session_serializer = BGPSessionSerializer(data=data)
        assert bgp_session_serializer.is_valid() == False
        assert bgp_session_serializer.errors["errors"][0] == ErrorDetail(
            string="[ErrorDetail(string='A BGP session already exists between these 2 devices and IP addresses.', code='invalid')]",
            code="invalid",
        )

    def test_bgp_session_update__status_and_password(self):
        """Adding ipv4-unicast afisafi to an existing session."""
        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "",
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "",
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "maintenance",  # active to maintenance
            "password": "5678",  # 1234 to 5678
        }

        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        assert bgp_session_serializer.is_valid() == True
        bgp_session_serializer.save()

        bgp_session_got = BGPSession.objects.get(id=self.bgp_session.pk)
        assert bgp_session_got.status == "maintenance"
        assert bgp_session_got.password == "5678"
        assert bgp_session_got.tenant.name == "tenant1"

    def test_bgp_session_update__modify_peer(self):
        """Modify setting of a peer (DeviceBGPSession)."""
        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "peer_a",
                "maximum_prefixes": 50000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "peer_b",
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "active",
            "password": "1234",
        }
        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        assert bgp_session_serializer.is_valid() == True
        bgp_session_serializer.save()

        bgp_session_got = BGPSession.objects.get(id=self.bgp_session.pk)
        assert bgp_session_got.peer_a.description == "peer_a"
        assert bgp_session_got.peer_a.maximum_prefixes == 50000
        assert bgp_session_got.peer_a.enforce_first_as == False
        assert bgp_session_got.peer_b.description == "peer_b"

    def test_bgp_session_update__patch_peer_a_route_policy(self):
        """Peer setting of a peer (DeviceBGPSession)."""
        # Set route_policy_out
        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "route_policy_out": self.route_policy1.pk,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
            },
        }
        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        assert bgp_session_serializer.is_valid() == True
        bgp_session_serializer.save()

        bgp_session_got = BGPSession.objects.get(id=self.bgp_session.pk)
        assert bgp_session_got.peer_a.route_policy_out == self.route_policy1

        # Remove route_policy_out
        data["peer_a"]["route_policy_out"] = None

        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        assert bgp_session_serializer.is_valid() == True
        bgp_session_serializer.save()

        bgp_session_got = BGPSession.objects.get(id=self.bgp_session.pk)
        assert bgp_session_got.peer_a.route_policy_out == None

    def test_bgp_session_update__add_afisafi(self):
        """Adding ipv4-unicast afisafi to an existing session"""
        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv4-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv4-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "active",
            "password": "1234",
        }

        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        assert bgp_session_serializer.is_valid() == True
        bgp_session_serializer.save()

    def test_bgp_session_update__replace_afisafi(self):
        """Replace ipv4 afisafi by ipv6 to an existing session"""
        # we add first an ipv4 unicast safi
        for device_bgp_session in [self.device_bgp_session1, self.device_bgp_session2]:
            AfiSafi.objects.create(
                device_bgp_session=device_bgp_session,
                afi_safi_name="ipv4-unicast",
            )
        # here is the new data, we now want an ipv6 afisafi instead
        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv6-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "",
                "afi_safis": [{"afi_safi_name": "ipv6-unicast"}],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "active",
            "password": "1234",
        }

        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        assert bgp_session_serializer.is_valid() == True
        bgp_session_serializer.save()

        # check in database that the object has been modified
        for device_bgp_session in [self.device_bgp_session1, self.device_bgp_session2]:
            afi_safi = AfiSafi.objects.filter(
                device_bgp_session=device_bgp_session,
            )
            assert len(afi_safi) == 1
            assert afi_safi[0].afi_safi_name == "ipv6-unicast"

    def test_bgp_session_update__set_route_policy_afisafi(self):
        """Set route policies on an existing afisafi."""
        # we add first an ipv4 unicast safi
        for device_bgp_session in [self.device_bgp_session1, self.device_bgp_session2]:
            AfiSafi.objects.create(
                device_bgp_session=device_bgp_session,
                afi_safi_name="ipv4-unicast",
            )

        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "",
                "afi_safis": [
                    {
                        "afi_safi_name": "ipv4-unicast",
                        "route_policy_in": self.route_policy1.pk,
                        "route_policy_out": self.route_policy1.pk,
                    }
                ],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "",
                "afi_safis": [
                    {
                        "afi_safi_name": "ipv4-unicast",
                        "route_policy_in": self.route_policy2.pk,
                        "route_policy_out": self.route_policy2.pk,
                    }
                ],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "active",
            "password": "1234",
        }

        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        bgp_session_serializer.is_valid()
        bgp_session_serializer.save()

        # check in database that the object has been modified with what has been provided to the serializer
        for device_bgp_session, route_policy in zip(
            [self.device_bgp_session1, self.device_bgp_session2],
            [self.route_policy1, self.route_policy2],
        ):
            afi_safi = AfiSafi.objects.filter(
                device_bgp_session=device_bgp_session,
            )
            assert len(afi_safi) == 1
            assert afi_safi[0].afi_safi_name == "ipv4-unicast"
            assert afi_safi[0].route_policy_in == route_policy
            assert afi_safi[0].route_policy_out == route_policy

    def test_bgp_session_update__set_bad_route_policy_afisafi(self):
        """Set route policies from another device on an existing afisafi."""
        # we add first an ipv4 unicast safi
        for device_bgp_session in [self.device_bgp_session1, self.device_bgp_session2]:
            AfiSafi.objects.create(
                device_bgp_session=device_bgp_session,
                afi_safi_name="ipv4-unicast",
            )

        data = {
            "peer_a": {
                "local_address": self.ip_address1.pk,
                "device": self.device1.pk,
                "local_asn": self.asn1.pk,
                "description": "",
                "afi_safis": [
                    {
                        "afi_safi_name": "ipv4-unicast",
                        "route_policy_in": self.route_policy2.pk,
                        "route_policy_out": self.route_policy2.pk,
                    }
                ],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "peer_b": {
                "local_address": self.ip_address2.pk,
                "device": self.device2.pk,
                "local_asn": self.asn2.pk,
                "description": "",
                "afi_safis": [
                    {
                        "afi_safi_name": "ipv4-unicast",
                    }
                ],
                "maximum_prefixes": 1000,
                "enforce_first_as": False,
            },
            "status": "active",
            "password": "1234",
        }

        bgp_session_serializer = BGPSessionSerializer(instance=self.bgp_session, data=data)
        assert not bgp_session_serializer.is_valid()
        assert bgp_session_serializer.errors["errors"][0] == ErrorDetail(
            string="route_policy_in is not on the same device", code="invalid"
        )
