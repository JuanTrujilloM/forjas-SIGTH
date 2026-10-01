# external libraries imports
from django.http import FileResponse, Http404, HttpRequest
from django.views import View

# internal application code imports
from employees.services import EmployeePhotoService
from users.access import EmployeeFieldPolicy


# main class
# there is no public /media/ route: only accounts allowed in the employee admin get files
class AdminMediaView(View):
    def get(self, request: HttpRequest, path: str) -> FileResponse:
        if not EmployeeFieldPolicy.can_view_admin(request.user):
            raise Http404

        return EmployeePhotoService.response(path)
