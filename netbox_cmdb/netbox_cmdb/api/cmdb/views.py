from dcim.models import Device
from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from netbox_cmdb.helpers import cleaning
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
            status.HTTP_404_NOT_FOUND: "Bad Request: Device not found",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error: Something went wrong on the server",
        },
    )
    def post(self, request):
        device_name = request.data.get("device_name", None)
        if device_name is None:
            return Response(
                {"error": "Device name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        devices = Device.objects.filter(name=device_name)
        device_ids = [dev.id for dev in devices]
        if not device_ids:
            return Response(
                {"error": "no matching devices found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                deleted = cleaning.clean_cmdb_for_devices(device_ids)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"message": f"Objects related to device {device_name} have been deleted successfully: {deleted}"},
            status=status.HTTP_200_OK,
        )
