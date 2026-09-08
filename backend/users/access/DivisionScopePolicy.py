# external libraries imports
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import QuerySet


# main class
# Single point that decides WHICH RECORDS a user may see (6.3). The scope is by row, not
# by column: a user sees the records of their own division, and sees every field of them.
class DivisionScopePolicy:
    @staticmethod
    def sees_every_division(user: AbstractBaseUser | AnonymousUser) -> bool:
        division = getattr(user, 'division', None)
        return bool(division and division.has_full_employee_access)

    @staticmethod
    def scope(
        user: AbstractBaseUser | AnonymousUser,
        queryset: QuerySet,
        division_lookup: str = 'division',
    ) -> QuerySet:
        if user is None or not user.is_authenticated:
            return queryset.none()

        if DivisionScopePolicy.sees_every_division(user):
            return queryset

        division_id = getattr(user, 'division_id', None)

        # An account with no division belongs to IT, which works from the Django admin
        # and not from the API. Returning nothing is the safe reading of "no division".
        if division_id is None:
            return queryset.none()

        return queryset.filter(**{f'{division_lookup}_id': division_id})
