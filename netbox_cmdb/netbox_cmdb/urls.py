"""URLs."""

from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_cmdb.models.bgp import ASN, BGPSession, DeviceBGPSession, BGPPeerGroup
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
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
    DecommissioningView,
    DeviceBGPSessionEditView,
    DeviceBGPSessionListView,
    DeviceBGPSessionView,
    DeviecBGPSessionDeleteView,
    RoutePolicyDeleteView,
    RoutePolicyEditView,
    RoutePolicyListView,
    RoutePolicyView,
    SNMPCommunityDeleteView,
    SNMPCommunityEditView,
    SNMPCommunityListView,
    SNMPDeleteView,
    SNMPEditView,
    SNMPListView,
)

urlpatterns = [
    path(
        "decommisioning/<int:pk>/delete",
        DecommissioningView.as_view(),
        name="decommisioning_delete",
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
        DeviecBGPSessionDeleteView.as_view(),
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
]
