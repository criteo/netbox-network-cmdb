"""URLs."""

from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_cmdb.models.bgp import ASN, BGPSession, DeviceBGPSession, BGPPeerGroup
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.models.syslog import Syslog, SyslogServer
from netbox_cmdb.models.tacacs import Tacacs, TacacsServer
from netbox_cmdb.views import (
    ASNDeleteView,
    ASNEditView,
    ASNListView,
    ASNView,
    BGPPeerGroupDeleteView,
    BGPPeerGroupEditView,
    BGPPeerGroupListView,
    BGPPeerGroupView,
    BGPSessionBulkDeleteView,
    BGPSessionDeleteView,
    BGPSessionEditView,
    BGPSessionListView,
    BGPSessionView,
    DeviceBGPSessionEditView,
    DeviceBGPSessionListView,
    DeviceBGPSessionView,
    DeviceDecommissioningView,
    DeviceBGPSessionDeleteView,
    RoutePolicyDeleteView,
    RoutePolicyEditView,
    RoutePolicyListView,
    RoutePolicyView,
    SiteDecommissioningView,
    SNMPCommunityDeleteView,
    SNMPCommunityEditView,
    SNMPCommunityListView,
    SNMPDeleteView,
    SNMPEditView,
    SNMPListView,
    SyslogListView,
    SyslogEditView,
    SyslogDeleteView,
    SyslogServerListView,
    SyslogServerEditView,
    SyslogServerDeleteView,
    TacacsListView,
    TacacsEditView,
    TacacsDeleteView,
    TacacsServerListView,
    TacacsServerEditView,
    TacacsServerDeleteView,
)

urlpatterns = [
    path(
        "decommissioning/device/<int:pk>/delete",
        DeviceDecommissioningView.as_view(),
        name="device_decommissioning_delete",
    ),
    path(
        "decommissioning/site/<int:pk>/delete",
        SiteDecommissioningView.as_view(),
        name="site_decommissioning_delete",
    ),
    # ASN
    path("asn/", ASNListView.as_view(), name="asn_list"),
    path("asn/add/", ASNEditView.as_view(), name="asn_add"),
    path("asn/<int:pk>/", ASNView.as_view(), name="asn"),
    path("asn/<int:pk>/edit/", ASNEditView.as_view(), name="asn_edit"),
    path("asn/<int:pk>/delete/", ASNDeleteView.as_view(), name="asn_delete"),
    path(
        "asn/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="asn_changelog",
        kwargs={"model": ASN},
    ),
    path(
        "asn/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="asn_journal",
        kwargs={"model": ASN},
    ),
    # BGP session
    path("bgp-session/", BGPSessionListView.as_view(), name="bgpsession_list"),
    path("bgp-session/add/", BGPSessionEditView.as_view(), name="bgpsession_add"),
    path("bgp-session/<int:pk>/", BGPSessionView.as_view(), name="bgpsession"),
    path(
        "bgp-session/<int:pk>/edit/",
        BGPSessionEditView.as_view(),
        name="bgpsession_edit",
    ),
    path(
        "bgp-session/<int:pk>/delete/",
        BGPSessionDeleteView.as_view(),
        name="bgpsession_delete",
    ),
    path("bgp-session/delete/", BGPSessionBulkDeleteView.as_view(), name="bgpsession_bulk_delete"),
    path(
        "bgp-session/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="bgpsession_changelog",
        kwargs={"model": BGPSession},
    ),
    path(
        "bgp-session/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="bgpsession_journal",
        kwargs={"model": BGPSession},
    ),
    # Device BGP session
    path("device-bgp-session/", DeviceBGPSessionListView.as_view(), name="devicebgpsession_list"),
    path("device-bgp-session/add", DeviceBGPSessionEditView.as_view(), name="devicebgpsession_add"),
    path("device-bgp-session/<int:pk>/", DeviceBGPSessionView.as_view(), name="devicebgpsession"),
    path(
        "device-bgp-session/<int:pk>/edit",
        DeviceBGPSessionEditView.as_view(),
        name="devicebgpsession_edit",
    ),
    path(
        "device-bgp-session/<int:pk>/delete",
        DeviceBGPSessionDeleteView.as_view(),
        name="devicebgpsession_delete",
    ),
    path(
        "device-bgp-session/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="devicebgpsession_changelog",
        kwargs={"model": DeviceBGPSession},
    ),
    # Peer Group
    path("peer-group/", BGPPeerGroupListView.as_view(), name="bgppeergroup_list"),
    path("peer-group/add/", BGPPeerGroupEditView.as_view(), name="bgppeergroup_add"),
    path("peer-group/<int:pk>/", BGPPeerGroupView.as_view(), name="bgppeergroup"),
    path(
        "peer-group/<int:pk>/edit/",
        BGPPeerGroupEditView.as_view(),
        name="bgppeergroup_edit",
    ),
    path(
        "peer-group/<int:pk>/delete/",
        BGPPeerGroupDeleteView.as_view(),
        name="bgppeergroup_delete",
    ),
    path(
        "peer-group/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="bgppeergroup_changelog",
        kwargs={"model": BGPPeerGroup},
    ),
    path(
        "peer-group/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="bgppeergroup_journal",
        kwargs={"model": BGPPeerGroup},
    ),
    # Route Policy
    path("route-policy/", RoutePolicyListView.as_view(), name="routepolicy_list"),
    path("route-policy/add/", RoutePolicyEditView.as_view(), name="routepolicy_add"),
    path("route-policy/<int:pk>/", RoutePolicyView.as_view(), name="routepolicy"),
    path(
        "route-policy/<int:pk>/edit/",
        RoutePolicyEditView.as_view(),
        name="routepolicy_edit",
    ),
    path(
        "route-policy/<int:pk>/delete/",
        RoutePolicyDeleteView.as_view(),
        name="routepolicy_delete",
    ),
    path(
        "route-policy/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="routepolicy_changelog",
        kwargs={"model": RoutePolicy},
    ),
    path(
        "route-policy/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="routepolicy_journal",
        kwargs={"model": RoutePolicy},
    ),
    # SNMP
    path("snmp/", SNMPListView.as_view(), name="snmp_list"),
    path("snmp/add/", SNMPEditView.as_view(), name="snmp_add"),
    path(
        "snmp/<int:pk>/edit/",
        SNMPEditView.as_view(),
        name="snmp_edit",
    ),
    path(
        "snmp/<int:pk>/delete/",
        SNMPDeleteView.as_view(),
        name="snmp_delete",
    ),
    path(
        "snmp/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="snmp_changelog",
        kwargs={"model": SNMP},
    ),
    # SNMP Community
    path("snmp-community/", SNMPCommunityListView.as_view(), name="snmpcommunity_list"),
    path("snmp-community/add/", SNMPCommunityEditView.as_view(), name="snmpcommunity_add"),
    path(
        "snmp-community/<int:pk>/edit/",
        SNMPCommunityEditView.as_view(),
        name="snmpcommunity_edit",
    ),
    path(
        "snmp-community/<int:pk>/delete/",
        SNMPCommunityDeleteView.as_view(),
        name="snmpcommunity_delete",
    ),
    path(
        "snmp-community/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="snmpcommunity_changelog",
        kwargs={"model": SNMPCommunity},
    ),
    # SYSLOG
    path("syslog/", SyslogListView.as_view(), name="syslog_list"),
    path("syslog/add/", SyslogEditView.as_view(), name="syslog_add"),
    path(
        "syslog/<int:pk>/edit/",
        SyslogEditView.as_view(),
        name="syslog_edit",
    ),
    path(
        "syslog/<int:pk>/delete/",
        SyslogDeleteView.as_view(),
        name="syslog_delete",
    ),
    path(
        "syslog/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="syslog_changelog",
        kwargs={"model": Syslog},
    ),
    # SYSLOG SERVERS
    path("syslog-server/", SyslogServerListView.as_view(), name="syslogserver_list"),
    path("syslog-server/add/", SyslogServerEditView.as_view(), name="syslogserver_add"),
    path(
        "syslog-server/<int:pk>/edit/",
        SyslogServerEditView.as_view(),
        name="syslogserver_edit",
    ),
    path(
        "syslog-server/<int:pk>/delete/",
        SyslogServerDeleteView.as_view(),
        name="syslogserver_delete",
    ),
    path(
        "syslog-server/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="syslogserver_changelog",
        kwargs={"model": SyslogServer},
    ),
    # TACACS
    path("tacacs/", TacacsListView.as_view(), name="tacacs_list"),
    path("tacacs/add/", TacacsEditView.as_view(), name="tacacs_add"),
    path(
        "tacacs/<int:pk>/edit/",
        TacacsEditView.as_view(),
        name="tacacs_edit",
    ),
    path(
        "tacacs/<int:pk>/delete/",
        TacacsDeleteView.as_view(),
        name="tacacs_delete",
    ),
    path(
        "tacacs/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="tacacs_changelog",
        kwargs={"model": Tacacs},
    ),
    # TACACS SERVERS
    path("tacacs-server/", TacacsServerListView.as_view(), name="tacacsserver_list"),
    path("tacacs-server/add/", TacacsServerEditView.as_view(), name="tacacsserver_add"),
    path(
        "tacacs-server/<int:pk>/edit/",
        TacacsServerEditView.as_view(),
        name="tacacsserver_edit",
    ),
    path(
        "tacacs-server/<int:pk>/delete/",
        TacacsServerDeleteView.as_view(),
        name="tacacsserver_delete",
    ),
    path(
        "tacacs-server/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="tacacsserver_changelog",
        kwargs={"model": TacacsServer},
    ),
]
