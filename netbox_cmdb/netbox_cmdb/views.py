"""Views."""

from utilities.utils import count_related

from netbox.views.generic import (
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from netbox.views.generic.bulk_views import BulkDeleteView
from netbox_cmdb.filtersets import (
    ASNFilterSet,
    BGPPeerGroupFilterSet,
    BGPSessionFilterSet,
    DeviceBGPSessionFilterSet,
    RoutePolicyFilterSet,
    SNMPFilterSet,
)
from netbox_cmdb.forms import (
    ASNForm,
    BGPPeerGroupForm,
    BGPSessionFilterSetForm,
    BGPSessionForm,
    DeviceBGPSessionForm,
    RoutePolicyFilterSetForm,
    RoutePolicyForm,
    SNMPCommunityGroupForm,
    SNMPGroupForm,
)
from netbox_cmdb.models.bgp import (
    ASN,
    AfiSafi,
    BGPPeerGroup,
    BGPSession,
    DeviceBGPSession,
)
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.tables import (
    ASNTable,
    BGPPeerGroupTable,
    BGPSessionTable,
    DeviceBGPSessionTable,
    RoutePolicyTable,
    SNMPCommunityTable,
    SNMPTable,
)


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
    queryset = BGPSession.objects.prefetch_related("peer_a", "peer_b").all()
    filterset = BGPSessionFilterSet
    filterset_form = BGPSessionFilterSetForm
    table = BGPSessionTable
    template_name = "netbox_cmdb/bgpsession_list.html"


class BGPSessionEditView(ObjectEditView):
    queryset = BGPSession.objects.all()
    form = BGPSessionForm


class BGPSessionBulkDeleteView(BulkDeleteView):
    queryset = BGPSession.objects.all()
    filterset = BGPSessionFilterSet
    table = BGPSessionTable


class BGPSessionDeleteView(ObjectDeleteView):
    queryset = BGPSession.objects.all()


class BGPSessionView(ObjectView):
    queryset = BGPSession.objects.prefetch_related(
        "peer_a", "peer_b", "peer_a__afi_safis", "peer_b__afi_safis"
    ).all()
    template_name = "netbox_cmdb/bgpsession.html"


## DeviceBGPSession views
class DeviceBGPSessionListView(ObjectListView):
    queryset = DeviceBGPSession.objects.all()
    filterset = DeviceBGPSessionFilterSet
    table = DeviceBGPSessionTable


class DeviceBGPSessionView(ObjectView):
    queryset = DeviceBGPSession.objects.all()


class DeviceBGPSessionEditView(ObjectEditView):
    queryset = DeviceBGPSession.objects.all()
    form = DeviceBGPSessionForm
    filterset = DeviceBGPSessionFilterSet


class DeviecBGPSessionDeleteView(ObjectDeleteView):
    queryset = DeviceBGPSession.objects.all()


class DeviecBGPSessionBulkDeleteView(BulkDeleteView):
    queryset = DeviceBGPSession.objects.all()
    filterset = DeviceBGPSessionFilterSet
    table = DeviceBGPSessionTable


## Peer groups views
class BGPPeerGroupListView(ObjectListView):
    queryset = BGPPeerGroup.objects.annotate(refcount=count_related(DeviceBGPSession, "peer_group"))
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


## Route policy views


class RoutePolicyListView(ObjectListView):
    queryset = RoutePolicy.objects.annotate(
        refcount=sum(
            [
                count_related(AfiSafi, "route_policy_in"),
                count_related(AfiSafi, "route_policy_out"),
                count_related(DeviceBGPSession, "route_policy_in"),
                count_related(DeviceBGPSession, "route_policy_out"),
                count_related(BGPPeerGroup, "route_policy_in"),
                count_related(BGPPeerGroup, "route_policy_out"),
            ]
        )
    )
    filterset_form = RoutePolicyFilterSetForm
    filterset = RoutePolicyFilterSet
    table = RoutePolicyTable


class RoutePolicyView(ObjectView):
    queryset = RoutePolicy.objects.prefetch_related("route_policy_term").all()
    template_name = "netbox_cmdb/routepolicy.html"


class RoutePolicyEditView(ObjectEditView):
    model = RoutePolicy
    queryset = RoutePolicy.objects.prefetch_related("route_policy_term").all()
    form = RoutePolicyForm
    filterset = RoutePolicyFilterSet


class RoutePolicyDeleteView(ObjectDeleteView):
    queryset = RoutePolicy.objects.all()


class RoutePolicyBulkDeleteView(BulkDeleteView):
    queryset = RoutePolicy.objects.all()
    filterset = RoutePolicyFilterSet
    table = RoutePolicyTable


## Snmp groups views
class SNMPListView(ObjectListView):
    queryset = SNMP.objects.all()
    filterset = SNMPFilterSet
    table = SNMPTable


class SNMPEditView(ObjectEditView):
    queryset = SNMP.objects.all()
    form = SNMPGroupForm


class SNMPDeleteView(ObjectDeleteView):
    queryset = SNMP.objects.all()


## Snmp Community groups views
class SNMPCommunityListView(ObjectListView):
    queryset = SNMPCommunity.objects.all()
    table = SNMPCommunityTable


class SNMPCommunityEditView(ObjectEditView):
    queryset = SNMPCommunity.objects.all()
    form = SNMPCommunityGroupForm


class SNMPCommunityDeleteView(ObjectDeleteView):
    queryset = SNMPCommunity.objects.all()
