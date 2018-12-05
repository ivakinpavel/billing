from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from billing.core.tests.factories import RateFactory, WalletFactory
from billing.core.enums import CurrencyChoices
from billing.core.models import Rate, Wallet, WalletLog


class TestWalletRefillView(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_valid_data(self):
        wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_refill', kwargs={'pk': wallet.pk})
        data = {
            "currency": "USD",
            "amount": 10
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == 200
        wallet.refresh_from_db()
        assert wallet.amount == Decimal('10.00')

    def test_wrong_currency(self):
        wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_refill', kwargs={'pk': wallet.pk})
        data = {
            "currency": "EUR",
            "amount": 10
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == 400

    def test_no_currency(self):
        wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_refill', kwargs={'pk': wallet.pk})
        data = {
            "amount": 10
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == 400

    def test_negative_amount(self):
        wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_refill', kwargs={'pk': wallet.pk})
        data = {
            "currency": "USD",
            "amount": -10
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == 400

    def test_invalid_amount(self):
        wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_refill', kwargs={'pk': wallet.pk})
        data = {
            "currency": "USD",
            "amount": "invalid_amount"
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == 400

    def test_invalid_places_amount(self):
        wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_refill', kwargs={'pk': wallet.pk})
        data = {
            "currency": "USD",
            "amount": 10.333
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == 400

    def test_invalid_max_digits_amount(self):
        wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_refill', kwargs={'pk': wallet.pk})
        data = {
            "currency": "USD",
            "amount": 100000000000000
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == 400


class TestWalletTransferView(TestCase):

    def setUp(self):
        RateFactory(source_currency='EUR', rate='1.13')
        self.client = APIClient()

    def tearDown(self):
        Rate.objects.all().delete()
        WalletLog.objects.all().delete()
        Wallet.objects.all().delete()

    def test_direct_transfer(self):
        source_wallet = WalletFactory(currency=CurrencyChoices.USD.value, amount=15.00)
        target_wallet = WalletFactory(currency=CurrencyChoices.USD.value, amount=10.00)
        url = reverse('core:wallet_transfer', kwargs={'pk': source_wallet.pk})
        data = {
            "target_wallet_id": target_wallet.id,
            "amount": 10.00
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        source_wallet.refresh_from_db()
        target_wallet.refresh_from_db()
        assert source_wallet.amount == Decimal('5.00')
        assert target_wallet.amount == Decimal('20.00')

    def test_direct_conversion(self):
        source_wallet = WalletFactory(currency=CurrencyChoices.EUR.value, amount=15.00)
        target_wallet = WalletFactory(currency=CurrencyChoices.USD.value)
        url = reverse('core:wallet_transfer', kwargs={'pk': source_wallet.pk})
        data = {
            "target_wallet_id": target_wallet.id,
            "amount": 10.00
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        source_wallet.refresh_from_db()
        target_wallet.refresh_from_db()
        assert source_wallet.amount == Decimal('5.00')
        assert target_wallet.amount == Decimal('11.30')

    def test_reverse_conversion(self):
        source_wallet = WalletFactory(currency=CurrencyChoices.USD.value, amount=15.00)
        target_wallet = WalletFactory(currency=CurrencyChoices.EUR.value)
        url = reverse('core:wallet_transfer', kwargs={'pk': source_wallet.pk})
        data = {
            "target_wallet_id": target_wallet.id,
            "amount": 10.00
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        source_wallet.refresh_from_db()
        target_wallet.refresh_from_db()
        assert source_wallet.amount == Decimal('5.00')
        assert target_wallet.amount == Decimal('8.84')  # 8.849 round to floor

    def test_two_step_conversion(self):
        RateFactory(source_currency='CAD', rate='0.76')
        source_wallet = WalletFactory(currency=CurrencyChoices.CAD.value, amount=15.00)
        target_wallet = WalletFactory(currency=CurrencyChoices.EUR.value)
        url = reverse('core:wallet_transfer', kwargs={'pk': source_wallet.pk})
        data = {
            "target_wallet_id": target_wallet.id,
            "amount": 10.00
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        source_wallet.refresh_from_db()
        target_wallet.refresh_from_db()
        assert source_wallet.amount == Decimal('5.00')
        assert target_wallet.amount == Decimal('6.72')  # CAD->USD rate * USD->EUR rate * amount round to floor

    def test_no_rate(self):
        source_wallet = WalletFactory(currency=CurrencyChoices.CAD.value, amount=15.00)
        target_wallet = WalletFactory(currency=CurrencyChoices.EUR.value, amount=10.00)
        url = reverse('core:wallet_transfer', kwargs={'pk': source_wallet.pk})
        data = {
            "target_wallet_id": target_wallet.id,
            "amount": 10.00
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 400
        source_wallet.refresh_from_db()
        target_wallet.refresh_from_db()
        assert source_wallet.amount == Decimal('15.00')
        assert target_wallet.amount == Decimal('10.00')

    def test_negative_amount(self):
        source_wallet = WalletFactory(currency=CurrencyChoices.CAD.value, amount=15.00)
        target_wallet = WalletFactory(currency=CurrencyChoices.EUR.value, amount=10.00)
        url = reverse('core:wallet_transfer', kwargs={'pk': source_wallet.pk})
        data = {
            "target_wallet_id": target_wallet.id,
            "amount": -10.00
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 400
        source_wallet.refresh_from_db()
        target_wallet.refresh_from_db()
        assert source_wallet.amount == Decimal('15.00')
        assert target_wallet.amount == Decimal('10.00')
