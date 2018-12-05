from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from billing.core.models import Rate


class TestRateCreateView(TestCase):

    def setUp(self):
        self.url = reverse('core:rates')
        self.client = APIClient()

    def tearDown(self):
        Rate.objects.all().delete()

    def test_valid_data(self):
        data = {
            "date": "2018-12-01",
            "rate": 1.13,
            "source_currency": "EUR"
        }

        response = self.client.post(self.url, data, format='json')

        assert response.status_code == 201
        rate = Rate.objects.get(date=response.json()['date'],
                                source_currency=response.json()['source_currency'])
        assert rate
        assert str(rate.date) == data['date']
        assert rate.source_currency == data['source_currency']

    def test_invalid_date(self):
        data = {
            "date": "2018-12",
            "rate": 1.13,
            "source_currency": "EUR"
        }

        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400

    def test_invalid_rate(self):
        data = {
            "date": "2018-12-01",
            "rate": 1.133333333,
            "source_currency": "EUR"
        }

        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400

    def test_invalid_currency(self):
        data = {
            "date": "2018-12-01",
            "rate": 1.13,
            "source_currency": "RUB"
        }

        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400

    def test_duplicates(self):
        data = {
            "date": "2018-12-01",
            "rate": 1.13,
            "source_currency": "EUR"
        }

        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 201
        # break up unique set constraint
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400
