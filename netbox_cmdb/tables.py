"""Tables."""
import django_tables2 as tables
from netbox.tables import NetBoxTable

from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession


class ASNTable(NetBoxTable):
    number = tables.LinkColumn()
    organization_name = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ASN
        fields = ("pk", "number", "organization_name")


class BGPSessionTable(NetBoxTable):
    peer_a = tables.Column()
    peer_b = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = BGPSession
        fields = (
            "pk",
            "peer_a",
            "peer_b",
        )


class BGPPeerGroupTable(NetBoxTable):
    device = tables.LinkColumn()
    name = tables.LinkColumn()
    asn = tables.Column()
    route_policy_in = tables.Column()
    route_policy_out = tables.Column()
    maximum_prefixes = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = BGPPeerGroup
        fields = (
            "pk",
            "name",
            "local_asn",
            "remote_asn",
            "route_policy_in",
            "route_policy_out",
            "maximum_prefixes",
        )
