# external libraries imports
from django_filters import rest_framework as django_filters
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request

# internal application code imports
from users.access.EmployeeFieldPolicy import EmployeeFieldPolicy


# main code
def _readable_by(request: Request | None) -> frozenset[str]:
    return EmployeeFieldPolicy.readable_fields(getattr(request, 'user', None))


def _root_field(lookup: str) -> str:
    return lookup.lstrip('^=@$-').split('__')[0]


# filters on hidden columns are dropped: stratum=1 would reveal the stratum without showing it
class EmployeeFieldFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        readable = _readable_by(self.request)

        for name in list(self.filters):
            if _root_field(self.filters[name].field_name) not in readable:
                del self.filters[name]


class EmployeeFieldOrderingFilter(OrderingFilter):
    def get_valid_fields(self, queryset, view, context=None) -> list:
        readable = _readable_by((context or {}).get('request'))

        return [
            (field, label)
            for field, label in super().get_valid_fields(queryset, view, context)
            if _root_field(field) in readable
        ]


class EmployeeFieldSearchFilter(SearchFilter):
    def get_search_fields(self, view, request: Request) -> list[str]:
        readable = _readable_by(request)

        return [
            field for field in super().get_search_fields(view, request) or []
            if _root_field(field) in readable
        ]
