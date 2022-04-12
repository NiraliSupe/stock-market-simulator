from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from stock_simulator.exceptions import InvalidTokenException, TypeException, RecordNotFoundException
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from stock_simulator.models import CashBalance, Stock, StockPrice
from datetime import timedelta

class HelperMixin:

    def get_user_object(self):
        username = None
        if self.request.user.username:
            username = self.request.user.username
        else:
            token = self.request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            if token:
                try:
                    valid_data = VerifyJSONWebTokenSerializer().validate({'token': token})
                    username = valid_data['user']
                except Exception as ex:
                    raise InvalidTokenException("Token doesn't match with our signature. Please contact administrator.")

        return get_object_or_404(User, username=username)

    def get_cash_balance(self, user):
        if user and not isinstance(user, User):
            raise TypeException('user must be of type User.')
        cash_balance = CashBalance.objects.filter(owner=user)
        if not cash_balance:
            raise RecordNotFoundException(f'No cash balance record found for the user')
        else:
            return cash_balance[0]

    def get_stock(self, ticker):
        try:
            return Stock.objects.get(name=ticker)
        except Stock.DoesNotExist:
            raise RecordNotFoundException(f'{ticker} not found.')

    def get_stock_price_by_date(self, transaction_date, ticker):
        transaction_date = self.handle_weekend_date(transaction_date)
        stock_price = StockPrice.objects.filter(date=transaction_date.strftime("%Y-%m-%d"), ticker__name=ticker)

        if not stock_price:
            raise RecordNotFoundException(f'No stock price found for the ticker {ticker}')
        else:
            return (stock_price[0].open + stock_price[0].close) / 2

    def get_stock_closing_price_by_date(self, transaction_date, ticker):
        transaction_date = self.handle_weekend_date(transaction_date)
        stock_price = StockPrice.objects.filter(date=transaction_date.strftime("%Y-%m-%d"), ticker__name=ticker)

        if not stock_price:
            raise RecordNotFoundException(f'No stock price found for the ticker {ticker}')
        else:
            return stock_price[0].close

    def handle_weekend_date(self, transaction_date):
        week_num = transaction_date.weekday()
        # 5 Sat, 6 Sun
        if week_num == 5:
            return transaction_date - timedelta(days=1)
        elif week_num == 6:
            return transaction_date - timedelta(days=2)

        return transaction_date
