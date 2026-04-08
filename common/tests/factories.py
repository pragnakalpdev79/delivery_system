# Standard Library Imports
import factory
import logging

# Third-Party Imports (Django)
from factory.django import DjangoModelFactory
from faker import Faker
from faker.providers.phone_number import Provider

# Local Imports
from apps.users.models import CustomUser

logger = logging.getLogger('main')

class IndiaPhoneNumberProvider(Provider):
    """
    A Provider for phone number.
    """

    def india_phone_number(self):
        return f'+91{self.msisdn()[3:]}'

fake = Faker()
fake.add_provider(IndiaPhoneNumberProvider)

class CustomUserFactory(DjangoModelFactory):

    class Meta:
        model = CustomUser

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.first_name}@example.com')
    utype = 'c'
    phone_number= fake.india_phone_number()
    logger.info(phone_number)
