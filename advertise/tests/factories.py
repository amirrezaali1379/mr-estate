import factory

from advertise.models import Advertise


class AdvertiseFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory('account.tests.factories.UserFactory')
    title = factory.Faker('sentence', nb_words=4)
    price = factory.Faker('pyint')

    class Meta:
        model = Advertise
