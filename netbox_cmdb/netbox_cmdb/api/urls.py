from django.urls import path
from netbox.api.routers import NetBoxRouter

from netbox_cmdb.api.bgp.views import (
    ASNViewSet,
    AvailableASNsView,
    BGPGlobalViewSet,
    BGPPeerGroupViewSet,
    BGPSessionsViewSet,
    DeviceBGPSessionsViewSet,
)
from netbox_cmdb.api.bgp_community_list.views import BGPCommunityListViewSet
from netbox_cmdb.api.cmdb.views import (
    DeviceCMDBDecommissioningAPIView,
    DeviceDecommissioningAPIView,
    SiteDecommissioningAPIView,
)
from netbox_cmdb.api.interface.views import (
    DeviceInterfaceViewSet,
    LinkViewSet,
    LogicalInterfaceViewSet,
    PortLayoutViewSet,
)
from netbox_cmdb.api.prefix_list.views import PrefixListViewSet
from netbox_cmdb.api.route_policy.views import RoutePolicyViewSet
from netbox_cmdb.api.snmp.views import SNMPCommunityViewSet, SNMPViewSet
from netbox_cmdb.api.vlan.views import VLANViewSet
from netbox_cmdb.api.vrf.views import VRFViewSet
from netbox_cmdb.api.syslog.views import SyslogServerViewSet, SyslogViewSet
from netbox_cmdb.api.tacacs.views import TacacsServerViewSet, TacacsViewSet

router = NetBoxRouter()

router.register("asns", ASNViewSet)
router.register("bgp-global", BGPGlobalViewSet)
router.register("bgp-sessions", BGPSessionsViewSet)
router.register("device-bgp-sessions", DeviceBGPSessionsViewSet)
router.register("bgp-community-lists", BGPCommunityListViewSet)
router.register("device-interfaces", DeviceInterfaceViewSet)
router.register("logical-interfaces", LogicalInterfaceViewSet)
router.register("links", LinkViewSet)
router.register("peer-groups", BGPPeerGroupViewSet)
router.register("port-layouts", PortLayoutViewSet)
router.register("prefix-lists", PrefixListViewSet)
router.register("route-policies", RoutePolicyViewSet)
router.register("snmp", SNMPViewSet)
router.register("snmp-community", SNMPCommunityViewSet)
router.register("vlans", VLANViewSet)
router.register("vrfs", VRFViewSet)
router.register("syslog", SyslogViewSet)
router.register("syslog-server", SyslogServerViewSet)
router.register("tacacs", TacacsViewSet)
router.register("tacacs-server", TacacsServerViewSet)

urlpatterns = [
    path(
        "asns/available-asn/",
        AvailableASNsView.as_view(),
        name="asns-available-asn",
    ),
    path(
        "management/device-cmdb-decommissioning/",
        DeviceCMDBDecommissioningAPIView.as_view(),
        name="device-cmdb-decommissioning",
    ),
    path(
        "management/device-decommissioning/",
        DeviceDecommissioningAPIView.as_view(),
        name="device-decommissioning",
    ),
    path(
        "management/site-decommissioning/",
        SiteDecommissioningAPIView.as_view(),
        name="site-decommissioning",
    ),
]
urlpatterns += router.urls
