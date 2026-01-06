"""Views."""

import math
from datetime import datetime

from dcim.models import Device, Site
from django.db import transaction
from django.shortcuts import render
from netbox.views.generic import (
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from netbox.views.generic.bulk_views import BulkDeleteView
from utilities.forms import ConfirmationForm
from utilities.utils import count_related

from netbox_cmdb.filtersets import (
    ASNFilterSet,
    BGPPeerGroupFilterSet,
    BGPSessionFilterSet,
    DeviceBGPSessionFilterSet,
    RoutePolicyFilterSet,
    SNMPFilterSet,
    SyslogFilterSet
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
    SyslogServerForm,
    SyslogForm,

)
from netbox_cmdb.helpers import cleaning
from netbox_cmdb.models.bgp import (
    ASN,
    AfiSafi,
    BGPPeerGroup,
    BGPSession,
    DeviceBGPSession,
)
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.models.syslog import Syslog, SyslogServer
from netbox_cmdb.tables import (
    ASNTable,
    BGPPeerGroupTable,
    BGPSessionTable,
    DeviceBGPSessionTable,
    RoutePolicyTable,
    SNMPCommunityTable,
    SNMPTable,
    SyslogTable,
    SyslogServerTable,
)


class DecommissioningBaseView(ObjectDeleteView):
    template_name = "netbox_cmdb/decommissioning/base.html"
    site_template_name = "netbox_cmdb/decommissioning/site_progressive.html"
    device_template_name = "netbox_cmdb/decommissioning/device_summary.html"
    base_form_url = ""


class DeviceDecommissioningView(DecommissioningBaseView):
    base_form_url = "/plugins/cmdb/decommissioning/device"
    queryset = Device.objects.all()

    def get(self, request, *args, **kwargs):
        device = self.get_object(**kwargs)
        form = ConfirmationForm(initial=request.GET)

        return render(
            request,
            self.template_name,
            {
                "object": device,
                "object_type": "device",
                "form": form,
                "return_url": self.get_return_url(request, device),
                **self.get_extra_context(request, device),
            },
        )

    def post(self, request, *args, **kwargs):
        # Fetch the device to delete
        device = self.get_object(**kwargs)

        try:
            with transaction.atomic():
                deleted = cleaning.clean_cmdb_for_devices([device.id])
                device.delete()
        except Exception as error:
            return render(
                request,
                self.device_template_name,
                context={"error": f"Failed to clean device: {error}"},
            )

        return render(
            request,
            self.device_template_name,
            context={"deleted_device": device.name, "deleted_objects": deleted},
        )


class SiteDecommissioningView(DecommissioningBaseView):
    base_form_url = "/plugins/cmdb/decommissioning/site"
    queryset = Site.objects.all()

    def get(self, request, *args, **kwargs):
        site = self.get_object(**kwargs)
        form = ConfirmationForm(initial=request.GET)

        return render(
            request,
            self.template_name,
            {
                "object": site,
                "object_type": "site",
                "form": form,
                "return_url": self.get_return_url(request, site),
                **self.get_extra_context(request, site),
            },
        )

    def post(self, request, *args, **kwargs):
        # Fetch the device to delete
        site = self.get_object(**kwargs)
        devices = Device.objects.filter(site=site.id)

        # Get list of devices to delete
        CHUNK_SIZE = 20
        device_ids = [dev.id for dev in devices]
        remaining_chunks = math.ceil(len(device_ids) / CHUNK_SIZE)

        # We avoid an infinite loop if we fail to delete devices
        if request.POST.get("chunks"):
            previously_remaining_chunks = int(request.POST["chunks"])
            if remaining_chunks >= previously_remaining_chunks:
                return render(
                    request,
                    self.site_template_name,
                    context={
                        "object": site,
                        "object_type": "site",
                        "status": '<span class="badge bg-danger">Failed</span>',
                        "error": "devices are not being deleted, stopping here",
                        "chunks": remaining_chunks,
                        "stop": True,
                    },
                )

        if not device_ids:
            try:
                with transaction.atomic():
                    cleaning.clean_site_topology(site)
            except Exception as error:
                return render(
                    request,
                    self.site_template_name,
                    context={
                        "object": site,
                        "object_type": "site",
                        "status": '<span class="badge bg-danger">Failed</span>',
                        "error": f"Topology cleaning failure: {error}",
                        "chunks": remaining_chunks,
                        "stop": True,
                    },
                )

        chunk = device_ids[0:CHUNK_SIZE]

        try:
            with transaction.atomic():
                cleaning.clean_cmdb_for_devices(chunk)
                device_names = [dev.name for dev in devices[0:CHUNK_SIZE]]
                for dev in devices[0:CHUNK_SIZE]:
                    dev.delete()

        except Exception as error:
            return render(
                request,
                self.site_template_name,
                context={
                    "object": site,
                    "object_type": "site",
                    "status": '<span class="badge bg-danger">Failed</span>',
                    "error": f"Device cleaning failure: {error}",
                    "chunks": remaining_chunks,
                    "stop": True,
                },
            )

        # Tell the client to continue requesting deletion
        if remaining_chunks:
            status = f"Number of devices to delete: {len(device_ids) - len(chunk)}"
            message = f'<div class="mb-3 alert alert-secondary"><b>{datetime.now().strftime("%H:%M:%S")}</b> - deleted: {device_names}</div>'

            return render(
                request,
                self.site_template_name,
                context={
                    "object": site,
                    "object_type": "site",
                    "status": status,
                    "message": message,
                    "chunks": remaining_chunks,
                },
            )

        return render(
            request,
            self.site_template_name,
            context={
                "object": site,
                "object_type": "site",
                "status": '<span class="badge bg-success">Success</span>',
                "message": f'<div class="mb-3 alert alert-success">{site.name}: site, racks, locations, devices and CMDB deleted</div>',
                "chunks": remaining_chunks,
                "stop": True,
            },
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


class DeviceBGPSessionDeleteView(ObjectDeleteView):
    queryset = DeviceBGPSession.objects.all()


class DeviceBGPSessionBulkDeleteView(BulkDeleteView):
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

class SyslogListView(ObjectListView):
    queryset = Syslog.objects.all()
    filterset = SyslogFilterSet
    table = SyslogTable


class SyslogEditView(ObjectEditView):
    queryset = Syslog.objects.all()
    form = SyslogForm


class SyslogDeleteView(ObjectDeleteView):
    queryset = Syslog.objects.all()

class SyslogServerListView(ObjectListView):
    queryset = SyslogServer.objects.all()
    filterset = SyslogFilterSet
    table = SyslogServerTable


class SyslogServerEditView(ObjectEditView):
    queryset = SyslogServer.objects.all()
    form = SyslogServerForm


class SyslogServerDeleteView(ObjectDeleteView):
    queryset = SyslogServer.objects.all()
