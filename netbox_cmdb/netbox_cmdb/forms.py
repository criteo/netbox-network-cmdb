"""Forms."""

from dcim.models import Device
from dcim.models.devices import DeviceType
from dcim.models.sites import SiteGroup
from django import forms
from django.utils.translation import gettext as _
from extras.models import Tag
from utilities.forms import DynamicModelMultipleChoiceField
from utilities.forms.fields import DynamicModelChoiceField, MultipleChoiceField

from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from netbox_cmdb.choices import AssetMonitoringStateChoices, AssetStateChoices
from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession


class ASNForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = ASN
        fields = ["number", "organization_name", "tags"]


class BGPSessionForm(NetBoxModelForm):
    class Meta:
        model = BGPSession
        fields = ["peer_a", "peer_b", "state", "monitoring_state"]


class BGPSessionFilterSetForm(NetBoxModelFilterSetForm):
    device__site__group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        label=_("Site"),
        required=False,
    )
    device__device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        label=_("Device type"),
        required=False,
    )
    state = MultipleChoiceField(choices=AssetStateChoices, required=False)
    monitoring_state = MultipleChoiceField(choices=AssetMonitoringStateChoices, required=False)

    model = BGPSession


class BGPPeerGroupForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )
    device = DynamicModelChoiceField(queryset=Device.objects.all())
    local_asn = DynamicModelChoiceField(queryset=ASN.objects.all(), required=False)
    remote_asn = DynamicModelChoiceField(queryset=ASN.objects.all(), required=False)

    class Meta:
        model = BGPPeerGroup
        fields = [
            "name",
            "device",
            "local_asn",
            "remote_asn",
            "tags",
        ]


class InlineTermForm(forms.models.BaseInlineFormSet):
    """InlineTermForm is a form that require at least one item to be valid.
    It is useful for following models:
    - bgp community list
    - route policies
    - prefix list"""

    def clean(self):
        # count valid forms.
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass  # such validation is already handled in previous validation steps
        if count < 1:
            raise forms.ValidationError("You must have at least one term.")
