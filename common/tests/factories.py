# Standard Library Imports
import factory

# Third-Party Imports (Django)
from factory.django import DjangoModelFactory

# Local Imports
from apps.users.models import CustomUser

class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.first_name}@example.com')
