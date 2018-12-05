import math

from django.db.models import Q
from rest_framework import serializers

from billing.core.models import Rate, WalletLog
from billing.core.enums import WalletLogOperationChoices, CurrencyChoices


def log_wallet_operation(operation, **kwargs):
    WalletLog.objects.create(operation=WalletLogOperationChoices.from_name(operation).value, **kwargs)


class Converter:
    def __init__(self, date, source_currency, target_currency):
        self.date = date
        self.source_currency = source_currency
        self.target_currency = target_currency

    def find_rate(self, source_currency, target_currency):
        try:
            rate = Rate.objects.get(
                Q(date=self.date, source_currency=source_currency, target_currency=target_currency) |
                Q(date=self.date, source_currency=target_currency, target_currency=source_currency)
            )
            if rate.source_currency == source_currency and rate.target_currency == target_currency:
                return rate.rate
            else:
                return 1 / rate.rate
        except Rate.DoesNotExist:
            return

    def _convert(self, rate, amount):
        return math.floor(amount * rate * 100) / 100.0  # floor down

    def convert(self, amount):
        rate = self.find_rate(self.source_currency, self.target_currency)
        if not rate:
            source_to_default = self.find_rate(self.source_currency, CurrencyChoices.default_currency())
            default_to_target = self.find_rate(CurrencyChoices.default_currency(), self.target_currency)
            if not source_to_default or not default_to_target:
                raise serializers.ValidationError('Could not find proper rates')
            rate = source_to_default * default_to_target
        converted_amount = self._convert(rate, amount)
        return converted_amount
