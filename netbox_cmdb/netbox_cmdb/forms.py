"""Forms."""
from dcim.models import Device
from django import forms
from extras.models import Tag
from netbox.forms import NetBoxModelForm
from utilities.forms import DynamicModelMultipleChoiceField
from utilities.forms.fields import DynamicModelChoiceField

from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession


class ASNForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = ASN
        fields = ["number", "organization_name", "tags"]


class BGPSessionForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )

    class Meta:
        model = BGPSession
        fields = [
            "peer_a",
            "peer_b",
            "tags",
        ]


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
