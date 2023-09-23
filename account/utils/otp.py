import pyotp


class TOTP:
    @classmethod
    def generate_otp(self) -> tuple[str, str]:
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=60*5)
        code = totp.now()
        return code, secret

    @classmethod
    def validate_otp(self, secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret, interval=5*60)
        result = totp.verify(code)
        return result

    @classmethod
    def send_otp(self, receiver: str, code: str) -> None:
        print(f"{receiver} -> {code}")
