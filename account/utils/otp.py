import pyotp

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone

from account.utils.exeptions import TooEarly, UserExists
from account.models import OTP


class TOTP:
    def generate_otp(self, user: AbstractBaseUser) -> str:
        if user.is_phone_verified:
            raise UserExists()

        otp, created = OTP.objects.get_or_create(user=user)
        if not created:
            last_request_time = otp.request_time
            elapsed_time = timezone.now() - last_request_time
            if elapsed_time < timedelta(minutes=1):
                remaining_seconds = 60 - elapsed_time.seconds
                raise TooEarly(
                    "Please wait at least one minute before requesting another OTP.", remaining_seconds
                )

        secret = pyotp.random_base32()
        otp.secret = secret
        otp.save()
        totp = pyotp.TOTP(secret, interval=60*5)
        code = totp.now()
        return code

    def validate_otp(self, user: AbstractBaseUser, code: str) -> bool:
        try:
            otp = OTP.objects.get(user=user)
            totp = pyotp.TOTP(otp.secret, interval=5*60)
            result = totp.verify(code)
            if result:
                otp.delete()
            return result
        except OTP.DoesNotExist:
            return False

    def send_otp(self, user: AbstractBaseUser, code):
        print(f"{user.phone_number} -> {code}")
