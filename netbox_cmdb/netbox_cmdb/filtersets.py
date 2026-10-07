import django_filters
from django.db.models import Q
from netaddr import AddrFormatError, IPNetwork
from netbox.filtersets import ChangeLoggedModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import MultiValueCharFilter

from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession, DeviceBGPSession
from netbox_cmdb.models.interface import Link, LogicalInterface
from netbox_cmdb.models.management_route import ManagementRoute
from netbox_cmdb.models.ntp import NTP
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP
from netbox_cmdb.models.sonic_role_mapping import SonicRoleMapping
from netbox_cmdb.models.syslog import Syslog
from netbox_cmdb.models.tacacs import Tacacs

device_location_filterset = [
    "device__location__name",
    "device__site__name",
    "device__site__group__name",
    "device__site__region__name",
    "device__rack__name",
    "device__site__group_id",
    "device__device_type_id",
]

# Same filters for models attached to a device through their parent interface
# (e.g. logical interfaces).
parent_interface_device_location_filterset = [
    f"parent_interface__{field}" for field in device_location_filterset
]

# Same filters for models attached to a device through a logical interface
# (e.g. management routes).
logical_interface_device_location_filterset = [
    f"logical_interface__parent_interface__{field}" for field in device_location_filterset
]


class ASNFilterSet(ChangeLoggedModelFilterSet):
    """AS number filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = ASN
        fields = ["id", "number", "organization_name"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(number__icontains=value) | Q(organization_name__icontains=value)
        ).distinct()


class BGPSessionFilterSet(ChangeLoggedModelFilterSet, TenancyFilterSet):
    """BGP Session filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    device = MultiValueCharFilter(
        method="filter_peer_device",
        label="device*",
    )

    device__rack__name = MultiValueCharFilter(
        method="filter_device_location",
        label="device__rack__name",
    )

    device__location__name = MultiValueCharFilter(
        method="filter_device_location",
        label="device__location__name",
    )

    device__site__name = MultiValueCharFilter(
        method="filter_device_location",
        label="device__site__name",
    )

    device__site__group__name = MultiValueCharFilter(
        method="filter_device_location",
        label="device__site__group__name",
    )

    device__site__group_id = MultiValueCharFilter(
        method="filter_device_location",
        label="device__site__group",
    )

    device__site__region__name = MultiValueCharFilter(
        method="filter_device_location",
        label="device__site__region__name",
    )

    device__device_type_id = MultiValueCharFilter(
        method="filter_device_type",
        label="device__device_type",
    )

    local_address = MultiValueCharFilter(
        method="filter_peer_address",
        label="local_address",
    )

    class Meta:
        model = BGPSession
        exclude = ["__all__"]
        fields = [
            "id",
            "device",
            "local_address",
            "state",
            "monitoring_state",
        ] + device_location_filterset

    def filter_peer_address(self, queryset, name, value):
        if len(value) > 2:
            # a BGP session can't have more than 2 peers
            return queryset.none()

        for val in value:
            # we chain the querysets to get a single BGP session when 2 values are passed
            queryset = queryset.filter(
                Q(peer_a__local_address__address__net_in=[val])
                | Q(peer_b__local_address__address__net_in=[val])
            )
        return queryset

    def filter_peer_device(self, queryset, name, value):
        if len(value) > 2:
            # a BGP session can't have more than 2 devices
            return queryset.none()

        for val in value:
            # we chain the querysets to get a single BGP session when 2 values are passed
            queryset = queryset.filter(Q(peer_a__device__name=val) | Q(peer_b__device__name=val))
        return queryset

    def filter_device_location(self, queryset, name, value):
        if len(value) > 2:
            # a BGP session can't have more than 2 devices
            return queryset.none()

        for val in value:
            # we chain the querysets to get a single BGP session when 2 values are passed
            peer_a_lookup = {f"peer_a__{name}": val}
            peer_b_lookup = {f"peer_b__{name}": val}

            queryset = queryset.filter(Q(**peer_a_lookup) | Q(**peer_b_lookup))
        return queryset

    def filter_device_type(self, queryset, name, value):
        if len(value) > 2:
            # a BGP session can't have more than 2 devices
            return queryset.none()

        for val in value:
            # we chain the querysets to get a single BGP session when 2 values are passed
            peer_a_lookup = {f"peer_a__{name}": val}
            peer_b_lookup = {f"peer_b__{name}": val}

            queryset = queryset.filter(Q(**peer_a_lookup) | Q(**peer_b_lookup)).distinct()
        return queryset

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(peer_a__device__name__icontains=value)
            | Q(peer_a__description__icontains=value)
            | Q(peer_b__device__name__icontains=value)
            | Q(peer_b__description__icontains=value)
        ).distinct()


class DeviceBGPSessionFilterSet(ChangeLoggedModelFilterSet):
    """Device BGP Session filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = DeviceBGPSession
        fields = ["id", "device__name", "local_address", "local_asn"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) | Q(description__icontains=value)
        ).distinct()


class RoutePolicyFilterSet(ChangeLoggedModelFilterSet):
    """Route Policy filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = RoutePolicy
        fields = ["id", "device__id", "device__name", "name"] + device_location_filterset

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(name__icontains=value)


class BGPPeerGroupFilterSet(ChangeLoggedModelFilterSet):
    """BGP Session filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = BGPPeerGroup
        fields = ["id", "local_asn", "remote_asn", "device", "name"] + device_location_filterset

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) | Q(name__icontains=value)
        ).distinct()


class LinkFilterSet(ChangeLoggedModelFilterSet):
    """Link filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = Link
        fields = [
            "id",
            "interface_a__device__name",
            "interface_b__device__name",
            "state",
            "monitoring_state",
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(interface_a__name__icontains=value)
            | Q(interface_a__device__name__icontains=value)
            | Q(interface_b__name__icontains=value)
            | Q(interface_b__device__name__icontains=value)
        ).distinct()


class LogicalInterfaceFilterSet(ChangeLoggedModelFilterSet):
    """Logical interface filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = LogicalInterface
        fields = [
            "id",
            "parent_interface__device__name",
            "parent_interface__name",
            "type",
            "mode",
            "state",
            "monitoring_state",
            "use_ipv6_link_local_only",
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(parent_interface__name__icontains=value)
            | Q(parent_interface__device__name__icontains=value)
            | Q(description__icontains=value)
        ).distinct()


class ManagementRouteFilterSet(ChangeLoggedModelFilterSet):
    """Management route filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = ManagementRoute
        fields = [
            "id",
            "logical_interface__parent_interface__device__name",
            "logical_interface__parent_interface__name",
            "kind",
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        query = (
            Q(logical_interface__parent_interface__name__icontains=value)
            | Q(logical_interface__parent_interface__device__name__icontains=value)
            | Q(description__icontains=value)
        )
        try:
            # a prefix or an address: the routes whose prefix contains it
            query |= Q(prefix__net_contains_or_equals=str(IPNetwork(value.strip())))
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(query).distinct()


class SNMPFilterSet(ChangeLoggedModelFilterSet):
    """AS number filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = SNMP
        fields = ["device"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(device__name__icontains=value)).distinct()


class NTPFilterSet(ChangeLoggedModelFilterSet):
    """NTP filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = NTP
        fields = ["device"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(device__name__icontains=value)).distinct()


class SyslogFilterSet(ChangeLoggedModelFilterSet):
    """Syslog filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = Syslog
        fields = ["device"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(device__name__icontains=value)).distinct()


class TacacsFilterSet(ChangeLoggedModelFilterSet):
    """TACACS filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = Tacacs
        fields = ["device"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(device__name__icontains=value)).distinct()


class SonicRoleMappingFilterSet(ChangeLoggedModelFilterSet):
    """SONiC Role Mapping filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = SonicRoleMapping
        fields = ["device_role", "sonic_type"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(device_role__name__icontains=value)).distinct()
