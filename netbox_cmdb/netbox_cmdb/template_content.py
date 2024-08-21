from extras.plugins import PluginTemplateExtension


class DecommisioningBase(PluginTemplateExtension):
    def buttons(self):
        return (
            f'<a href="/plugins/cmdb/decommisioning/{self.obj}/{self.context["object"].id}/delete" '
            'class="btn btn-sm btn-danger">Decommission</a>'
        )


class DeviceDecommisioning(DecommisioningBase):
    model = "dcim.device"
    obj = "device"


class SiteDecommisioning(DecommisioningBase):
    model = "dcim.site"
    obj = "site"


template_extensions = [DeviceDecommisioning, SiteDecommisioning]
