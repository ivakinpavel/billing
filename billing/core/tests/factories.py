from datetime import datetime

from factory import DjangoModelFactory, SubFactory

from billing.users.tests.factories import UserFactory
from billing.core.models import Rate, Wallet


class RateFactory(DjangoModelFactory):
    date = datetime.now().date()

    class Meta:
        model = Rate


class WalletFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)

    class Meta:
        model = Wallet
