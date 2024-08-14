import django_filters
from django.db.models import Q
from netbox.filtersets import ChangeLoggedModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import MultiValueCharFilter

from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession, DeviceBGPSession
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP

device_location_filterset = [
    "device__location__name",
    "device__site__name",
    "device__site__group__name",
    "device__site__region__name",
    "device__rack__name",
    "device__site__group_id",
    "device__device_type_id",
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
