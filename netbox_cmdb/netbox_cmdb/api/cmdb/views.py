from dcim.models import Device, Site
from django.db import transaction
from django.http import StreamingHttpResponse
from drf_yasg.utils import swagger_auto_schema
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from netbox_cmdb.helpers import cleaning


class DeviceDecommissioningBaseSerializer(serializers.Serializer):
    device_name = serializers.CharField()


class DeviceCMDBDecommissioningAPIView(APIView):

    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    @swagger_auto_schema(
        request_body=DeviceDecommissioningBaseSerializer,
        responses={
            status.HTTP_200_OK: "Objects related to device have been deleted successfully",
            status.HTTP_400_BAD_REQUEST: "Bad Request: Device name is required",
            status.HTTP_404_NOT_FOUND: "Bad Request: Device not found",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error: Something went wrong on the server",
        },
    )
    def delete(self, request):
        device_name = request.data.get("device_name", None)
        if device_name is None:
            return Response(
                {"error": "device_name is required"}, status=status.HTTP_400_BAD_REQUEST
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
            {
                "message": f"CMDB cleaned for {device_name}",
                "deleted": deleted,
            },
            status=status.HTTP_200_OK,
        )


class DeviceDecommissioningAPIView(APIView):

    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    @swagger_auto_schema(
        request_body=DeviceDecommissioningBaseSerializer,
        responses={
            status.HTTP_200_OK: "Objects related to device have been deleted successfully",
            status.HTTP_400_BAD_REQUEST: "Bad Request: Device name is required",
            status.HTTP_404_NOT_FOUND: "Bad Request: Device not found",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error: Something went wrong on the server",
        },
    )
    def delete(self, request):
        device_name = request.data.get("device_name", None)
        if device_name is None:
            return Response(
                {"error": "device_name is required"}, status=status.HTTP_400_BAD_REQUEST
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
                for device in devices:
                    device.delete()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "message": f"{device_name} decommissionned",
                "deleted": deleted,
            },
            status=status.HTTP_200_OK,
        )


class SiteDecommissioningSerializer(serializers.Serializer):
    site_name = serializers.CharField()


class SiteDecommissioningAPIView(APIView):

    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    @swagger_auto_schema(
        request_body=SiteDecommissioningSerializer,
        responses={
            status.HTTP_200_OK: "Site have been deleted successfully",
            status.HTTP_400_BAD_REQUEST: "Bad Request: Site name is required",
            status.HTTP_404_NOT_FOUND: "Bad Request: Site not found",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error: Something went wrong on the server",
        },
    )
    def delete(self, request):
        site_name = request.data.get("site_name", None)
        if site_name is None:
            return Response({"error": "site_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            site = Site.objects.get(name=site_name)
        except Site.DoesNotExist:
            return Response({"error": "site not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(
                {"error": "internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        devices = Device.objects.filter(site=site.id)

        def _start():
            CHUNK_SIZE = 20
            device_ids = [dev.id for dev in devices]
            for i in range(0, len(device_ids), CHUNK_SIZE):
                chunk = device_ids[i : i + CHUNK_SIZE]
                try:
                    with transaction.atomic():
                        cleaning.clean_cmdb_for_devices(chunk)
                        for dev in devices[i : i + CHUNK_SIZE]:
                            dev.delete()
                    yield f'{{"deleted": {[dev.name for dev in devices[i:i+CHUNK_SIZE]]}}}\n\n'

                except Exception as e:
                    StreamingHttpResponse.status_code = 500
                    msg = {"error": str(e)}
                    yield f"{msg}\n\n"
                    return

            try:
                with transaction.atomic():
                    cleaning.clean_site_topology(site)
                    yield "{{'message': 'topology cleaned'}}\n\n"
            except Exception as e:
                StreamingHttpResponse.status_code = 500
                msg = {"error": str(e)}
                yield f"{msg}\n\n"
                return

            msg = {
                "message": f"site {site_name} has been deleted successfully",
            }
            yield f"{msg}\n\n"

        return StreamingHttpResponse(_start(), content_type="text/plain")
