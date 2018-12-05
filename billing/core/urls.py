from django.urls import path

from billing.core.views import (
    RateCreateView, WalletRefillView, WalletMoneyTransferView,
    ReportView
)

app_name = "core"
urlpatterns = [
    path('rates/', RateCreateView.as_view(), name='rates'),
    path('wallets/<int:pk>/refill/', WalletRefillView.as_view(), name='wallet_refill'),
    path('wallets/<int:pk>/transfer/', WalletMoneyTransferView.as_view(), name='wallet_transfer'),
    path('report/', ReportView.as_view(), name='report'),
]
