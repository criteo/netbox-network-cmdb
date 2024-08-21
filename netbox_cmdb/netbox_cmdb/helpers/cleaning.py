from dcim.models import Location, Rack
from django.db.models import Q

from netbox_cmdb.models.bgp import BGPPeerGroup, BGPSession, DeviceBGPSession
from netbox_cmdb.models.bgp_community_list import BGPCommunityList
from netbox_cmdb.models.prefix_list import PrefixList
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP


def clean_cmdb_for_devices(device_ids: list[int]):
    deleted_objects = {
        "bgp_sessions": [],
        "device_bgp_sessions": [],
        "bgp_peer_groups": [],
        "route_policies": [],
        "prefix_lists": [],
        "bgp_community_lists": [],
        "snmp": [],
    }

    bgp_sessions = BGPSession.objects.filter(
        Q(peer_a__device__id__in=device_ids) | Q(peer_b__device__id__in=device_ids)
    )
    device_bgp_sessions = DeviceBGPSession.objects.filter(device__id__in=device_ids)
    bgp_peer_groups = BGPPeerGroup.objects.filter(device__id__in=device_ids)
    route_policies = RoutePolicy.objects.filter(device__id__in=device_ids)
    prefix_lists = PrefixList.objects.filter(device__id__in=device_ids)
    bgp_community_lists = BGPCommunityList.objects.filter(device__id__in=device_ids)
    snmp = SNMP.objects.filter(device__id__in=device_ids)

    deleted_objects["bgp_sessions"] = [str(val) for val in list(bgp_sessions)]
    deleted_objects["device_bgp_sessions"] = [str(val) for val in list(device_bgp_sessions)]
    deleted_objects["bgp_peer_groups"] = [str(val) for val in list(bgp_peer_groups)]
    deleted_objects["route_policies"] = [str(val) for val in list(route_policies)]
    deleted_objects["prefix_lists"] = [str(val) for val in list(prefix_lists)]
    deleted_objects["bgp_community_lists"] = [str(val) for val in list(bgp_community_lists)]
    deleted_objects["snmp"] = [str(val) for val in list(snmp)]

    bgp_sessions.delete()
    device_bgp_sessions.delete()
    bgp_peer_groups.delete()
    route_policies.delete()
    prefix_lists.delete()
    bgp_community_lists.delete()
    snmp.delete()

    return deleted_objects


def clean_site_topology(site):
    racks = Rack.objects.filter(site=site.id)
    racks.delete()

    locations = Location.objects.filter(site=site.id)
    locations.delete()

    site.delete()
