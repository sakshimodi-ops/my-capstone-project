from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from myadmin.models import User

class CustomJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split()

            if prefix != "Bearer":
                return None

            decoded = AccessToken(token)
            user_id = decoded.get('user_id')

            user = User.objects.get(user_id=user_id)

            return (user, None)

        except Exception as e:
            raise AuthenticationFailed("Invalid or expired token")