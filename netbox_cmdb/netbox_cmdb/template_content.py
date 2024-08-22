from extras.plugins import PluginTemplateExtension


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


template_extensions = [DeviceDecommissioning, SiteDecommissioning]
