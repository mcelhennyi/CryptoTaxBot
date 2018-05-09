from sqlalchemy import create_engine
from sqlalchemy.sql import text
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
    def __init__(self, verbose=False, db_loc_offset=''):
        self._engine = create_engine('sqlite:///'+ db_loc_offset + DB_NAME, echo=verbose)
        _Session = sessionmaker(bind=self._engine)
        self._session = _Session()

        # Create the tables
        Base.metadata.create_all(self._engine)  # Base come from tables.py import

    def query_all_withdrawals(self, exchange):
        query = self._session.query(Withdrawal).filter(Withdrawal.exchange_name == exchange.upper())
        query_results = query.all()
        return Withdrawal.__table__.columns.keys(), query_results  # TODO: Note: this is a return of all column names.

    def query_all_deposits(self, exchange):
        # stmt = stmt.columns(Deposit.insert_time, Deposit.amount, Deposit.asset)
        query = self._session.query(Deposit).filter(Deposit.exchange_name == exchange.upper())
        query_results = query.order_by(Deposit.insert_time).all()
        return Deposit.__table__.columns.keys(), query_results  # TODO: Note: this is a return of all column names.

    def get_all_symbols_for_exchange(self, exchange):
        query = self._session.query(Trade.symbol).distinct(Trade.symbol).filter(Trade.exchange_name == exchange.upper())
        query_results = query.all()
        return query_results

    def has_deposits(self, symbol, exchange):
        query = self._session.query(Deposit.row_id).filter(Deposit.exchange_name == exchange.upper(),
                                                           Deposit.asset == symbol.upper())
        query_results = query.all()
        if len(query_results) > 0:
            return True
        else:
            return False

    def has_withdrawals(self, symbol, exchange):
        query = self._session.query(Withdrawal.row_id).filter(Withdrawal.exchange_name == exchange.upper(),
                                                              Withdrawal.asset == symbol.upper())
        query_results = query.all()
        if len(query_results) > 0:
            return True
        else:
            return False

    def get_profit_for_pair(self, symbol, base):
        pass

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
    di = DatabaseInterface(db_loc_offset='../')

    # ----------------------------------------------- #
    # -- Test getting profit/loss for a given coin -- #
    # ----------------------------------------------- #
    # Exchange to check for
    exchange = 'binance'

    # Get all coins
    symbols = di.get_all_symbols_for_exchange(exchange)

    # for each coin check if it has any deposits/withdrawals...skip that coin for now
    for coin_tuple in symbols:
        # get all symbols returns a tuple, first index being the coin
        coin = coin_tuple[0]
        if di.has_deposits(coin, exchange) or di.has_withdrawals(coin, exchange):
            print(coin + " has deposits/withdrawals, skipping for now.")
        else:
            pass


    # di.save_deposit()
    #
    # di.save_trade()
    #
    # di.save_withdrawal()

