"""Views."""

from dcim.models import Device
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from netbox.views.generic import (
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from netbox.views.generic.bulk_views import BulkDeleteView
from utilities.forms import ConfirmationForm
from utilities.htmx import is_htmx
from utilities.utils import count_related

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
from netbox_cmdb.models.bgp_community_list import BGPCommunityList
from netbox_cmdb.models.prefix_list import PrefixList
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


## Decommission a device
class DecommissioningView(ObjectDeleteView):
    queryset = Device.objects.all()
    template_name = "netbox_cmdb/decommissioning.html"

    def get(self, request, *args, **kwargs):
        """
        GET request handler.

        Args:
            request: The current request
        """
        obj = self.get_object(**kwargs)
        form = ConfirmationForm(initial=request.GET)

        # If this is an HTMX request, return only the rendered deletion form as modal content
        if is_htmx(request):
            # form_url = reverse("decommisioning_delete", kwargs={'pk': obj.pk})
            form_url = f"/plugins/cmdb/decommisioning/{kwargs['pk']}/delete"
            return render(
                request,
                "htmx/delete_form.html",
                {
                    "object": obj,
                    "object_type": self.queryset.model._meta.verbose_name,
                    "form": form,
                    "form_url": form_url,
                    **self.get_extra_context(request, obj),
                },
            )

        return render(
            request,
            self.template_name,
            {
                "object": obj,
                "form": form,
                "return_url": self.get_return_url(request, obj),
                **self.get_extra_context(request, obj),
            },
        )

    def post(self, request, *args, **kwargs):
        # Fetch the device to delete
        device = self.get_object(**kwargs)
        deleted_objects = {
            "bgp_sessions": [],
            "device_bgp_sessions": [],
            "bgp_peer_groups": [],
            "route_policies": [],
            "prefix_lists": [],
            "bgp_community_lists": [],
            "snmp": [],
        }

        device_name = device.name

        try:
            with transaction.atomic():
                bgp_sessions = BGPSession.objects.filter(
                    Q(peer_a__device__id=device.id) | Q(peer_b__device__id=device.id)
                )
                device_bgp_sessions = DeviceBGPSession.objects.filter(device__id=device.id)
                bgp_peer_groups = BGPPeerGroup.objects.filter(device__id=device.id)
                route_policies = RoutePolicy.objects.filter(device__id=device.id)
                prefix_lists = PrefixList.objects.filter(device__id=device.id)
                bgp_community_lists = BGPCommunityList.objects.filter(device__id=device.id)
                snmp = SNMP.objects.filter(device__id=device.id)

                deleted_objects["bgp_sessions"] = [str(val) for val in list(bgp_sessions)]
                deleted_objects["device_bgp_sessions"] = [
                    str(val) for val in list(device_bgp_sessions)
                ]
                deleted_objects["bgp_peer_groups"] = [str(val) for val in list(bgp_peer_groups)]
                deleted_objects["route_policies"] = [str(val) for val in list(route_policies)]
                deleted_objects["prefix_lists"] = [str(val) for val in list(prefix_lists)]
                deleted_objects["bgp_community_lists"] = [
                    str(val) for val in list(bgp_community_lists)
                ]
                deleted_objects["snmp"] = [str(val) for val in list(snmp)]

                bgp_sessions.delete()
                device_bgp_sessions.delete()
                bgp_peer_groups.delete()
                route_policies.delete()
                prefix_lists.delete()
                bgp_community_lists.delete()
                snmp.delete()

        except Exception as e:
            # Render the template with an error message
            return render(request, self.template_name, context={"error": str(e)})

        # Call the parent class's post method to delete the device
        super().post(request, *args, **kwargs)

        # Return the HTML response with the list of deleted objects
        return render(
            request,
            self.template_name,
            context={"deleted_device": device_name, "deleted_objects": deleted_objects},
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
