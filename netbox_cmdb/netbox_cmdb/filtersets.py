import django_filters
from django.db.models import Q
from netbox.filtersets import ChangeLoggedModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from tenancy.models import Tenant
from utilities.filters import MultiValueCharFilter

from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession


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
        label="device",
    )

    local_address = MultiValueCharFilter(
        method="filter_peer_address",
        label="local_address",
    )

    class Meta:
        model = BGPSession
        exclude = ["__all__"]
        fields = ["id", "device", "local_address"]

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

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(peer_a__device__name__icontains=value) | Q(peer_b__device__name__icontains=value)
        ).distinct()


class BGPPeerGroupFilterSet(ChangeLoggedModelFilterSet):
    """BGP Session filterset."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = BGPPeerGroup
        fields = ["id", "local_asn", "remote_asn", "device", "name"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) | Q(name__icontains=value)
        ).distinct()
