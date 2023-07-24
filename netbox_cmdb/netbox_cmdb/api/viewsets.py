from netbox.api.viewsets import NetBoxModelViewSet

from netbox_cmdb.api.pagination import PAGINATORS


class CustomNetBoxModelViewSet(NetBoxModelViewSet):
    # we need to specify the ordering here as well since we can't fallback on the
    # CursorPagination object ordering value, until the following PR is merged:
    # https://github.com/encode/django-rest-framework/pull/8954
    ordering = "-created"

    # Code taken from https://github.com/netbox-community/netbox/pull/10764
    @property
    def paginator(self):
        """
        Allow the request to designate the paginator class per the pagination_mode parameter.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            elif mode := self.request.query_params.get("pagination_mode"):
                self._paginator = PAGINATORS.get(mode, self.pagination_class)()
            else:
                self._paginator = self.pagination_class()
        return self._paginator
