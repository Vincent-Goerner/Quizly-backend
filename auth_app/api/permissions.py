from rest_framework import permissions
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTCookieAuthentication(authentication.BaseAuthentication):
    
    cookie_name = "access_token"

    def authenticate(self, request):
        token = request.COOKIES.get(self.cookie_name)

        if not token:
            return None

        jwt_auth = JWTAuthentication()

        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
        except (InvalidToken, TokenError):
            raise exceptions.AuthenticationFailed(
                "Invalid or expired token"
                )

        return (user, validated_token)