# external libraries imports
from django.contrib import admin
from django.urls import include, path

# main code
# no version prefix: the frontend is the only client and ships with the backend
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('employees.urls')),
]
