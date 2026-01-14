"""Admin module."""

from dcim.models import Device
from django.contrib import admin
from django.contrib.admin.options import StackedInline
from django.db import transaction
from ipam.models import IPAddress
from tenancy.models import Tenant

from netbox_cmdb.forms import InlineTermForm
from netbox_cmdb.models.bgp import (
    ASN,
    AfiSafi,
    Aggregate,
    BGPGlobal,
    BGPPeerGroup,
    BGPSession,
    DeviceBGPSession,
    GlobalAfiSafi,
    RedistributedNetwork,
)
from netbox_cmdb.models.bgp_community_list import BGPCommunityList, BGPCommunityListTerm
from netbox_cmdb.models.interface import (
    DeviceInterface,
    Link,
    LogicalInterface,
    PortLayout,
)
from netbox_cmdb.models.prefix_list import PrefixList, PrefixListTerm
from netbox_cmdb.models.route_policy import RoutePolicy, RoutePolicyTerm
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.models.syslog import Syslog, SyslogServer
from netbox_cmdb.models.vlan import VLAN
from netbox_cmdb.models.vrf import VRF


class BaseAdmin(admin.ModelAdmin):
    """AdminCommon is a Django ModelAdmin class containing common attributes."""

    # exclude all non-editable fields, it means all other fields will be automatically displayed
    exclude = ["created", "last_updated", "object_changes"]


class AfiSafiInline(StackedInline):
    model = AfiSafi
    autocomplete_fields = ("route_policy_in", "route_policy_out")
    extra = 1


class AggregateInline(StackedInline):
    model = Aggregate


class RedistributedNetworkInline(StackedInline):
    model = RedistributedNetwork


@admin.register(GlobalAfiSafi)
class GlobalAfiSafiAdmin(BaseAdmin):
    model = GlobalAfiSafi
    inlines = [AggregateInline, RedistributedNetworkInline]

    search_fields = ("device__name", "afi_safi_name")
    autocomplete_fields = ("bgp_global",)
    list_display = ("bgp_global", "afi_safi_name")


@admin.register(BGPGlobal)
class BGPGlobalAdmin(BaseAdmin):
    models = BGPGlobal

    search_fields = ("device__name",)
    autocomplete_fields = (
        "device",
        "local_asn",
    )
    list_display = ("device",)


@admin.register(BGPPeerGroup)
class BGPPeerGroupAdmin(BaseAdmin):
    """Admin class to manage BGPPeerGroup objects."""

    search_fields = ("name", "device__name")
    autocomplete_fields = (
        "local_asn",
        "remote_asn",
        "device",
        "route_policy_in",
        "route_policy_out",
    )
    list_display = ("name", "device")


@admin.register(ASN)
class ASNAdmin(BaseAdmin):
    """Admin class to manage ASN objects."""

    search_fields = ("number", "organization_name")
    list_display = ("number", "organization_name")


@admin.register(DeviceBGPSession)
class DeviceBGPSessionAdmin(BaseAdmin):
    """Admin class to manage DeviceBGPSession objects."""

    search_fields = ("device__name", "local_address__address", "description")
    autocomplete_fields = (
        "device",
        "local_address",
        "local_asn",
        "peer_group",
        "route_policy_in",
        "route_policy_out",
    )

    inlines = [AfiSafiInline]
    list_display = (
        "device",
        "local_address",
        "local_asn",
        "peer_group",
        "description",
    )


@admin.register(BGPSession)
class BGPSessionAdmin(BaseAdmin):
    """Admin class to manage BGPSession objects."""

    search_fields = ("peer_a__device__name", "peer_b__device__name")
    autocomplete_fields = ("peer_a", "peer_b")

    def delete_queryset(self, request, queryset) -> None:
        """Override method as we prefer to call the delete() method of the model, taking care of
        removing BGP peers well."""

        with transaction.atomic():
            for obj in queryset:
                obj.delete()


class RoutePolicyTermInline(StackedInline):
    """Inline class to manage RoutePolicyTerm objects within RoutePolicy admin page."""

    model = RoutePolicyTerm
    formset = InlineTermForm
    autocomplete_fields = (
        "from_bgp_community_list",
        "from_prefix_list",
    )


@admin.register(RoutePolicy)
class RoutePolicyAdmin(BaseAdmin):
    """Admin class to manage RoutePolicy objects."""

    search_fields = ("name", "device__name")
    autocomplete_fields = ("device",)
    list_display = (
        "name",
        "device",
    )
    inlines = [RoutePolicyTermInline]


class PrefixListTermInline(StackedInline):
    """Inline class to manage PrefixListTerm objects within PrefixList admin page."""

    model = PrefixListTerm
    formset = InlineTermForm


@admin.register(PrefixList)
class PrefixListAdmin(BaseAdmin):
    """Admin class to manage PrefixList objects."""

    search_fields = ("name", "device__name")
    autocomplete_fields = ("device",)
    inlines = [PrefixListTermInline]
    list_display = (
        "name",
        "device",
    )


class BGPCommunityListTermInline(StackedInline):
    """Inline class to manage BGPCommunityListTerm objects within BGPCommunityList admin page."""

    model = BGPCommunityListTerm
    formset = InlineTermForm


@admin.register(BGPCommunityList)
class BGPCommunityListAdmin(BaseAdmin):
    """Admin class to manage BGPCommunityList objects."""

    search_fields = ("name", "device__name")
    autocomplete_fields = ("device",)
    inlines = [BGPCommunityListTermInline]
    list_display = (
        "name",
        "device",
    )


@admin.register(SNMP)
class SNMPAdmin(BaseAdmin):
    """Admin class to manage SNMPCommunity objects."""

    list_display = (
        "device",
        "community_list_display",
        "location",
        "contact",
    )

    search_fields = ("device__name", "location")

    def community_list_display(self, obj):
        return ", ".join([str(community) for community in obj.community_list.all()])

    community_list_display.short_description = "Community List"


@admin.register(SNMPCommunity)
class SNMPCommunitytAdmin(BaseAdmin):
    """Admin class to manage SNMP objects."""

    list_display = (
        "name",
        "type",
        "community",
    )
    search_fields = ("name", "name")


class LogicalInterfaceInline(StackedInline):
    """Admin class to manage LogicalInterface objects within DeviceInterface admin page."""

    model = LogicalInterface
    autocomplete_fields = (
        "vrf",
        "ipv4_address",
        "ipv6_address",
        "untagged_vlan",
        "native_vlan",
    )
    extra = 0
    fields = (
        "index",
        "enabled",
        "state",
        "monitoring_state",
        "mtu",
        "type",
        "vrf",
        "ipv4_address",
        "ipv6_address",
        "mode",
        "untagged_vlan",
        "native_vlan",
        "description",
    )
    filter_horizontal = ("tagged_vlans",)


@admin.register(DeviceInterface)
class DeviceInterfaceAdmin(BaseAdmin):
    """Admin class to manage DeviceInterface objects."""

    search_fields = ("name", "device__name", "description")
    autocomplete_fields = ("device",)
    list_display = (
        "name",
        "device",
        "enabled",
        "state",
        "monitoring_state",
        "speed",
        "fec",
    )
    list_filter = ("enabled", "state", "monitoring_state", "fec")
    inlines = [LogicalInterfaceInline]


@admin.register(LogicalInterface)
class LogicalInterfaceAdmin(BaseAdmin):
    """Admin class to manage LogicalInterface objects."""

    search_fields = (
        "parent_interface__name",
        "parent_interface__device__name",
        "description",
    )
    autocomplete_fields = (
        "parent_interface",
        "vrf",
        "ipv4_address",
        "ipv6_address",
        "untagged_vlan",
        "native_vlan",
    )
    list_display = (
        "parent_interface",
        "index",
        "enabled",
        "state",
        "monitoring_state",
        "type",
        "vrf",
        "ipv4_address",
        "ipv6_address",
    )
    list_filter = ("enabled", "state", "monitoring_state", "type", "mode")
    filter_horizontal = ("tagged_vlans",)


@admin.register(Link)
class LinkAdmin(BaseAdmin):
    """Admin class to manage Link objects."""

    search_fields = (
        "interface_a__name",
        "interface_a__device__name",
        "interface_b__name",
        "interface_b__device__name",
    )
    autocomplete_fields = ("interface_a", "interface_b")
    list_display = (
        "interface_a",
        "interface_b",
        "state",
        "monitoring_state",
    )
    list_filter = ("state", "monitoring_state")


@admin.register(PortLayout)
class PortLayoutAdmin(BaseAdmin):
    """Admin class to manage PortLayout objects."""

    search_fields = (
        "name",
        "label_name",
        "logical_name",
        "vendor_name",
        "device_type__model",
        "network_role__name",
    )
    list_display = (
        "name",
        "device_type",
        "network_role",
        "label_name",
        "logical_name",
        "vendor_name",
    )
    list_filter = ("device_type", "network_role")


@admin.register(VRF)
class VRFAdmin(BaseAdmin):
    """Admin class to manage VRF objects."""

    search_fields = ("name", "tenant__name")
    autocomplete_fields = ("tenant",)
    list_display = (
        "name",
        "tenant",
    )
    list_filter = ("tenant",)


@admin.register(VLAN)
class VLANAdmin(BaseAdmin):
    """Admin class to manage VLAN objects."""

    search_fields = ("name", "vid", "tenant__name", "description")
    autocomplete_fields = ("tenant",)
    list_display = (
        "vid",
        "name",
        "tenant",
        "description",
    )
    list_filter = ("tenant",)


@admin.register(Syslog)
class SyslogAdmin(BaseAdmin):
    """Admin class to manage Syslog configuration objects."""

    list_display = (
        "device",
        "get_servers",
    )

    search_fields = ("device__name", "server_list__server_address")

    def get_servers(self, obj):
        """
        Return a comma-separated list of Syslog servers bound to this device.
        """
        return ", ".join(s.server_address for s in obj.server_list.all())

    get_servers.short_description = "Syslog Servers"


@admin.register(SyslogServer)
class SyslogServerAdmin(BaseAdmin):
    """Admin class to manage Syslog Server objects."""

    list_display = ("server_address",)

    search_fields = ("server_address",)


# We need to register Netbox core models to the Admin page or we won't be able to lookup
# dynamically over the objects.
@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    search_fields = ["address"]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    search_fields = ["name"]
