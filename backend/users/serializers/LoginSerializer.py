# external libraries imports
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, Throttled

# internal application code imports
from users.services import LoginAttemptService
from users.validators import CorporateEmailValidator


# main class
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[CorporateEmailValidator()])
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs: dict) -> dict:
        request = self.context.get('request')

        # checked before the password, or a locked attacker would still learn when it is right
        if LoginAttemptService.is_locked(request, attrs['email']):
            raise Throttled(
                detail='Demasiados intentos fallidos. Espera 15 minutos y vuelve a intentarlo.'
            )

        user = authenticate(
            request=request,
            username=attrs['email'],
            password=attrs['password'],
        )

        if user is None:
            LoginAttemptService.register_failure(request, attrs['email'])
            raise AuthenticationFailed('Correo o contraseña incorrectos.')

        LoginAttemptService.register_success(request, attrs['email'])
        attrs['user'] = user

        return attrs
