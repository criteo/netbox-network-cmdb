"""URLs."""
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_cmdb.models.bgp import *
from netbox_cmdb.views import (
    ASNDeleteView,
    ASNEditView,
    ASNListView,
    ASNView,
    BGPPeerGroupDeleteView,
    BGPPeerGroupEditView,
    BGPPeerGroupListView,
    BGPPeerGroupView,
    BGPSessionDeleteView,
    BGPSessionEditView,
    BGPSessionListView,
    BGPSessionView,
)

urlpatterns = [
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
]
