from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
from sqlalchemy.orm import relationship
from DataStorage.tables import Base, Trade, Deposit, Withdrawal
from DataStorage.tables import DepositStatusEnum, WithdrawalStatusEnum
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

# ------------- #
#    Configs    #
# ------------- #

DB_NAME = "temp_db.db"  # This will be the sqlite filename


# ----------------------------- #
# Do not modify below this line #
# ----------------------------- #

class DatabaseInterface:
    def __init__(self, verbose=False):
        self._engine = create_engine('sqlite:///'+DB_NAME, echo=verbose)
        _Session = sessionmaker(bind=self._engine)
        self._session = _Session()

        # Create the tables
        Base.metadata.create_all(self._engine)  # Base come from tables.py import

    def query_withdrawals(self):
        return self._session.query(Withdrawal).filter(Withdrawal.exchange_name == "BINANCE").all()

    def save_trade(self,
                   time_millis,
                   exchange_name,
                   trade_id,
                   order_id,
                   symbol,
                   base_symbol,
                   quantity,
                   price,
                   commission_fee,
                   commission_symbol,
                   money_flow,
                   fair_market_value_btc_usd,
                   fair_market_value_bnb_usd,
                   fair_market_value_com_usd,
                   is_buy,
                   is_maker,
                   is_best_match):

        # Create a row to insert
        trade_row = Trade(
            # Administrative
            time=time_millis,
            exchange_name=exchange_name.upper(),

            # Ids
            order_id=order_id,
            trade_id=trade_id,

            # Symbols
            symbol=symbol.upper(),
            base=base_symbol.upper(),
            commission_asset=commission_symbol.upper(),

            # Money from exchange
            commission_fee=commission_fee,
            price=price,
            quantity=quantity,

            # Money Calculated
            money_flow=money_flow,

            # Fair Market Values (Calculated
            fair_market_value_btc_usd=fair_market_value_btc_usd,
            fair_market_value_bnb_usd=fair_market_value_bnb_usd,
            fair_market_value_commission_usd=fair_market_value_com_usd,

            # Booleans
            is_best_match=is_best_match,
            is_buyer=is_buy,
            is_maker=is_maker
        )

        # Insert the row
        try:
            _ = self._session.query(Trade).filter(and_(Trade.trade_id == trade_id, Trade.order_id == order_id)).one()
            # This should never happen, it means we are trying to insert something that already exists..this forces
            #    uniqueness between the combination of the trade_id and order_id combo
            # TODO uncomment below lines once we have smart requesting from binance api
            # print(str(trade_row))
            # assert False  # WHOA!!!! We just tried to add a duplicate...or what seems like a duplicate
        except NoResultFound:
            # print("Not found, adding: " + order_id + ":" + trade_id)
            self._session.add(trade_row)
            self._session.commit()

        return True

    def save_deposit(self,

                     # Administrative
                     insert_time,
                     exchange_name,
                     address,
                     address_tag,
                     tx_id,
                     status,

                     # Money
                     asset,
                     amount):

        deposit_row = Deposit(
            # Administrative
            insert_time=insert_time,
            exchange_name=exchange_name.upper(),
            address=address,
            address_tag=address_tag,
            tx_id=tx_id,
            status=DepositStatusEnum(status),

            # Money
            asset=asset.upper(),
            amount=amount
        )

        try:
            ret = self._session.query(Deposit).filter(and_(Deposit.tx_id == tx_id, Deposit.asset == asset)).one()
            # This forces uniqueness between the combination of the address and asset combo,
            #  we dont add if it already exists
        except NoResultFound:
            # print("Not found, adding: " + order_id + ":" + trade_id)
            self._session.add(deposit_row)
            self._session.commit()

    def save_withdrawal(self,
                        # Administrative
                        withdrawl_id,

                        apply_time,
                        success_time,
                        exchange_name,
                        address,
                        address_tag,
                        tx_id,
                        status,

                        # Money
                        asset,
                        amount):

        withdraw_row = Withdrawal(
            # Administrative
            withdrawl_id=withdrawl_id,
            apply_time=apply_time,
            success_time=success_time,
            exchange_name=exchange_name.upper(),
            address=address,
            address_tag=address_tag,
            tx_id=tx_id,
            status=WithdrawalStatusEnum(status),

            # Money
            asset=asset.upper(),
            amount=amount
        )

        # Insert the row
        try:
            _ = self._session.query(Withdrawal).filter(Withdrawal.withdrawl_id == withdrawl_id).one()
        # do something with existing
        except NoResultFound:
            print("Not found, adding: " + withdrawl_id)
            self._session.add(withdraw_row)
            self._session.commit()

        return True


if __name__ == "__main__":
    di = DatabaseInterface()

    # di.save_deposit()
    #
    # di.save_trade()
    #
    # di.save_withdrawal()

