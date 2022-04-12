from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import DateRangeField

class CashBalance(models.Model): #cashbalance
    """
    It stores cash balance (default $100,000) for transactions.
    """
    amount = models.FloatField(default=100000)
    owner = models.ForeignKey(User, null=False, blank=False, related_name='cash_balance', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    object_updated_at = models.DateTimeField(default='2017-01-01')

    def __str__(self):
        return  self.owner.username


class Stock(models.Model):
    """
    It stores unique list of ticker from the json file.
    """
    name = models.CharField(null=False, blank=False, max_length=50, unique=True)
    def __str__(self):
        return  self.name


TRANSACTION_TYPE = (
    ('buy', 'Buy'),
    ('sell', 'Sell'),
)
class Transaction(models.Model):
    """
    It stores all the transactions (buy or sell) carried out by the user.
    """
    ticker = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transaction')
    transaction_type = models.CharField(null=False, blank=False, max_length=10, choices=TRANSACTION_TYPE)  ## Buy SELL
    amount = models.FloatField(null=True, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    cash_balance = models.ForeignKey(CashBalance, related_name='transaction', on_delete=models.CASCADE)


class Position(models.Model):
    """
    It stores stock holdings. It gets updated based on the transactions.
    """
    date = DateRangeField(null=True, db_index=True)
    ticker = models.ForeignKey(Stock, on_delete=models.CASCADE, null=False, related_name='position')
    quantity = models.IntegerField(null=False, default=0)
    cash_balance = models.ForeignKey(CashBalance, on_delete=models.CASCADE, null=False, related_name='positions')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'ticker', 'cash_balance'], name='unique-date-ticker-portfolio')
        ]


class CashTransaction(models.Model):  #cash transaction
    """
    It maintains cash balance after every transaction.
    """
    date = DateRangeField(null=True, db_index=True)
    amount = models.FloatField(null=False, default=0)
    cash_balance = models.ForeignKey(CashBalance, null=False, related_name='cashbalance', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'cash_balance'], name='unique-date-portfolio')
        ]


class StockPrice(models.Model):
    """
    It stores stock prices.
    """
    date = models.DateField(null=False, blank=False)
    ticker = models.ForeignKey(Stock, related_name='price', on_delete=models.CASCADE)
    open = models.FloatField(null=False, blank=False)
    close = models.FloatField(null=False, blank=False)
    low = models.FloatField(null=False, blank=False)
    high = models.FloatField(null=False, blank=False)
    volume = models.IntegerField(null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'ticker'], name='unique-date-ticker')
        ]
