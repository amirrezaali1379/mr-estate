import pytest

from django.urls import reverse
from rest_framework.test import APIClient

from .factories import UserFactory
from account.models import CustomUser
from account.utils import exeptions, otp


@pytest.mark.django_db
def test_signup():
    client = APIClient()
    user = UserFactory.build()

    body = {
        'phone_number': user.phone_number,
        'password': UserFactory.default_password(),
        'confirm_password': UserFactory.default_password()
    }

    url = reverse('account:signup')
    response = client.post(path=url, data=body)
    assert response.status_code == 200

    assert response.data['phone_number'] == user.phone_number

    saved_user = CustomUser.objects.get(phone_number=user.phone_number)
    assert saved_user is not None


@pytest.mark.django_db
def test_login():
    client = APIClient()
    user = UserFactory.create()
    url = reverse("account:token_obtain_pair")

    body = {'phone_number': user.phone_number,
            'password': UserFactory.default_password()}
    print(body)
    response = client.post(path=url, data=body)
    print(response.data)
    access = response.data.get("access")
    refresh = response.data.get("refresh")

    assert access != None
    assert type(access) == str

    assert refresh != None
    assert type(refresh) == str


@pytest.mark.django_db
def test_otp():
    totp = otp.TOTP()
    user1 = UserFactory.create()
    user1.is_active = False
    user1.save()

    code = totp.generate_otp(user1)

    assert code != None

    with pytest.raises(exeptions.TooEarly):
        totp.generate_otp(user1)

    user2 = UserFactory.create()

    with pytest.raises(exeptions.UserExists):
        totp.generate_otp(user2)

    assert totp.validate_otp(user1, code)
