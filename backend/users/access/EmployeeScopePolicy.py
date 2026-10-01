# external libraries imports
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import QuerySet

# internal application code imports
from users.enums import AccessProfile


# main class
class EmployeeScopePolicy:
    FULL_SCOPE_PROFILES = frozenset({
        AccessProfile.TALENT_MANAGEMENT,
        AccessProfile.GENERAL_MANAGEMENT,
        AccessProfile.OCCUPATIONAL_SAFETY,
    })

    @staticmethod
    def sees_every_employee(user: AbstractBaseUser | AnonymousUser) -> bool:
        return getattr(user, 'profile', '') in EmployeeScopePolicy.FULL_SCOPE_PROFILES

    @staticmethod
    def scope(
        user: AbstractBaseUser | AnonymousUser,
        queryset: QuerySet,
        division_lookup: str = 'division',
        section_lookup: str = 'section',
    ) -> QuerySet:
        if user is None or not user.is_authenticated:
            return queryset.none()

        if EmployeeScopePolicy.sees_every_employee(user):
            return queryset

        if user.profile == AccessProfile.DIRECTOR and user.division_id is not None:
            return queryset.filter(**{f'{division_lookup}_id': user.division_id})

        if user.profile == AccessProfile.LEADER:
            section_ids = user.section_assignments.values('section_id')
            return queryset.filter(**{f'{section_lookup}_id__in': section_ids})

        # IT (no profile) works from the admin; a director with no division sees nobody
        return queryset.none()
