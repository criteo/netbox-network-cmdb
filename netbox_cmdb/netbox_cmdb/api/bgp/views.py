from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django_pglocks import advisory_lock
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from netbox.api.viewsets.mixins import ObjectValidationMixin
from netbox_cmdb import filtersets
from netbox_cmdb.api.bgp.serializers import (
    AvailableAsnSerializer,
    BGPASNSerializer,
    BGPGlobalSerializer,
    BGPPeerGroupSerializer,
    BGPSessionSerializer,
    DeviceBGPSessionSerializer,
)
from netbox_cmdb.api.viewsets import CustomNetBoxModelViewSet
from netbox_cmdb.filtersets import (
    ASNFilterSet,
    BGPSessionFilterSet,
    DeviceBGPSessionFilterSet,
)
from netbox_cmdb.models.bgp import (
    ASN,
    BGPGlobal,
    BGPPeerGroup,
    BGPSession,
    DeviceBGPSession,
)


class ASNViewSet(CustomNetBoxModelViewSet):
    queryset = ASN.objects.all()
    serializer_class = BGPASNSerializer
    filterset_class = ASNFilterSet


class AvailableASNsView(ObjectValidationMixin, APIView):
    queryset = ASN.objects.all()

    @swagger_auto_schema(
        request_body=AvailableAsnSerializer,
        responses={201: BGPASNSerializer},
    )
    def post(self, request):
        self.queryset = self.queryset.restrict(request.user, "add")

        # Validate requested ASN
        serializer = AvailableAsnSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(raise_exception=True)

        min_asn, max_asn = (
            serializer.validated_data["min_asn"],
            serializer.validated_data["max_asn"],
        )
        if min_asn > max_asn:
            raise ValidationError(detail="Min ASN can't be inferior to max ASN.")

        data = self._create_next_available_asn(
            min_asn, max_asn, serializer.validated_data["organization_name"]
        )
        return Response(data, status=status.HTTP_201_CREATED)

    @advisory_lock("create-next-available-asn")
    def _create_next_available_asn(self, min_asn, max_asn, organization_name):
        available_asns = ASN().get_available_asns(min_asn, max_asn)
        if not len(available_asns) > 0:
            raise ValidationError(detail="No ASN available within this range.")

        serializer = BGPASNSerializer(
            data={
                "number": available_asns[0],
                "organization_name": organization_name,
            }
        )

        serializer.is_valid(raise_exception=True)

        # Create the new ASN
        try:
            with transaction.atomic():
                created = serializer.save()
                self._validate_objects(created)
        except ObjectDoesNotExist:
            raise PermissionDenied()
        return serializer.data


class BGPGlobalViewSet(CustomNetBoxModelViewSet):
    queryset = BGPGlobal.objects.all()
    serializer_class = BGPGlobalSerializer
    filterset_fields = ["device__name"] + filtersets.device_location_filterset


class BGPSessionsViewSet(CustomNetBoxModelViewSet):
    queryset = BGPSession.objects.all()
    serializer_class = BGPSessionSerializer
    filterset_class = BGPSessionFilterSet


class DeviceBGPSessionsViewSet(CustomNetBoxModelViewSet):
    queryset = DeviceBGPSession.objects.all()
    serializer_class = DeviceBGPSessionSerializer
    filterset_class = DeviceBGPSessionFilterSet


class BGPPeerGroupViewSet(CustomNetBoxModelViewSet):
    queryset = BGPPeerGroup.objects.all()
    serializer_class = BGPPeerGroupSerializer
    filterset_fields = [
        "id",
        "name",
        "device__id",
        "device__name",
    ] + filtersets.device_location_filterset
