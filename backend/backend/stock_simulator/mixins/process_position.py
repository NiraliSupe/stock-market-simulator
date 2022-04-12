from stock_simulator.models import Position
from stock_simulator.exceptions import NotEnoughCashException
from datetime import datetime, timedelta

class ProcessPosition:

    def get_quantity(self, position_obj):
        return position_obj.quantity if position_obj else 0

    def process_position(self, transaction):
        if isinstance(transaction.created_at, str):
            position_date = datetime.strptime(transaction.created_at, '%Y-%m-%dT%H:%M:%Sz').date()
        else:
            position_date = transaction.created_at.date()

        previous_record = Position.objects.filter(date__contains=position_date - timedelta(days=1)
            , ticker__name=transaction.ticker.name
            , cash_balance=transaction.cash_balance)
        current_record = Position.objects.filter(date__startswith=position_date
            , ticker__name=transaction.ticker.name
            , cash_balance=transaction.cash_balance
        )

        previous_position_obj = previous_record[0] if previous_record else None
        current_position_obj = current_record[0] if current_record else None

        current_quantity = -1*transaction.quantity if transaction.transaction_type == 'sell' else transaction.quantity
        previous_quantity = self.get_quantity(previous_position_obj)

        self.process_quantity(previous_quantity, current_quantity, transaction.transaction_type)

        if not current_position_obj:
            self.create_position(previous_position_obj, current_quantity, position_date, transaction.ticker, transaction.cash_balance)
        else:
            self.update_quantity(current_position_obj, current_quantity)

    def create_position(self, previous_position_obj, current_quantity, position_date, stock, cash_balance):
        position_obj, created = Position.objects.get_or_create(
            date="[{},)".format(position_date),
            ticker=stock,
            cash_balance=cash_balance,
            defaults={'quantity': current_quantity + self.get_quantity(previous_position_obj)},
        )
        position_obj.save()

        if previous_position_obj:
            date_range = "[{}, {})".format(previous_position_obj.date.lower, position_date.strftime("%Y-%m-%d"))
            previous_position_obj.date = date_range
            previous_position_obj.save()

    def update_quantity(self, current_position_obj, current_quantity):
        current_position_obj.quantity = current_quantity + current_position_obj.quantity
        current_position_obj.save()

    def process_quantity(self, previous_quantity, current_quantity, transaction_type):
        if transaction_type == 'sell' and abs(current_quantity) > previous_quantity:
            raise NotEnoughCashException('Invalid transaction: insufficient shares to sell.')