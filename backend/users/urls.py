# external libraries imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# internal application code imports
from .views.SystemHealthView import SystemHealthView

# main code
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('health/', SystemHealthView.as_view(), name='users.system_health'),
]
