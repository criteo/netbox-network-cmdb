"""Forms."""

from dcim.models import Device, DeviceRole
from dcim.models.devices import DeviceType
from dcim.models.sites import SiteGroup
from django import forms
from django.utils.translation import gettext as _
from extras.models import Tag
from ipam.models import IPAddress
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms import DynamicModelMultipleChoiceField
from utilities.forms.fields import DynamicModelChoiceField, MultipleChoiceField

from netbox_cmdb.choices import AssetMonitoringStateChoices, AssetStateChoices
from netbox_cmdb.constants import MAX_COMMUNITY_PER_DEVICE
from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession, DeviceBGPSession
from netbox_cmdb.models.interface import (
    DeviceInterface,
    Link,
    LogicalInterface,
    PortLayout,
)
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.models.syslog import Syslog, SyslogServer
from netbox_cmdb.models.tacacs import Tacacs, TacacsServer, duplicate_priorities
from netbox_cmdb.models.vlan import VLAN
from netbox_cmdb.models.vrf import VRF


class ASNForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = ASN
        fields = ["number", "organization_name", "tags"]


class BGPSessionForm(NetBoxModelForm):
    peer_a = DynamicModelChoiceField(
        queryset=DeviceBGPSession.objects.all(),
        label=_("Peer A"),
        required=True,
    )
    peer_b = DynamicModelChoiceField(
        queryset=DeviceBGPSession.objects.all(),
        label=_("Peer B"),
        required=True,
    )

    class Meta:
        model = BGPSession
        fields = ["peer_a", "peer_b", "state", "monitoring_state", "tenant"]


class DeviceBGPSessionForm(NetBoxModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {})
        if instance is not None and instance.device:
            initial["device"] = str(instance.device)
            kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    device = forms.CharField(disabled=True)
    route_policy_in = DynamicModelChoiceField(
        queryset=RoutePolicy.objects.all(),
        label=_("Route Policy in"),
        query_params={
            "device__id": "$device",
        },
        to_field_name="name",
        fetch_trigger="open",
        required=False,
    )
    route_policy_out = DynamicModelChoiceField(
        queryset=RoutePolicy.objects.all(),
        label=_("Route Policy out"),
        query_params={
            "device__id": "$device",
        },
        to_field_name="name",
        fetch_trigger="open",
        required=False,
    )

    class Meta:
        model = DeviceBGPSession
        fields = ["device", "route_policy_in", "route_policy_out"]


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


class RoutePolicyForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    class Meta:
        model = RoutePolicy
        fields = [
            "name",
            "device",
            "description",
        ]


class RoutePolicyFilterSetForm(NetBoxModelFilterSetForm):
    device__id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        label=_("Device"),
        required=False,
    )
    name = forms.CharField(
        required=False,
    )

    model = RoutePolicy


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


class SNMPGroupForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    class Meta:
        model = SNMP
        fields = ["device", "community_list", "location", "contact"]

    def clean_community_list(self):
        community_list = self.cleaned_data.get("community_list")
        if len(community_list) > MAX_COMMUNITY_PER_DEVICE:
            raise forms.ValidationError(
                f"You cannot select more than {MAX_COMMUNITY_PER_DEVICE} SNMP Communities."
            )
        return community_list


class SNMPCommunityGroupForm(NetBoxModelForm):
    class Meta:
        model = SNMPCommunity
        fields = ["name", "community", "type"]


class SyslogForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    class Meta:
        model = Syslog
        fields = ["device", "server_list"]


class SyslogServerForm(NetBoxModelForm):

    class Meta:
        model = SyslogServer
        fields = ["server_address"]


class DeviceInterfaceForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label=_("Device"),
    )

    class Meta:
        model = DeviceInterface
        fields = [
            "device",
            "name",
            "enabled",
            "state",
            "monitoring_state",
            "autonegotiation",
            "speed",
            "fec",
            "description",
        ]


class LogicalInterfaceForm(NetBoxModelForm):
    parent_interface = DynamicModelChoiceField(
        queryset=DeviceInterface.objects.all(),
        label=_("Parent interface"),
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        label=_("VRF"),
        required=False,
    )
    ipv4_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label=_("IPv4 address"),
        required=False,
    )
    ipv6_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label=_("IPv6 address"),
        required=False,
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        label=_("Untagged VLAN"),
        required=False,
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        label=_("Tagged VLANs"),
        required=False,
    )
    native_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        label=_("Native VLAN"),
        required=False,
    )

    class Meta:
        model = LogicalInterface
        fields = [
            "parent_interface",
            "index",
            "enabled",
            "state",
            "monitoring_state",
            "type",
            "mode",
            "mtu",
            "vrf",
            "ipv4_address",
            "ipv6_address",
            "untagged_vlan",
            "tagged_vlans",
            "native_vlan",
            "description",
        ]


class LinkForm(NetBoxModelForm):
    interface_a = DynamicModelChoiceField(
        queryset=DeviceInterface.objects.all(),
        label=_("Interface A"),
    )
    interface_b = DynamicModelChoiceField(
        queryset=DeviceInterface.objects.all(),
        label=_("Interface B"),
    )

    class Meta:
        model = Link
        fields = [
            "interface_a",
            "interface_b",
            "state",
            "monitoring_state",
        ]


class PortLayoutForm(NetBoxModelForm):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        label=_("Device type"),
    )
    network_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        label=_("Network role"),
    )

    class Meta:
        model = PortLayout
        fields = [
            "device_type",
            "network_role",
            "name",
            "label_name",
            "logical_name",
            "vendor_name",
            "vendor_short_name",
            "vendor_long_name",
        ]


class TacacsServerListCleanMixin:
    """Shared server_list validation, for both the plugin UI and the Django admin forms.

    The API enforces the same rule in TacacsSerializer.validate_server_list(). It cannot live in
    Tacacs.clean() as a ModelForm validates the instance before saving its m2m fields.
    """

    def clean(self):
        cleaned_data = super().clean()
        duplicates = duplicate_priorities(cleaned_data.get("server_list") or [])
        if duplicates:
            raise forms.ValidationError(
                {
                    "server_list": "Servers of a same device must have distinct priorities, "
                    f"already used more than once: {duplicates}."
                }
            )
        return cleaned_data


class TacacsForm(TacacsServerListCleanMixin, NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    class Meta:
        model = Tacacs
        fields = [
            "device",
            "passkey",
            "server_list",
        ]

    # passkey length is validated by Tacacs.clean()


class TacacsAdminForm(TacacsServerListCleanMixin, forms.ModelForm):
    """Django admin form for Tacacs, the admin does not use TacacsForm."""

    class Meta:
        model = Tacacs
        fields = "__all__"


class TacacsServerForm(NetBoxModelForm):

    class Meta:
        model = TacacsServer
        fields = [
            "server_address",
            "priority",
            "tcp_port",
        ]
