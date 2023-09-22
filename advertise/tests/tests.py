import pytest

from typing import Tuple
from django.urls import reverse
from rest_framework.test import APIClient

from .factories import AdvertiseFactory
from account.models import CustomUser


@pytest.mark.django_db
def test_update_advertise(client_and_user: Tuple[APIClient, CustomUser]):
    client, user = client_and_user
    advertise = AdvertiseFactory.create()
    url = reverse('advertise:advertise-detail', kwargs={'pk': advertise.id})

    body = {
        'title': 'new title'
    }

    response = client.patch(path=url, data=body)

    assert response.status_code == 403

    advertise.user = user
    advertise.save()

    response = client.patch(path=url, data=body)

    assert response.status_code == 200
    assert response.data['title'] == body['title']
