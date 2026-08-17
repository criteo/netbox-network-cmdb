from django.db.models import Q
from extras.plugins import PluginTemplateExtension
from utilities.ordering import naturalize_interface

from netbox_cmdb.models.interface import DeviceInterface, Link


class DecommissioningBase(PluginTemplateExtension):
    def buttons(self):
        return (
            f'<a href="/plugins/cmdb/decommissioning/{self.obj}/{self.context["object"].id}/delete" '
            'class="btn btn-sm btn-danger">Decommission</a>'
        )


class DeviceDecommissioning(DecommissioningBase):
    model = "dcim.device"
    obj = "device"


class SiteDecommissioning(DecommissioningBase):
    model = "dcim.site"
    obj = "site"


class DeviceCMDBOverview(PluginTemplateExtension):
    """Shows CMDB interfaces and links related to the device on its detail page."""

    model = "dcim.device"

    def full_width_page(self):
        device = self.context["object"]

        interfaces = sorted(
            DeviceInterface.objects.filter(device=device).prefetch_related("logicalinterface"),
            key=lambda interface: naturalize_interface(interface.name.lower(), max_length=100),
        )
        links = (
            Link.objects.filter(Q(interface_a__device=device) | Q(interface_b__device=device))
            .select_related("interface_a__device", "interface_b__device")
            .order_by("interface_a__device__name", "interface_a__name")
        )

        return self.render(
            "netbox_cmdb/inc/device_cmdb_overview.html",
            extra_context={
                "cmdb_interfaces": interfaces,
                "cmdb_links": links,
            },
        )


template_extensions = [DeviceDecommissioning, SiteDecommissioning, DeviceCMDBOverview]
