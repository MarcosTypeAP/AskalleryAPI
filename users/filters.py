"""User filters."""


from rest_framework import filters


class CustomSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        if view.action == 'list':
            return ['username', 'first_name', 'last_name']
        return super().get_search_fields(view, request)
