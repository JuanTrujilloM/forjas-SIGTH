# external libraries imports
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

# internal application code imports
from employees.views import AdminMediaView

# main code
media_prefix = settings.MEDIA_URL.lstrip('/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{media_prefix}<path:path>', AdminMediaView.as_view(), name='employees.admin_media'),
    path('api/', include('users.urls')),
    path('api/', include('employees.urls')),
]
