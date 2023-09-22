import factory

from faker import Faker

from account.models import CustomUser


fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        skip_postgeneration_save = True

    phone_number = factory.Sequence(
        lambda n: '09' + str(fake.random_number(digits=9)))
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or UserFactory.default_password()
        self.set_password(password)
        if create:
            self.save()

    @classmethod
    def default_password(self):
        return 'someDummyPassword1'
