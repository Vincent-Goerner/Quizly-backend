from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration that validates matching passwords,
    checks for unique username and email, and creates the user instance.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_confirmed_password(self, value):
        """
        Ensures that the `confirmed_password` matches the provided `password`;
        raises a validation error if they differ.
        """
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_username(self, value):
        """
        Validates that the username is not already in use; raises an error if
        a user with the given username exists.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Invalid credentials.")
        return value
    
    def validate_email(self, value):
        """
        Validates that the email address is unique; raises an error if a user
        with the given email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Invalid credentials.')
        return value

    def save(self):
        """
        Creates a new user with a hashed password based on the validated data
        and returns the newly created user instance.
        """
        pw = self.validated_data['password']

        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(pw)
        account.save()
        return account


class LoginTokenObtainPairSerializer(serializers.Serializer):
    """
    Serializer for validating login credentials and authenticating a user
    before issuing JWT tokens or related login responses.
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, payload):
        """
        Validates the provided username and password by checking user existence
        and performing authentication; raises a validation error on failure.
        On success, attaches the authenticated `user` to the payload.
        """
        payload_username = payload.get('username')
        payload_password = payload.get('password')

        try:
            user = User.objects.get(username=payload_username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Username or password is not correct")

        user = authenticate(username=payload_username, password=payload_password)
        if not user:
            raise serializers.ValidationError("Username or password is not correct")

        payload['user'] = user
        return payload