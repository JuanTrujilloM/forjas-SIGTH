# external libraries imports
from rest_framework.permissions import SAFE_METHODS, BasePermission

# internal application code imports
from users.access.EmployeeFieldPolicy import EmployeeFieldPolicy


# main class
class EmployeeWritePermission(BasePermission):
    message = 'Solo Talento Humano puede modificar la información de los empleados.'

    def has_permission(self, request, view) -> bool:
        return request.method in SAFE_METHODS or EmployeeFieldPolicy.can_write(request.user)
