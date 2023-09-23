from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from account.serializers import (UserSerializer,
                                 VerifyUserSerializer,
                                 UserUpdateSerializers)
from account.utils.otp import TOTP
from account.permissions import IsPhoneVerified
from account.models import OTP


class OTPRequestView(APIView):
    serializer_class = UserSerializer
    http_method_names = ['post',]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_model = get_user_model()
        phone_number = request.data.get('phone_number')
        user, created = user_model.objects.get_or_create(
            phone_number=phone_number)

        if not created:
            try:
                user_otp = user.otp
            except OTP.DoesNotExist:
                user_otp = None

            if user_otp:
                last_request_time = user_otp.request_time
                elapsed_time = timezone.now() - last_request_time
                if elapsed_time < timedelta(minutes=1):
                    remaining_seconds = 60 - elapsed_time.seconds
                    return Response(
                        {
                            'detail': "Please wait at least one minute before requesting another OTP.",
                            'remaining_seconds': remaining_seconds
                        }, status=status.HTTP_425_TOO_EARLY,
                    )

                user_otp.delete()

        code, secret = TOTP.generate_otp()
        OTP.objects.create(
            user=user,
            secret=secret
        )

        TOTP.send_otp(phone_number, code)
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "created": created,
            "verified": user.is_phone_verified,
        })


class VerifyUserView(APIView):
    serializer_class = VerifyUserSerializer
    permission_classes = [permissions.IsAuthenticated,]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        try:
            user_otp = request.user.otp
        except OTP.DoesNotExist:
            user_otp = None

        if not user_otp:
            return Response(
                {
                    'detail': 'no request available'
                }, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        if TOTP.validate_otp(user_otp.secret, code):
            request.user.is_phone_verified = True
            request.user.save()

            return Response({
                'detail': 'verified'
            })
        else:
            return Response({'detail': 'code is not valid'}, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializers
    permission_classes = [IsPhoneVerified, ]

    def get_object(self):
        return self.request.user
