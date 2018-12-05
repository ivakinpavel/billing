# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models, transaction
from django.core.validators import MinValueValidator

from billing.users.models import User
from billing.core.enums import WalletLogOperationChoices, CurrencyChoices


class Rate(models.Model):
    date = models.DateField()
    rate = models.DecimalField(max_digits=16, decimal_places=8)
    source_currency = models.CharField(max_length=3, choices=CurrencyChoices.rate_choices())
    target_currency = models.CharField(max_length=3, default=CurrencyChoices.default_currency())

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        unique_together = ['date', 'source_currency', 'target_currency']
        index_together = ['date', 'source_currency', 'target_currency']

    def __str__(self):
        return f'{self.source_currency}->{self.target_currency}: {self.date}'


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices())
    amount = models.DecimalField(max_digits=16, decimal_places=2,
                                 default=0.00, validators=[MinValueValidator(Decimal('0.00'))])

    @classmethod
    def deposit(cls, id, amount):
        with transaction.atomic():
            wallet = (
                cls.objects
                .select_for_update()
                .get(id=id)
            )

            wallet.amount += amount
            wallet.save()
        return wallet

    class Meta:
        verbose_name = 'Кошелек'
        verbose_name_plural = 'Кошельки'

    def __str__(self):
        return f'{self.user.name} {self.currency} wallet'


class WalletLog(models.Model):
    operation = models.PositiveSmallIntegerField(choices=WalletLogOperationChoices.choices())
    source_wallet = models.ForeignKey(Wallet, blank=True, null=True, on_delete=models.PROTECT, related_name='logs')
    target_wallet = models.ForeignKey(Wallet, blank=True, null=True, on_delete=models.PROTECT)
    source_amount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    target_amount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'История операций по кошелькам'
        ordering = ['-id']
