import django_filters as filters
from .models import CashBalance, StockPrice, CashTransaction


class StockPriceFilter(filters.FilterSet):
    class Meta:
        model = StockPrice
        fields = {
            'ticker': ['exact', 'lt', 'gt'],
            'date': ['exact', 'year__gt', 'lt', 'gt'],
        }


class CashTransactionFilter(filters.FilterSet):
    class Meta:
        model = CashTransaction
        fields = {
            'cash_balance': ['exact', 'lt', 'gt'],
            #'date': ['contains'],
        }