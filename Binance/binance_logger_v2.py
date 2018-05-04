from binance.client import Client
from FairMarketValue.cryptocompare_interface import CryptoCompareInterface
import time
import datetime
import os, sys
import glob
import pandas
from DataStorage.database_interface import DatabaseInterface
from Utils.helper_functions import repeated_try

KEY_FILE = ".keys"
CSV_BASE_LOCATION = "logs"
CSV_HEADERS = ['Epoch Time', 'Date/Time', 'Id', 'OrderId', 'Trading Pair', 'Quantity', 'Price in base currency',
               'Commission paid to exchange', 'Commision coin type (CCT)', 'Profit/Loss (+/-) (BTC)', 'Money Flows USD',
               'Fair Market Value USD (1-BTC)', 'Fair Market Value USD (1-BNB)', 'Fair Market Value USD (1-CCT)',
               'Buy/Sell', 'isMaker', 'isBestMatch']
# Indices of date in folder name
YEAR = 2
MONTH = 3
DAY = 4


if not os.path.isdir(CSV_BASE_LOCATION):
    os.mkdir(CSV_BASE_LOCATION)

# ASSUMES BASE CURRENCY TICKER IS ONLY 3 CHARS LONG!!!!
# Due to Binance's api limits of 120 requests per-minute, this will only send one call per second.
#  Therefore, pulling records for every coin can take about 2 minutes (as of Jan 2018)


class BinanceLogger:
    def __init__(self, fmv=None):
        api_key, api_secret = self.load_keys()
        print("Connecting to binance...")
        self.client = Client(api_key, api_secret)
        print("Connected!")

        if fmv is None:
            self._fmv = CryptoCompareInterface()
        else:
            self._fmv = fmv

        self._recent_directory = None
        self._database = DatabaseInterface()

    @staticmethod
    def load_keys():
        # Load key file to memory
        with open(KEY_FILE, mode='r') as f:
            lines = ""
            for line in f:
                lines += line

        # format:
        # key = <key>
        # secret = <secret>
        # fmv-key = <key>
        # fmv-secret = <secret>
        lines_split = lines.split('\n')
        key = lines_split[0].split('=')[1].strip(' ')
        secret = lines_split[1].split('=')[1].strip(' ')

        return key, secret

    def main(self):
        # Get date for file titles
        date = datetime.datetime.now().strftime("%Y_%m_%d")

        # fetch list of withdrawals
        # withdraws = self.client.get_withdraw_history()
        # info = self.client.get_exchange_info()

        # Poll for all symbols in exchange
        print("Polling for symbols...")
        avail_symbols = self._get_list_symbols_available()

        # Iterate over each symbol, pull my trades, and log them with calculations included ...
        #   (profit/loss, fair market value, etc)
        # for i, both in enumerate(avail_symbols):
        #     time_start = time.time()
        #
        #     # Get sym and base
        #     sym, base = self._split_sym_base(both)
        #     if sym == "123":
        #         continue  # Bug in Binance RestAPI causes a return of a "123" symbol, SKIP IT
        #
        #     # Process the coin pair
        #     print("\n***************************************\nProcessing " + str(sym) + str(base) + " trades...")
        #
        #     # Save trades off to database
        #     # self._save_my_trades_for_symbol(symbol=sym, base=base)  # TODO: get last_id to not pull all trades
        #
        #
        #     print("\n\t-- Progress: " + str(i+1) + "/" + str(len(avail_symbols)) + " symbol pairs processed. --")
        #
        #     # Constrain main loop to once per second
        #     time_elapsed = time.time() - time_start
        #     if time_elapsed < 1:
        #         time.sleep(1-time_elapsed)

        # Save off the deposits to database
        self._save_my_deposits()

        # Save off the withdrawls to database
        self._save_my_withdrawals()

        print("\nDone!")

    @staticmethod
    def _get_my_time_string(time_millis):
        return datetime.datetime.fromtimestamp(time_millis/1000).strftime('%c')

    def _split_sym_base(self, both):
        """
        Split both into a sym+base pair. Can handle <n number of letters><3 letters> and <n number of letters>USDT

        :param both:
        :return:
        """
        last_three = both[-3:]
        sym = str(both).split(last_three)[0]
        if last_three == "SDT":
            base = both[-4:]
            sym = str(both).split(base)[0]
            return sym, base
        else:
            base = last_three

        return sym, base

    def _print_withdraw_entry(self, withdraw):
        print("Address " + str(withdraw['address']))
        print("\taddressTag " + str(withdraw['addressTag']))
        print("\tamount " + str(withdraw['amount']))
        print("\tapplyTime " + str(withdraw['applyTime']))
        print("\tasset " + str(withdraw['asset']))
        print("\tid " + str(withdraw['id']))
        print("\tstatus " + str(withdraw['status']))
        print("\tsuccessTime " + str(withdraw['successTime']))
        time_success = int(withdraw['successTime'])
        print("\t\tTime: " + str(BinanceLogger._get_my_time_string(time_success)))
        print("\ttxId " + str(withdraw['txId']))
        print("\taddress " + str(withdraw['address']))

    def _get_list_symbols_available(self):
        info = self.client.get_exchange_info()
        avail_sym = []
        for symbol in info['symbols']:
            avail_sym.append(symbol['symbol'])

        return avail_sym

    def _save_my_deposits(self):

        # Get the withdrawals
        deposits = repeated_try(callback=self.client.get_deposit_history, function_name="get_deposit_history")

        for deposit in deposits['depositList']:
            # Save them to the database
            self._database.save_deposit(
                                        # Administrative
                                        insert_time=deposit['insertTime'],
                                        exchange_name="BINANCE",
                                        address=deposit['address'],
                                        address_tag=deposit['addressTag'],
                                        tx_id=deposit['txId'],
                                        status=deposit['status'],

                                        # Money
                                        asset=deposit['asset'],
                                        amount=deposit['amount'])

        return deposits

    def _save_my_withdrawals(self):

        # Get the withdrawals
        withdrawals = repeated_try(callback=self.client.get_withdraw_history, function_name="get_withdraw_history")

        for withdrawal in withdrawals['withdrawList']:
            # Save them to the database
            self._database.save_withdrawal(
                                           # Administrative
                                           withdrawl_id=withdrawal['id'],
                                           apply_time=withdrawal['applyTime'],
                                           success_time=withdrawal['successTime'],
                                           exchange_name="BINANCE",
                                           address=withdrawal['address'],
                                           address_tag=withdrawal['addressTag'],
                                           tx_id=withdrawal['txId'],
                                           status=withdrawal['status'],

                                           # Money
                                           asset=withdrawal['asset'],
                                           amount=withdrawal['amount'])

        return withdrawals

    def _save_my_trades_for_symbol(self, symbol, base, id_from=None):
        """
        trades is an array of dictionaries. Each dictionary is a different trade I made.
        Each dictionary contains the following tags:
            commission: The cost of the transaction that binance takes
            isMaker: ?
            isBuyer: True if this was a buy, false if it was a sell
            time: time since epoch, use _get_my_time_string(time_millis) to get string time
            qty: The amount of coin filled
            id: This is a child of order ID and is representative of parts of an order. This is the same ID that is used to
                modify the return in the 'fromId' field for the client.get_my_trades() call. If the ID sent
                is less than or equal to other Ids, those trades are returned.
            isBestMatch: ?
            orderId: This is the ID of the order.
            price: price of the coin, in base currency.
            commissionAsset: The currency used to pay the commission to binance.

        :param symbol:
        :return: processed trades csv, trades json obj
        """

        # Retrieve the trade data for this pair from binance
        trades_obj = None
        if id_from is None:
            print("No cached_logs for " + symbol + " found, pulling all past trades...")
            trades_obj = repeated_try(callback=self.client.get_my_trades, function_name="get_my_trades",
                                      symbol=symbol+base)
        else:
            print("Cached_logs for " + symbol + base + " found, pulling trades since " + str(id_from) + " trade 'id'")
            trades_obj = repeated_try(callback=self.client.get_my_trades, function_name="get_my_trades",
                                      symbol=symbol+base, fromId=id_from+1)

        # Save off to database, calculate money flow
        self._save_to_database(trades_obj,
                               base_currency=base,
                               symbol=symbol)

        return trades_obj

    def _save_to_database(self, trades, base_currency='BTC', symbol=''):
        """
        This will call the save_trade function of the database object after calculating fmv and money flow.

        :param trades:
        :param base_currency:
        :param symbol:
        :return:
        """
        num_trades = len(trades)
        for i, trade in enumerate(trades):
            # trade['time'] IS in milliseconds
            print("Processing " + symbol+base_currency + " trades " + str(i+1) + "/" + str(num_trades) + "...")
            is_buy = trade['isBuyer']
            fair_market_value_btc_usd = self._fmv.get_average_usd_price_of_btc(epoch_millis=trade['time'])
            fair_market_value_bnb_usd = self._fmv.get_average_usd_price_of_bnb(epoch_millis=trade['time'])
            fair_market_value_base_usd = self._fmv.get_average_usd_price_of_(symbol=base_currency,
                                                                             epoch_millis=trade['time'])
            fair_market_value_com_usd = self._fmv.get_average_usd_price_of_(symbol=trade['commissionAsset'],
                                                                            epoch_millis=trade['time'])
            # Calculates the fee of the transaction
            fee = self._get_fee(commission_paid=float(trade['commission']),
                                commission_symbol=trade['commissionAsset'],
                                epoch_millis=trade['time'])

            # Calculate the money flow. This is not profit loss, but rather how much spent or how much received.
            money_flow = self._get_money_flow(quantity=float(trade['qty']),
                                              value_of_sym_in_base_currency=float(trade['price']),
                                              base_fmv=fair_market_value_base_usd,
                                              fee_usd=fee,
                                              is_buy=is_buy)

            # Add this entry to the database
            self._database.save_trade(time_millis=trade['time'],
                                      trade_id=trade['id'],
                                      order_id=trade['orderId'],
                                      symbol=symbol,
                                      base_symbol=base_currency,
                                      quantity=trade['qty'],
                                      price=trade['price'],
                                      commission_fee=trade['commission'],
                                      commission_symbol=trade['commissionAsset'],
                                      money_flow=money_flow,
                                      fair_market_value_btc_usd=fair_market_value_btc_usd,
                                      fair_market_value_bnb_usd=fair_market_value_bnb_usd,
                                      fair_market_value_com_usd=fair_market_value_com_usd,
                                      is_buy=is_buy,
                                      is_maker=trade['isMaker'],
                                      is_best_match=trade['isBestMatch'],
                                      exchange_name="binance")

    def _get_fee(self, commission_paid, commission_symbol, epoch_millis):
        """
        This takes the commission asset, get its value in USD then multiplies the commission paid times its value in
          USD to get the commission/fee pain in USD
        :param commission_paid:
        :param commission_symbol:
        :param epoch_millis:
        :return:
        """
        currency_in_usd = self._fmv.get_average_usd_price_of_(symbol=commission_symbol, epoch_millis=epoch_millis)
        return commission_paid * currency_in_usd

    def _get_money_flow(self, quantity, value_of_sym_in_base_currency, base_fmv, fee_usd, is_buy):
        """
        These values are all USD.
        :param quantity:
        :param value_of_sym_in_base_currency:
        :param base_fmv:
        :param fee_usd:
        :param is_buy:
        :return:
        """
        if is_buy:
            # If we are buying this we count it as a negative flow.
            # However if we are buying we want the fee to look like an outflow, so we add it
            #             n1  *          amt of <sym>          * USD / <sym>  + $USD
            flow = -((quantity * value_of_sym_in_base_currency * base_fmv) + fee_usd)
        else:
            # We sold, so we need to show our profit as a positive flow, but the fee is still a negative flow
            flow = quantity * value_of_sym_in_base_currency * base_fmv - fee_usd

        return flow


if __name__ == "__main__":
    bl = BinanceLogger()
    bl.main()
