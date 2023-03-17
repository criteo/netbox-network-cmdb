"""Views."""
from netbox.views.generic import (
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)

from netbox_cmdb.filtersets import (
    ASNFilterSet,
    BGPPeerGroupFilterSet,
    BGPSessionFilterSet,
)
from netbox_cmdb.forms import ASNForm, BGPPeerGroupForm, BGPSessionForm
from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession
from netbox_cmdb.tables import ASNTable, BGPPeerGroupTable, BGPSessionTable


## ASN views
class ASNListView(ObjectListView):
    queryset = ASN.objects.all()
    filterset = ASNFilterSet
    table = ASNTable
    template_name = "netbox_cmdb/asn_list.html"


class ASNEditView(ObjectEditView):
    queryset = ASN.objects.all()
    form = ASNForm


class ASNDeleteView(ObjectDeleteView):
    queryset = ASN.objects.all()


class ASNView(ObjectView):
    queryset = ASN.objects.all()
    template_name = "netbox_cmdb/asn.html"


## BGP Sessions views


class BGPSessionListView(ObjectListView):
    queryset = BGPSession.objects.all()
    filterset = BGPSessionFilterSet
    table = BGPSessionTable
    template_name = "netbox_cmdb/bgpsession_list.html"


class BGPSessionEditView(ObjectEditView):
    queryset = BGPSession.objects.all()
    form = BGPSessionForm


class BGPSessionDeleteView(ObjectDeleteView):
    queryset = BGPSession.objects.all()


class BGPSessionView(ObjectView):
    queryset = BGPSession.objects.all()
    template_name = "netbox_cmdb/bgpsession.html"


## Peer groups views
class BGPPeerGroupListView(ObjectListView):
    queryset = BGPPeerGroup.objects.all()
    filterset = BGPPeerGroupFilterSet
    table = BGPPeerGroupTable
    template_name = "netbox_cmdb/bgppeergroup_list.html"


class BGPPeerGroupEditView(ObjectEditView):
    queryset = BGPPeerGroup.objects.all()
    form = BGPPeerGroupForm


class BGPPeerGroupDeleteView(ObjectDeleteView):
    queryset = BGPPeerGroup.objects.all()


class BGPPeerGroupView(ObjectView):
    queryset = BGPPeerGroup.objects.all()
    template_name = "netbox_cmdb/bgppeergroup.html"
