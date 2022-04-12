from stock_simulator.models import CashTransaction, Transaction, CashBalance
from stock_simulator.exceptions import TypeException
from datetime import datetime, timedelta

class ProcessCashBalance:

    def get_after_amount(self, transaction):
        #transaction_amount = transaction.amount if transaction.amount else 1
        transaction_amount = transaction.amount if transaction.transaction_type == 'sell' \
            else transaction.amount * -1
        return transaction.cash_balance.amount + transaction_amount

    def process_cash_balance_transaction(self, transaction):
        if isinstance(transaction.created_at, str):
            cash_trans_date = datetime.strptime(transaction.created_at, '%Y-%m-%dT%H:%M:%Sz').date()
        else:
            cash_trans_date = transaction.created_at.date()
        after_transaction_amount = self.get_after_amount(transaction)
        previous_record = CashTransaction.objects.filter(date__contains=cash_trans_date - timedelta(days=1)
            , cash_balance=transaction.cash_balance)
        current_record = CashTransaction.objects.filter(date__startswith=cash_trans_date
            , cash_balance=transaction.cash_balance)

        previous_cash_obj = previous_record[0] if previous_record else None
        current_cash_obj = current_record[0] if current_record else None

        if not current_cash_obj:
            cash_trans_obj, created = CashTransaction.objects.get_or_create(
                date="[{},)".format(cash_trans_date),
                cash_balance=transaction.cash_balance,
                defaults={'amount': after_transaction_amount},
            )

            if previous_cash_obj:
                date_range = "[{}, {})".format(previous_cash_obj.date.lower, cash_trans_date.strftime("%Y-%m-%d"))
                previous_cash_obj.date = date_range
                previous_cash_obj.save()
        else:
            current_cash_obj.amount = after_transaction_amount
            current_cash_obj.save()

    def update_cash_balance(self, transaction):
        cash_balance = transaction.cash_balance
        cash_balance.amount = self.get_after_amount(transaction)
        cash_balance.object_updated_at = transaction.created_at
        cash_balance.save()

    def reset_balance(self, cash_balance):
        if cash_balance and not isinstance(cash_balance, CashBalance):
            raise TypeException('user must be of type User.')
        cash_balance.amount = 100000
        cash_balance.save()

    def create_initial_cash_transaction(self, cash_balance):
        CashTransaction.objects.get_or_create(
            date="[{},)".format('2017-01-01'),
            cash_balance=cash_balance,
            defaults={'amount': cash_balance.amount},
        )