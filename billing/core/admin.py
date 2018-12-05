from django.contrib import admin

from billing.core.models import Rate, Wallet, WalletLog


@admin.register(Rate)
class RateModelAdmin(admin.ModelAdmin):
    class Meta:
        model = Rate
    list_display = ['__str__', 'date', 'rate', 'source_currency', 'target_currency']


@admin.register(Wallet)
class WalletModelAdmin(admin.ModelAdmin):
    class Meta:
        model = Wallet
    list_display = ['__str__', 'amount', 'currency', 'id']
    raw_id_fields = ['user']


@admin.register(WalletLog)
class WalletLogModelAdmin(admin.ModelAdmin):
    class Meta:
        model = WalletLog
    list_display = ['__str__', 'operation', 'source_wallet', 'target_wallet', 'id']
    search_fields = ['']
