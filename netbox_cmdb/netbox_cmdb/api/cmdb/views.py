from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox_cmdb.models.bgp import BGPPeerGroup, BGPSession, DeviceBGPSession
from netbox_cmdb.models.bgp_community_list import BGPCommunityList
from netbox_cmdb.models.prefix_list import PrefixList
from netbox_cmdb.models.route_policy import RoutePolicy
from netbox_cmdb.models.snmp import SNMP


class DeleteAllCMDBObjectsRelatedToDeviceSerializer(serializers.Serializer):
    device_name = serializers.CharField()


class DeleteAllCMDBObjectsRelatedToDevice(APIView):

    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    @swagger_auto_schema(
        request_body=DeleteAllCMDBObjectsRelatedToDeviceSerializer,
        responses={
            status.HTTP_200_OK: "Objects related to device have been deleted successfully",
            status.HTTP_400_BAD_REQUEST: "Bad Request: Device name is required",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error: Something went wrong on the server",
        },
    )
    def post(self, request):
        device_name = request.data.get("device_name", None)
        if device_name is None:
            return Response(
                {"error": "Device name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Delete objects in reverse order of dependencies
                BGPSession.objects.filter(
                    Q(peer_a__device__name=device_name) | Q(peer_b__device__name=device_name)
                ).delete()
                DeviceBGPSession.objects.filter(device__name=device_name).delete()
                BGPPeerGroup.objects.filter(device__name=device_name).delete()
                RoutePolicy.objects.filter(device__name=device_name).delete()
                PrefixList.objects.filter(device__name=device_name).delete()
                BGPCommunityList.objects.filter(device_name=device_name).delete()
                SNMP.objects.filter(device__name=device_name).delete()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"message": f"Objects related to device {device_name} have been deleted successfully"},
            status=status.HTTP_200_OK,
        )
