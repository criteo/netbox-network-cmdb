from netbox.api.pagination import OptionalLimitOffsetPagination
from netbox.config import get_config
from rest_framework.pagination import CursorPagination, _reverse_ordering


# CustomCursorPagination, we took the work made here PR https://github.com/netbox-community/netbox/pull/10764/
# However we fixed one of the issue reported by the maintainer by applying a default ordering on the viewsets
class CustomCursorPagination(CursorPagination):
    # PAGE_SIZE is not set globally by NetBox, hence we fetch it from its config
    default_page_size = get_config().PAGINATE_COUNT
    page_size_query_param = 'limit'
    ordering = "-created"

    def paginate_queryset(self, queryset, request, view=None):
        """
        Reuses the implementation from CursorPagination with minor modification to handle limit=0.
        """
        self.page_size = self.get_page_size(request)

        self.base_url = request.build_absolute_uri()
        self.ordering = self.get_ordering(request, queryset, view)

        self.cursor = self.decode_cursor(request)
        if self.cursor is None:
            (offset, reverse, current_position) = (0, False, None)
        else:
            (offset, reverse, current_position) = self.cursor

        # Cursor pagination always enforces an ordering.
        if reverse:
            queryset = queryset.order_by(*_reverse_ordering(self.ordering))
        else:
            queryset = queryset.order_by(*self.ordering)

        # If we have a cursor with a fixed position then filter by that.
        if current_position is not None:
            order = self.ordering[0]
            is_reversed = order.startswith('-')
            order_attr = order.lstrip('-')

            # Test for: (cursor reversed) XOR (queryset reversed)
            if self.cursor.reverse != is_reversed:
                kwargs = {order_attr + '__lt': current_position}
            else:
                kwargs = {order_attr + '__gt': current_position}

            queryset = queryset.filter(**kwargs)

        if self.page_size:
            # If we have an offset cursor then offset the entire page by that amount.
            # We also always fetch an extra item in order to determine if there is a
            # page following on from this one.
            results = list(queryset[offset:offset + self.page_size + 1])
            self.page = list(results[:self.page_size])
        else:
            self.page = results = list(queryset[offset:])

        # Determine the position of the final item following the page.
        if len(results) > len(self.page):
            has_following_position = True
            following_position = self._get_position_from_instance(results[-1], self.ordering)
        else:
            has_following_position = False
            following_position = None

        if reverse:
            # If we have a reverse queryset, then the query ordering was in reverse
            # so we need to reverse the items again before returning them to the user.
            self.page = list(reversed(self.page))

            # Determine next and previous positions for reverse cursors.
            self.has_next = (current_position is not None) or (offset > 0)
            self.has_previous = has_following_position
            if self.has_next:
                self.next_position = current_position
            if self.has_previous:
                self.previous_position = following_position
        else:
            # Determine next and previous positions for forward cursors.
            self.has_next = has_following_position
            self.has_previous = (current_position is not None) or (offset > 0)
            if self.has_next:
                self.next_position = following_position
            if self.has_previous:
                self.previous_position = current_position

        # Display page controls in the browsable API if there is more
        # than one page.
        if (self.has_previous or self.has_next) and self.template is not None:
            self.display_page_controls = True

        return self.page

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size < 0:
                    raise ValueError()
                # Enforce maximum page size, if defined
                MAX_PAGE_SIZE = get_config().MAX_PAGE_SIZE
                if MAX_PAGE_SIZE:
                    return MAX_PAGE_SIZE if page_size == 0 else min(page_size, MAX_PAGE_SIZE)
                return page_size
            except (KeyError, ValueError):
                pass

        return self.default_page_size


PAGINATORS = {
    'limit_offset': OptionalLimitOffsetPagination,  # Default per settings.DEFAULT_PAGINATION_CLASS
    'cursor': CustomCursorPagination,
}
