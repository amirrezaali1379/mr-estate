from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from account.serializers import UserSerializer, VerifyUserSerializer, UserUpdateSerializers
from account.utils.otp import TOTP
from account.utils.exeptions import UserExists, TooEarly
from account.permissions import IsPhoneVerified


class CreateUserView(APIView):
    serializer_class = UserSerializer
    http_method_names = ['post',]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_model = get_user_model()
        phone_number = request.data.get('phone_number')
        password = serializer.validated_data.get('password')
        user = user_model.objects.filter(
            phone_number=phone_number).first()
        totp = TOTP()
        if not user:
            user = user_model.objects.create(
                phone_number=phone_number,
            )

        try:
            code = totp.generate_otp(user=user)
        except UserExists:
            return Response({'detail': 'user with this phone number exists'}, status=status.HTTP_400_BAD_REQUEST)
        except TooEarly as error:
            return Response({
                'detail': error.msg,
                'remaining_time': error.remaining_seconds,
            }, status=status.HTTP_425_TOO_EARLY)

        user.set_password(password)
        user.save()
        totp.send_otp(user, code)
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class VerifyUserView(APIView):
    serializer_class = VerifyUserSerializer
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        totp = TOTP()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        if totp.validate_otp(user=request.user, code=code):
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
