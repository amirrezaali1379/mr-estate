from rest_framework import serializers
from django.contrib.auth import password_validation

from account.models import CustomUser
from account.validators import phone_validator


class UserSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[phone_validator,])
    password = serializers.CharField(
        write_only=True,
        validators=[
            password_validation.validate_password
        ]
    )
    confirm_password = serializers.CharField(write_only=True,)

    def validate(self, data):
        password = data['password']
        confirm_password = data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError(
                'password and confirm password doesn\'t match.')

        return data


class VerifyUserSerializer(serializers.Serializer):
    code = serializers.CharField()


class UserUpdateSerializers(serializers.ModelSerializer):
    phone_number = serializers.CharField(read_only=True)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    address = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'first_name', 'last_name', 'address']
