from rest_framework import serializers

from billing.core.models import Wallet
from billing.core.serializers import WalletCreateSerializer
from billing.users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    wallet = WalletCreateSerializer(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'name', 'country', 'city', 'password', 'wallet')

    def create(self, validated_data):
        wallet_data = validated_data.pop('wallet')
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        Wallet.objects.create(user=user, **wallet_data)
        return user
