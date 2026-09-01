# external libraries imports
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


# main class
# touches no table on purpose: a failure here means the URL or CORS is wrong, not the database
class SystemHealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response({'status': 'ok', 'service': 'SIGTH API'})
