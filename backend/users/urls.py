# external libraries imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# internal application code imports
from .views import (
    CsrfTokenView,
    CurrentUserView,
    DivisionViewSet,
    LoginView,
    LogoutView,
    SectionViewSet,
)

# main code
router = DefaultRouter()
router.register('divisions', DivisionViewSet, basename='users.division')
router.register('sections', SectionViewSet, basename='users.section')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/csrf/', CsrfTokenView.as_view(), name='users.auth_csrf'),
    path('auth/login/', LoginView.as_view(), name='users.auth_login'),
    path('auth/logout/', LogoutView.as_view(), name='users.auth_logout'),
    path('auth/me/', CurrentUserView.as_view(), name='users.auth_current_user'),
]
