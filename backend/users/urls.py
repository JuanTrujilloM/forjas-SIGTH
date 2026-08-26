# external libraries imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# main code
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
