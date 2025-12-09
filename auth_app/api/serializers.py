from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Invalid credentials.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Invalid credentials.')
        return value

    def save(self):
        pw = self.validated_data['password']

        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(pw)
        account.save()
        return account


class LoginTokenObtainPairSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, payload):
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