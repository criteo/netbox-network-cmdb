"""Management route serializers."""

from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from netbox_cmdb.api.interface.serializers import NestedLogicalInterfaceSerializer
from netbox_cmdb.models.management_route import ManagementRoute, management_route_errors


class ManagementRouteSerializer(ModelSerializer):
    logical_interface = NestedLogicalInterfaceSerializer()
    display = SerializerMethodField(read_only=True)

    class Meta:
        model = ManagementRoute
        fields = "__all__"

    def get_display(self, obj):
        return str(obj)

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks.

        Duplicates are reported by validate(), with the same message as the plugin UI.
        """
        return []

    def validate(self, attrs):
        # A PATCH only carries the changed fields, the others come from the stored route.
        def current(field):
            if field in attrs:
                return attrs[field]
            return getattr(self.instance, field, None)

        errors = management_route_errors(
            current("logical_interface"),
            current("kind"),
            current("prefix"),
            current("next_hop"),
            exclude_pk=getattr(self.instance, "pk", None),
        )
        if errors:
            raise ValidationError(errors)
        return attrs
