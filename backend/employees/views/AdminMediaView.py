# external libraries imports
from django.http import FileResponse, Http404, HttpRequest
from django.views import View

# internal application code imports
from employees.services import EmployeePhotoService
from users.access import EmployeeFieldPolicy


# main class
# Serves uploaded files only to the accounts that may enter the employee admin (6.3), so
# the admin's own links to a photo work. There is no public /media/ route.
class AdminMediaView(View):
    def get(self, request: HttpRequest, path: str) -> FileResponse:
        if not EmployeeFieldPolicy.can_view_admin(request.user):
            raise Http404

        return EmployeePhotoService.response(path)
