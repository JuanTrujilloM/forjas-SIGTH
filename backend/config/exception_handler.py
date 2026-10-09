# external libraries imports
from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


# main code
# Django's 404 text is in English and names the model; NotFound's default detail is translated
def exception_handler(exc: Exception, context: dict) -> Response | None:
    if isinstance(exc, Http404):
        exc = NotFound()
    return drf_exception_handler(exc, context)
