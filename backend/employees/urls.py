# external libraries imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# internal application code imports
from .views import (
    CostCenterViewSet,
    EmployeeViewSet,
    IndicatorExportView,
    IndicatorView,
    MonthlyCutEmployeeViewSet,
    MonthlyCutViewSet,
    PositionViewSet,
)

# main code
router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employees.employee')
router.register('positions', PositionViewSet, basename='employees.position')
router.register('cost-centers', CostCenterViewSet, basename='employees.cost_center')
router.register('monthly-cuts', MonthlyCutViewSet, basename='employees.monthly_cut')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'monthly-cuts/<int:cut_pk>/employees/',
        MonthlyCutEmployeeViewSet.as_view({'get': 'list'}),
        name='employees.monthly_cut_employees',
    ),
    path('indicators/', IndicatorView.as_view(), name='employees.indicators'),
    path('indicators/export/', IndicatorExportView.as_view(), name='employees.indicators_export'),
]
