# external libraries imports
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

# internal application code imports
from users.validators import CorporateEmailValidator


# main class
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[CorporateEmailValidator()])
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs: dict) -> dict:
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )
        
        if user is None:
            raise AuthenticationFailed('Correo o contraseña incorrectos.')

        attrs['user'] = user

        return attrs
