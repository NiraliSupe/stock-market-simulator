from rest_framework import viewsets
from rest_framework.views import Response, status
from rest_framework import generics
### DB
from django.db import transaction
from django.db import connection
### Authentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import permission_classes
### Models
from .models import (
    CashTransaction
    , Position
    , Transaction
    , Stock
    , StockPrice
    , Position
    , CashBalance
)
### Serializers
from .serializers import (
    UserSerializer
    , CashTransactionSerializer
    , TransactionSerializer
    , StockSerializer
    , StockPriceSerializer
    , PositionSerializer
    , FileUploadSerializer
    , CashBalanceSerializer
)
### Exceptions
from .exceptions import (
    NotEnoughCashException
    , InvalidDataException,
    RecordNotFoundException
)
### Mixin and Paging
from .mixins import ProcessPosition, ProcessCashBalance, HelperMixin, AuthMixin
from rest_framework.pagination import PageNumberPagination
### Filters
from django_filters import rest_framework as filters
from .filters import CashTransactionFilter, StockPriceFilter
### Mis
from datetime import date, datetime
import pandas as pd


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 150


@permission_classes([IsAuthenticated])
class CashBalanceViewSet(AuthMixin, HelperMixin, viewsets.ModelViewSet):
    queryset = CashBalance.objects.all()
    serializer_class = CashBalanceSerializer

    def get_queryset(self):
        user = self.get_user_object()
        return CashBalance.objects.filter(owner=user)

    @transaction.atomic
    def create(self, request):
        user = self.get_user_object()
        try:
            self.get_cash_balance(user)
            return Response({'error': 'Account exists for the user.'}, status=status.HTTP_400_BAD_REQUEST)
        except RecordNotFoundException:
            return self.create_cash_balance_record(request, user)

    def create_cash_balance_record(self, request, user):
        request_data = request.data
        if not 'owner' in request.data:
            request_data['owner'] = user.id
        serializer = CashBalanceSerializer(data=request_data)
        if serializer.is_valid():
            cash_balance = serializer.save()
            self.create_initial_cash_transaction(cash_balance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_initial_cash_transaction(self, cash_balance):
        CashTransaction.objects.get_or_create(
            date="[{},)".format('2017-01-01'),
            cash_balance=cash_balance,
            defaults={'amount': cash_balance.amount},
        )


@permission_classes([IsAuthenticated])
class TransactionViewSet(AuthMixin, HelperMixin, ProcessPosition, ProcessCashBalance, viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.get_user_object()
        cash_balance = self.get_cash_balance(user)
        return Transaction.objects.filter(cash_balance=cash_balance.id).order_by('-id')

    @transaction.atomic
    def create(self, request):
        user = self.get_user_object()
        cash_balance = self.get_cash_balance(user)

        stock_obj = self.get_stock(request.data['ticker'])

        transaction_data = self.prepare_transaction_data(request, cash_balance, stock_obj)
        amount_after_transaction = self.get_after_amount_from_record(transaction_data, cash_balance)

        if transaction_data['transaction_type'] == 'buy' and amount_after_transaction < 0:
            raise NotEnoughCashException('Insufficient balance to complete the transaction.')

        serializer = TransactionSerializer(data=transaction_data)
        if serializer.is_valid():
            transaction_obj =serializer.save()
            self.process_position(transaction_obj)
            self.process_cash_balance_transaction(transaction_obj)
            self.update_cash_balance(transaction_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            transaction.set_rollback(True)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_after_amount_from_record(self, transaction_data, cash_balance):
        transaction_amount = transaction_data['amount'] if transaction_data['transaction_type'] == 'sell' \
            else transaction_data['amount'] * -1
        return cash_balance.amount + transaction_amount

    def prepare_transaction_data(self, request, cash_balance, stock):
        transaction_data = request.data

        transaction_date = datetime.strptime(transaction_data['created_at'], '%Y-%m-%dT%H:%M:%Sz').date()

        if transaction_date.weekday() == 5 or transaction_date.weekday() == 6:
            raise InvalidDataException('Market closed.')

        if transaction_date.year != 2017:
            raise InvalidDataException('This application supports year: 2017')

        if transaction_date < cash_balance.object_updated_at.date():
            raise InvalidDataException(f'Transaction date should be greater than or equal to last transaction date. Last transaction date: {str(cash_balance.object_updated_at)} ')

        transaction_data['ticker'] = stock.id
        transaction_data['cash_balance'] = cash_balance.id
        transaction_data['amount'] = transaction_data['quantity'] * self.get_stock_price_by_date(transaction_date, stock.name)
        return transaction_data


@permission_classes([IsAuthenticatedOrReadOnly])
class StockPriceViewSet(AuthMixin, viewsets.ModelViewSet):
    queryset = StockPrice.objects.all()
    serializer_class = StockPriceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StockPriceFilter
    pagination_class = StandardResultsSetPagination

    def create(self, request):
        for data in request.data:
            date_string = datetime.strptime(data.pop('date'), '%m/%d/%y')
            name = data.pop('Name')
            ticker_obj, created = Stock.objects.get_or_create(name=name)
            obj, created = StockPrice.objects.update_or_create(ticker=ticker_obj, date=date.strftime(date_string, '%Y-%m-%d'), defaults=data)
        return Response(status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated])
class PositionViewSet(AuthMixin, HelperMixin, viewsets.ModelViewSet):
    serializer_class = PositionSerializer
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.get_user_object()
        cash_balance = self.get_cash_balance(user)
        return Position.objects.filter(cash_balance=cash_balance.id).order_by('-id')


@permission_classes([IsAuthenticated])
class CashTransactionViewSet(AuthMixin, HelperMixin, viewsets.ModelViewSet):
    serializer_class = CashTransactionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CashTransactionFilter
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.get_user_object()
        cash_balance = self.get_cash_balance(user)
        return CashTransaction.objects.filter(cash_balance=cash_balance.id).order_by('-id')


@permission_classes([IsAuthenticated])
class EvaluateAPIView(AuthMixin, HelperMixin, viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    http_method_names = ['get']

    def list(self, request):
        evaluate_date = self.request.query_params.get('date', '2017-12-31')
        user = self.get_user_object()
        cash_balance = self.get_cash_balance(user)
        result = {}
        queryset = self.get_queryset()
        if evaluate_date:
            evaluate_date = datetime.strptime(evaluate_date, '%Y-%m-%d')
            queryset = queryset.filter(date__contains=evaluate_date, cash_balance=cash_balance.id)
        queryset = self.filter_queryset(queryset)

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     data = self.get_serializer(page, many=True).data
        #     response = self.get_paginated_response(data)
        #     response.data['total'] = self.get_total_shares(response.data, evaluate_date)
        #     response.data = self.add_cash_balance(response.data, cash_balance, evaluate_date)
        #     return response

        serializer = self.get_serializer(queryset, many=True)
        result['results'] = serializer.data
        result['total'] = self.get_total_shares(result, evaluate_date)
        result = self.add_cash_balance(result, cash_balance, evaluate_date)
        result['total($)'] = round(result.pop('total'), 2)
        return Response(result)

    def get_total_shares(self, data, evaluate_date):
        return sum(p['quantity'] * self.get_stock_closing_price_by_date(evaluate_date, p['ticker']) \
            for p in data.get('results',[]))

    def get_cash_balance_transaction(self, evaluate_date, cash_balance):
        queryset = CashTransaction.objects.filter(date__contains=evaluate_date, cash_balance=cash_balance.id)
        serializer = CashTransactionSerializer(queryset, many=True)
        return serializer.data

    def add_cash_balance(self, data, cash_balance, evaluate_date):
        cash_balance_transaction = self.get_cash_balance_transaction(evaluate_date, cash_balance)
        if cash_balance_transaction:
            data['results'].append(cash_balance_transaction[0])
            data['total'] += cash_balance_transaction[0]['amount']

        return data


@permission_classes([IsAuthenticatedOrReadOnly])
class StockViewSet(AuthMixin, viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    pagination_class = StandardResultsSetPagination


@permission_classes([IsAuthenticated])
class UploadTradeByFileAPIView(AuthMixin, HelperMixin, ProcessPosition, ProcessCashBalance, generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']

        file_df = pd.read_csv(file)
        self.validate_csv(file_df)
        sorted_df = file_df.sort_values(by=['created_at', 'ticker'])
        transactions = sorted_df.to_dict(orient='records')
        try:
            self.process_csv(transactions)
            return Response({'detail': 'CSV is uploaded successfully.'}, status=status.HTTP_200_OK)
        except Exception as ex:
            transaction.set_rollback(True)
            return Response({'error': f'Failed to process the CSV. Reason: {ex}'}, status=status.HTTP_400_BAD_REQUEST)

    def validate_csv(self, file_df):
        required_columns = ['transaction_type', 'created_at', 'quantity', 'ticker']

        if set(required_columns) - set(list(file_df.columns)) or  len(file_df.columns) > len(required_columns):
            raise InvalidDataException(f"CSV header should contain: {','.join(required_columns)} columns.")

    def process_csv(self, transactions):
        user = self.get_user_object()
        cash_balance = self.get_cash_balance(user)

        self.reset_balance(cash_balance)
        self.remove_exsiting_transactions(cash_balance)
        self.remove_exsiting_positions(cash_balance)
        self.remove_exsiting_cash_transaction(cash_balance)
        self.create_initial_cash_transaction(cash_balance)
        self.upload_transactions(transactions, cash_balance)

    def remove_exsiting_transactions(self, cash_balance):
        Transaction.objects.filter(cash_balance=cash_balance).delete()

    def remove_exsiting_positions(self, cash_balance):
        Position.objects.filter(cash_balance=cash_balance).delete()

    def remove_exsiting_cash_transaction(self, cash_balance):
        CashTransaction.objects.filter(cash_balance=cash_balance).delete()

    def upload_transactions(self, transactions, cash_balance):
        for transaction in transactions:
            transaction_obj = self.create_transaction(transaction, cash_balance)
            if transaction_obj:
                self.process_position(transaction_obj)
                self.process_cash_balance_transaction(transaction_obj)
                self.update_cash_balance(transaction_obj)

    def is_valid_transaction(self, transaction, cash_balance):
        transaction_date = datetime.strptime(transaction['created_at'], '%Y-%m-%dT%H:%M:%Sz').date()
        if transaction_date.year != 2017:
            print (f'Skipping transaction as create date is not 2017.... Skipped transaction: {str(transaction)}')
            return False

        amount_after_transaction = self.get_after_amount_from_record(transaction, cash_balance)
        if transaction['transaction_type'] == 'buy' and amount_after_transaction < 0:
            raise NotEnoughCashException(f'Inufficient balance to complete the transaction. Failed at: {str(transaction)}')
            return False

        return True

    def create_transaction(self, transaction, cash_balance):
        position_date = datetime.strptime(transaction['created_at'], '%Y-%m-%dT%H:%M:%Sz').date()
        stock = self.get_stock(transaction['ticker'])
        stock_price = self.get_stock_price_by_date(position_date, transaction['ticker'])
        transaction['amount'] = stock_price * transaction['quantity']
        transaction['ticker'] = stock
        transaction['cash_balance'] = cash_balance

        if self.is_valid_transaction(transaction, cash_balance):
            transaction_obj, created = Transaction.objects.get_or_create(**transaction)
            if not created:
                transaction_obj.quantity = transaction_obj.quantity + transaction['quantity']
                transaction_obj.amount = transaction_obj.amount + transaction['amount']
                transaction_obj.save()
            return transaction_obj
        else:
            return None

    def get_after_amount_from_record(self, transaction_data, cash_balance):
        transaction_amount = transaction_data['amount'] if transaction_data['transaction_type'] == 'sell' \
            else transaction_data['amount'] * -1
        return cash_balance.amount + transaction_amount
