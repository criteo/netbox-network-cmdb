from netbox_cmdb.api.snmp.serializers import SNMPCommunitySerializer, SNMPSerializer
from netbox_cmdb.models.snmp import SNMP, SNMPCommunity
from netbox_cmdb.choices import SNMPCommunityType
from netbox_cmdb.tests.common import BaseTestCase


class SNMPCommunitySerializerCreate(BaseTestCase):
    def test_create(self):
        data = {"name": "my_comm1", "community": "my_community", "type": "readonly"}
        snmpcommunity_serializer = SNMPCommunitySerializer(data=data)
        assert snmpcommunity_serializer.is_valid() == True
        snmpcommunity_serializer.save()

        community1 = SNMPCommunity.objects.get(name="my_comm1")

        assert community1.community == "my_community"
        assert community1.type == SNMPCommunityType.RO

        data = {
            "device": self.device1.pk,
            "community_list": [community1.pk],
            "location": "my_location",
            "contact": "my_team",
        }

        snmp_serializer = SNMPSerializer(data=data)
        assert snmp_serializer.is_valid() == True
        snmp_serializer.save()

        conf = SNMP.objects.get(device__name=self.device1.name)

        assert conf.location == "my_location"
        assert conf.contact == "my_team"
        assert conf.community_list.all()[0] == community1
        assert conf.device == self.device1
