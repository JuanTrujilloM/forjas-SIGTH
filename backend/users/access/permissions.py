# external libraries imports
from rest_framework.permissions import SAFE_METHODS, BasePermission

# internal application code imports
from users.access.EmployeeFieldPolicy import EmployeeFieldPolicy


# main class
class ContractAlertPermission(BasePermission):
    message = 'Solo Talento Humano ve los vencimientos de contrato.'

    def has_permission(self, request, view) -> bool:
        return EmployeeFieldPolicy.can_view_contract_alerts(request.user)


class EmployeeWritePermission(BasePermission):
    message = 'Solo Talento Humano puede modificar la información de los empleados.'

    def has_permission(self, request, view) -> bool:
        return request.method in SAFE_METHODS or EmployeeFieldPolicy.can_write(request.user)
