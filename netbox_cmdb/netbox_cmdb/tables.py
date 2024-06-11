"""Tables."""

import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from netbox_cmdb.models.bgp import ASN, BGPPeerGroup, BGPSession
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity


class ASNTable(NetBoxTable):
    number = tables.LinkColumn()
    organization_name = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ASN
        fields = ("pk", "number", "organization_name")


class BGPSessionTable(NetBoxTable):
    id = tables.Column(linkify=True)
    peer_a__device = tables.Column(verbose_name="Device A")
    peer_a__description = tables.Column(verbose_name="Device A description")
    peer_a__local_address = tables.Column(verbose_name="Device A local address")
    peer_b__device = tables.Column(verbose_name="Device B")
    peer_b__description = tables.Column(verbose_name="Device B description")
    peer_b__local_address = tables.Column(verbose_name="Device B local address")
    state = columns.ChoiceFieldColumn()
    monitoring_state = columns.ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = BGPSession
        fields = (
            "id",
            "peer_a__device",
            "peer_a__description",
            "peer_a__local_address",
            "peer_b__device",
            "peer_b__description",
            "peer_b__local_address",
            "state",
            "monitoring_state",
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


class SNMPTable(NetBoxTable):
    device = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = SNMP
        fields = ("device", "community_list", "location", "contact")


class SNMPCommunityTable(NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = SNMPCommunity
        fields = ("name", "community", "type")
