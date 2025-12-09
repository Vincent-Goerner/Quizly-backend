from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegistrationSerializer, LoginTokenObtainPairSerializer
from .permissions import IsOwner


class RegistrationView(APIView):
    """
    API endpoint for creating new user accounts. Allows public access and
    delegates validation and creation logic to the `RegistrationSerializer`.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Processes registration data, validates it using the serializer,
        creates the user on success, and returns appropriate responses for
        successful creation or validation errors.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({'detail': 'User created successfully!'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView): 
    """
    View that authenticates a user via username and password and returns
    JWT access and refresh tokens stored securely in HTTP-only cookies.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Validates login credentials using `LoginTokenObtainPairSerializer`.
        On success, generates JWT tokens, sets them as secure cookies, and
        returns user information. Returns 401 on validation failure.
        """
        serializer = LoginTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            response = Response(
                {
                    "detail": "Login successfully!",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_200_OK,
            )
            
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="Lax"
            )

            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="Lax"
            )

            return response
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    

class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get("refresh_token")

        if refresh is None:
            return Response(
                {'detail': 'Refresh token not found!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data={'refresh':refresh})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {'detail': 'Refresh token invalid!'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get("access")

        response = Response(
            {
                'detail': 'Token refreshed',
                'access': access_token
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response
    

class LogoutView(APIView):
    """
    View that refreshes the JWT access token using the refresh token stored
    in an HTTP-only cookie and returns a new access token.
    """
    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):
        """
        Retrieves the refresh token from cookies, validates it using the 
        serializer, and issues a new access token. Returns appropriate 
        error responses when the token is missing or invalid.
        """
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            print(f"Failed to move the token to the blacklist: {e}")

        response = Response(
            {
                "detail": (
                    "Log-Out successfully! All Tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
