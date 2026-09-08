# external libraries imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# internal application code imports
from .views import CsrfTokenView, CurrentUserView, LoginView, LogoutView

# main code
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('auth/csrf/', CsrfTokenView.as_view(), name='users.auth_csrf'),
    path('auth/login/', LoginView.as_view(), name='users.auth_login'),
    path('auth/logout/', LogoutView.as_view(), name='users.auth_logout'),
    path('auth/me/', CurrentUserView.as_view(), name='users.auth_current_user'),
]
