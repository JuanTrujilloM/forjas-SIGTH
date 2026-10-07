# external libraries imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# internal application code imports
from .views import CostCenterViewSet, EmployeeViewSet, PositionViewSet

# main code
router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employees.employee')
router.register('positions', PositionViewSet, basename='employees.position')
router.register('cost-centers', CostCenterViewSet, basename='employees.cost_center')

urlpatterns = [
    path('', include(router.urls)),
]
