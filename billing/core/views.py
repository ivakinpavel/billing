import csv
from io import StringIO
from datetime import datetime
from decimal import Decimal

from django.http import Http404, StreamingHttpResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework import serializers

from django_filters.views import FilterView

from billing.users.models import User
from billing.core.serializers import WalletRefillSerializer, WalletMoneyTransferSerializer, RateSerializer
from billing.core.models import Wallet
from billing.core.helpers import log_wallet_operation, Converter
from billing.core.filters import WalletLogFilter


class RateCreateView(CreateAPIView):
    serializer_class = RateSerializer


class WalletRefillView(UpdateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletRefillSerializer


class WalletMoneyTransferView(APIView):
    """
    Transfer money between wallets.
    """

    def get_object(self, pk):  # get objects with lock
        try:
            return Wallet.objects.select_for_update().get(pk=pk)
        except Wallet.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        with transaction.atomic():
            source_wallet = self.get_object(pk)
            target_wallet_serializer = WalletMoneyTransferSerializer(data=request.data)
            if target_wallet_serializer.is_valid():
                target_wallet = self.get_object(target_wallet_serializer.validated_data['id'])
                withdraw_amount = target_wallet_serializer.validated_data['amount']
                if source_wallet.amount < withdraw_amount:
                    raise serializers.ValidationError('Not enough money on source wallet')
                if target_wallet.currency == source_wallet.currency:  # direct transfer
                    deposit_amount = withdraw_amount
                else:  # should be converted
                    converter = Converter(datetime.now().date(), source_wallet.currency, target_wallet.currency)
                    deposit_amount = converter.convert(withdraw_amount)
                source_wallet.amount -= Decimal(withdraw_amount)
                target_wallet.amount += Decimal(deposit_amount)
                source_wallet.save()
                target_wallet.save()
                log_wallet_operation('transfer', source_wallet=source_wallet, target_wallet=target_wallet,
                                     source_amount=withdraw_amount, target_amount=deposit_amount)
                return Response({}, status=status.HTTP_200_OK)

        return Response(target_wallet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def make_report_csv(username, wallet_logs):
    user = get_object_or_404(User, name=username)
    print(user)
    print(user.wallet)
    for c, log in enumerate(wallet_logs):
        print(log)
        output = StringIO()
        writer = csv.writer(output)

        if c == 0:
            writer.writerow([f'Отчет операций по кошельку пользователя {user.name}, '
                             f'Валюта кошелька {user.wallet.currency}'])
            writer.writerow(['Дата', 'Операция', 'Сумма'])

        if log.operation == 1:
            writer.writerow([log.timestamp, 'Пополнение', log.target_amount])
        elif log.operation == 2 and log.source_wallet_id == user.wallet.id:
            writer.writerow([log.timestamp, 'Исходящий перевод', log.source_amount])
        elif log.operation == 2 and log.target_wallet_id == user.wallet.id:
            writer.writerow([log.timestamp, 'Входящий перевод', log.target_amount])
        output.seek(0)
        yield output.read()


class ReportView(FilterView):
    """
    View report of users wallet operation, or download it in .csv
    """
    filterset_class = WalletLogFilter
    template_name = 'pages/report.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        if self.request.GET.get('username'):
            context['user'] = get_object_or_404(User, name=self.request.GET.get('username'))
            context['user_id'] = context['user'].id
        return context

    def get(self, *args, **kwargs):
        if self.request.GET.get('csv'):
            fs = self.get_filterset(self.get_filterset_class())
            if fs.is_valid() or not self.get_strict():
                object_list = fs.qs
            else:
                object_list = fs.queryset.none()
            response = StreamingHttpResponse(
                make_report_csv(self.request.GET.get('username'), object_list),
                content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=report.csv'
            return response
        return super(ReportView, self).get(*args, **kwargs)
