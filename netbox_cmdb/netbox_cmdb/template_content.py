from extras.plugins import PluginTemplateExtension


class Decommisioning(PluginTemplateExtension):
    model = "dcim.device"

    def buttons(self):
        return (
            f'<a href="#" hx-get="/plugins/cmdb/decommisioning/{self.context["object"].id}/delete" '
            'hx-target="#htmx-modal-content" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#htmx-modal" '
            'class="btn btn-sm btn-danger">Decommission</a>'
        )


template_extensions = [Decommisioning]
