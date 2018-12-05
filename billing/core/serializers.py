from rest_framework import serializers

from billing.core.models import Wallet, Rate
from billing.core.helpers import log_wallet_operation


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ('date', 'rate', 'source_currency', 'target_currency')


class WalletRefillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ('amount', 'currency')
        extra_kwargs = {'amount': {'required': True}}

    def update(self, instance, validated_data):
        if validated_data['currency'] != instance.currency:
            raise serializers.ValidationError('Conversion is not allowed')
        Wallet.deposit(instance.id, validated_data['amount'])
        instance.refresh_from_db()
        log_wallet_operation('refill', target_wallet=instance, target_amount=validated_data['amount'])
        return instance


class WalletMoneyTransferSerializer(serializers.ModelSerializer):
    target_wallet_id = serializers.IntegerField(required=True, source='id')

    class Meta:
        model = Wallet
        fields = ('target_wallet_id', 'amount')
        extra_kwargs = {'amount': {'required': True}}


class WalletCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ('currency',)
