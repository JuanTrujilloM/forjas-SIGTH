# external libraries imports
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

# internal application code imports
from employees.enums import EMPLOYEE_FIELD_GROUPS, EmployeeFieldGroup
from users.enums import AccessProfile


# main class
class EmployeeFieldPolicy:
    _MANAGER_GROUPS = frozenset(EmployeeFieldGroup) - {
        EmployeeFieldGroup.NOTES,
        EmployeeFieldGroup.SOCIODEMOGRAPHIC,
    }

    READABLE_GROUPS: dict[str, frozenset[EmployeeFieldGroup]] = {
        AccessProfile.TALENT_MANAGEMENT: frozenset(EmployeeFieldGroup),
        AccessProfile.GENERAL_MANAGEMENT: frozenset(EmployeeFieldGroup),
        AccessProfile.DIRECTOR: _MANAGER_GROUPS,
        AccessProfile.LEADER: _MANAGER_GROUPS,
        AccessProfile.OCCUPATIONAL_SAFETY: frozenset({
            EmployeeFieldGroup.IDENTITY,
            EmployeeFieldGroup.EMPLOYMENT,
            EmployeeFieldGroup.HEALTH_AND_RISK,
            EmployeeFieldGroup.SOCIODEMOGRAPHIC,
        }),
    }

    @staticmethod
    def readable_fields(user: AbstractBaseUser | AnonymousUser | None) -> frozenset[str]:
        if user is None or not user.is_authenticated:
            return frozenset()

        groups = EmployeeFieldPolicy.READABLE_GROUPS.get(user.profile, frozenset())

        return frozenset().union(*(EMPLOYEE_FIELD_GROUPS[group] for group in groups))

    @staticmethod
    def can_write(user: AbstractBaseUser | AnonymousUser | None) -> bool:
        return bool(
            user is not None
            and user.is_authenticated
            and user.profile == AccessProfile.TALENT_MANAGEMENT
        )

    # the admin shows every field, so only Talent Management and IT (no profile) enter
    @staticmethod
    def can_view_admin(user: AbstractBaseUser | AnonymousUser | None) -> bool:
        return bool(
            user is not None
            and user.is_active
            and user.is_staff
            and (EmployeeFieldPolicy.can_write(user) or user.profile == '')
        )
