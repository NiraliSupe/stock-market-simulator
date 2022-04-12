import os
from rest_framework import serializers
from .models import CashBalance, Transaction, Stock, StockPrice, Position, CashTransaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'is_superuser'
            , 'username'
            , 'first_name'
            , 'last_name'
            , 'email'
            , 'is_staff'
            , 'is_active'
            , 'date_joined'
            , 'user_permissions'
        ]


class CashBalanceSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    class Meta:
        model = CashBalance
        fields = '__all__'
        extra_kwargs = {
            'owner': {'write_only': True}
        }


class TransactionSerializer(serializers.ModelSerializer):
    ticker_name = serializers.CharField(source='ticker.name', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {
            'ticker': {'write_only': True},
        }


class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = '__all__'


class StockPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockPrice
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='ticker.name', read_only=True)

    class Meta:
        model = Position
        fields = '__all__'
        extra_kwargs = {
            'ticker': {'write_only': True}
        }


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Please upload the csv file.')

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[validate_file_extension])

    class Meta:
        fields = ('file',)


class CashTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CashTransaction
        fields = '__all__'
