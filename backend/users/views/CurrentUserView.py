# external libraries imports
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# internal application code imports
from users.serializers import UserSerializer


# main class
class CurrentUserView(APIView):
    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)
