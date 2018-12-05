from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from billing.core.models import Wallet
from billing.users.models import User


class TestUserCreateView(TestCase):

    def setUp(self):
        self.url = reverse('users:register')
        self.client = APIClient()

    def tearDown(self):
        Wallet.objects.all().delete()
        User.objects.all().delete()

    def test_valid_data(self):
        data = {
            "username": "leo777",
            "name": "Leonid",
            "country": "Russia",
            "city": "Moscow",
            "password": "my_secret_password",
            "wallet": {
                "currency": "USD"
            }
        }

        response = self.client.post(self.url, data, format='json')

        assert response.status_code == 201
        assert 'username' in response.json().keys()
        assert data['username'] == response.json()['username']
        user = User.objects.get(username=response.json()['username'])
        assert user
        assert user.wallet
        assert user.wallet.currency == data['wallet']['currency']

    def test_invalid_data(self):
        data = {
            "username": "leo777",
            "name": "Leonid",
            "country": "Russia",
            "city": "Moscow",
        }

        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400

    def test_invalid_wallet_currency(self):
        data = {
            "username": "leo777",
            "name": "Leonid",
            "country": "Russia",
            "city": "Moscow",
            "password": "my_secret_password",
            "wallet": {
                "currency": "RUB"
            }
        }

        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400
