import pytest

from faker import Faker
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import CustomUser


fake = Faker()


@pytest.fixture
def client_and_user():
    user = CustomUser.objects.create_user(
        phone_number='09011111111',
        password='testUserP@ss1',
    )

    user.first_name = fake.first_name()
    user.last_name = fake.last_name()
    user.address = fake.address()
    user.is_active = True
    user.save()
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    return client, user
