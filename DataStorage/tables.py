import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Float, BigInteger, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import inspect


# ------------- #
#    Configs    #
# ------------- #

DB_NAME = "temp_db.db"  # This will be the sqlite filename


# ----------------------------- #
# Do not modify below this line #
# ----------------------------- #
Base = declarative_base()


class Trade(Base):
    __tablename__ = 'trades'

    # Define columns below
    row_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary Key

    # Administrative
    time = Column(BigInteger)               # Exchange server time of the trade
    exchange_name = Column(String(30))      # Name of the exchange this trade came from

    # Ids
    order_id = Column(BigInteger)  # ID of overall order
    trade_id = Column(BigInteger, index=True)   # ID of specific part of fill (see binance_logger.py for more info)

    # Symbols
    symbol = Column(String(5))              # Ex: ADABTC, ADA is symbol
    base = Column(String(5))                # Ex: ADABTC, BTC is base
    commission_asset = Column(String(5))    # Could be symbol, base, or other

    # Money from exchange
    commission_fee = Column(Float)          # Value of commission given to exchange
    price = Column(Float)                   # Price in base for the trade
    quantity = Column(Float)                     # Amount of symbol for the trade

    # Money Calculated
    money_flow = Column(Float)              # Money flow, a calculation based on price, fmv, fee, and qty

    # Fair Market Values (Calculated)
    fair_market_value_btc_usd = Column(Float)           # Fair Market value of BTC at time of trade
    fair_market_value_bnb_usd = Column(Float)           # Fair Market value of BNB at time of trade
    fair_market_value_commission_usd = Column(Float)    # Fair Market value of Commission asset, TOT

    # Booleans
    is_best_match = Column(Boolean)     # See api docs (?)
    is_buyer = Column(Boolean)          # Buy/Sell
    is_maker = Column(Boolean)          # See api docs (?)

    # convert to dictionary
    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class DepositStatusEnum(enum.Enum):
    e_pending = 0
    e_success = 1


class WithdrawalStatusEnum(enum.Enum):
    e_email_sent = 0
    e_canceled = 1
    e_awaiting_approval = 2
    e_rejected = 3
    e_processing = 4
    e_failure = 5
    e_completed = 6


class Deposit(Base):
    __tablename__ = 'deposits'

    # Define columns below
    row_id = Column(Integer, primary_key=True, autoincrement=True)

    # Administrative
    insert_time = Column(BigInteger)            # Exchange server time of the deposit
    exchange_name = Column(String(30))          # Name of the exchange this deposit is in
    address = Column(String(200))               # My address at the exchange
    address_tag = Column(BigInteger)            # (?)
    tx_id = Column(String(200))                 # Blockchain tx-id
    status = Column(Enum(DepositStatusEnum))    # see above enum

    # Money
    asset = Column(String(5))                   # Symbol
    amount = Column(Float)                      # Quantity deposited

    # convert to dictionary
    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class Withdrawal(Base):
    __tablename__ = 'withdrawals'

    # Define columns below
    row_id = Column(Integer, primary_key=True, autoincrement=True)

    # Administrative
    withdrawl_id = Column(String(200), unique=True)        # Id of the withdrawal (THIS IS BAD, primary key)
    apply_time = Column(BigInteger)                        # Exchange server time of the withdrawal
    success_time = Column(BigInteger)                      # Exchange server time of the withdrawal
    exchange_name = Column(String(30))                     # Name of the exchange this withdrawal is in
    address = Column(String(200))                          # My address at the exchange
    address_tag = Column(BigInteger)                       # (?)
    tx_id = Column(String(200))                            # Blockchain tx-id
    status = Column(Enum(WithdrawalStatusEnum))            # See above enum

    # Money
    asset = Column(String(5))                   # Symbol
    amount = Column(Float)                      # Quantity withdrawn

    # convert to dictionary
    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}



