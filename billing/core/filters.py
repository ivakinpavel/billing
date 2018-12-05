from django.db.models import Q
from django_filters import FilterSet, DateFromToRangeFilter, CharFilter, widgets

from billing.core.models import WalletLog


class WalletLogFilter(FilterSet):
    username = CharFilter(label='Username', method='user_filter')
    timestamp = DateFromToRangeFilter(field_name='timestamp',
                                      widget=widgets.RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'}))

    def user_filter(self, queryset, name, value):
        return queryset.filter(
            Q(source_wallet__user__name=value) |
            Q(target_wallet__user__name=value)
        )

    class Meta:
        model = WalletLog
        fields = ['username', 'timestamp']
