from binance.client import Client
from FairMarketValue.cryptocompare_interface import CryptoCompareInterface
import time
import datetime
import os, sys
import glob
import pandas

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

        full_csv_txt = ""

        # Iterate over each symbol, pull my trades, and log them with calculations included ...
        #   (profit/loss, fair market value, etc)
        for both in avail_symbols:
            time_start = time.time()

            # Get sym and base
            sym, base = self._split_sym_base(both)
            if sym == "123":
                continue  # Bug in Binance RestAPI causes a return of a "123" symbol, SKIP IT

            # Process the coin pair
            print("\n***************************************\nProcessing " + str(sym) + str(base) + " trades...")
            last_id = self._get_last_fetched_id_for_sym(sym)
            trades_csv, trades_obj = self._get_my_trades_for_symbol(symbol=sym, base=base, id_from=last_id)
            if len(trades_obj) > 0:
                # Log this trade away
                full_csv_txt += trades_csv
                trade_csv_filename = os.path.join(CSV_BASE_LOCATION, date + "_" + sym + ".csv")
                new_file = not os.path.isfile(trade_csv_filename)
                with open(trade_csv_filename, mode='a') as f:
                    # Add the Header
                    if new_file:
                        self._write_header(f)
                    f.write(trades_csv)

            # Constrain main loop to once per second
            time_elapsed = time.time() - time_start
            if time_elapsed < 1:
                time.sleep(1-time_elapsed)
        # Now log all to one file
        with open(os.path.join(CSV_BASE_LOCATION, date + "_all_pairs" + ".csv"), mode='w') as f:
            print("\n***************************************\nLogging all pairs to one file")
            self._write_header(f)
            f.write(full_csv_txt)

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

    def test(self, sym):
        # last_id = self._get_last_fetched_id_for_sym(sym)
        # trades_csv, trades_obj = self._get_my_trades_for_symbol(symbol=sym, base="BTC", id_from=last_id)
        # print("hello")
        pass

    def _get_last_fetched_id_for_sym(self, sym, base="BTC"):
        # Open the last saved file for the given symbol

        # Locate the directory of most recent records, if not already found
        if self._recent_directory is None:
            directories = glob.glob("cached_logs_*")

            if len(directories) is 0:
                # No Cached files, pull as many records as possible
                return None

            # Get the most recent folder
            split_dirs = []
            recent_index = 0
            for i, directory in enumerate(directories):
                split_dirs.append(directory.split("_"))

                # Get most recent folder of cached logs
                if split_dirs[i][YEAR] > split_dirs[recent_index][YEAR]:
                    recent_index = i
                else:
                    if split_dirs[i][MONTH] > split_dirs[recent_index][MONTH] and \
                            split_dirs[i][YEAR] >= split_dirs[recent_index][YEAR]:
                        recent_index = i
                    else:
                        if split_dirs[i][DAY] > split_dirs[recent_index][DAY] and \
                            split_dirs[i][MONTH] >= split_dirs[recent_index][MONTH] and \
                                split_dirs[i][YEAR] >= split_dirs[recent_index][YEAR]:
                            recent_index = i
            self._recent_directory = directories[recent_index]

        # Get the file for the symbol in the directory
        sym_files = glob.glob(os.path.join(self._recent_directory, "*" + sym.upper() + ".csv"))
        if len(sym_files) == 0:
            # No Cached files, pull as many records as possible
            return None

        # Sanity Check
        assert len(sym_files) == 1  # This should only return one file, if it doesnt then we have an issue saving data

        # Load the csv data from the file for this symbol
        df = pandas.read_csv(sym_files[0], usecols=[0, 2])

        # Get index with largest epoch
        row = df[CSV_HEADERS[0]].argmax()
        df_max_epochs = df.loc[df[CSV_HEADERS[0]] == df[CSV_HEADERS[0]][row]]
        max_trade_id = df_max_epochs[CSV_HEADERS[2]].argmax()
        trade_id = df[CSV_HEADERS[2]][max_trade_id]

        return trade_id

    def _get_last_profit_loss_for_sym(self, sym):

        # TODO: query for old logs, and pull out the last profit/loss value from the log and return it

        return 0

    def _get_my_trades_for_symbol(self, symbol, base, id_from=None):
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
        if id_from is None:
            print("No cached_logs for " + symbol + " found, pulling all past trades...")
            trades_obj = self.client.get_my_trades(symbol=symbol+base)
        else:
            print("Cached_logs for " + symbol + base + " found, pulling trades since " + str(id_from) + " trade 'id'")
            trades_obj = self.client.get_my_trades(symbol=symbol+base, fromId=id_from+1)

        # Generate the CSV for this pair
        trades_csv = self._get_csv_from_trades(trades_obj,
                                               last_profit_loss=self._get_last_profit_loss_for_sym(symbol.upper()),
                                               base_currency=base,
                                               symbol=symbol)
        
        return trades_csv, trades_obj

    def _add_field(self, value, endl=''):
        return str(value) + "," + endl

    def _get_csv_from_trades(self, trades, last_profit_loss=None, base_currency='BTC', symbol=''):
        csv_text = ""
        num_trades = len(trades)
        profit_loss = 0
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

            # Profit and loss is just the money flow for a given coin, plus the past profit loss.
            #  Note this should only be written to the file, and in the last row.
            profit_loss += money_flow
            logged_profit_loss = 0
            if i == num_trades-1:
                # We are on the last trade (last row), log profit/loss for it
                logged_profit_loss = profit_loss + last_profit_loss

            # Add this entry to the csv
            csv_text += self._data_to_csv(time_millis=trade['time'],
                                          trade_id=trade['id'],
                                          order_id=trade['orderId'],
                                          symbol=symbol,
                                          base_symbol=base_currency,
                                          quantity=trade['qty'],
                                          price=trade['price'],
                                          commission_fee=trade['commission'],
                                          commission_symbol=trade['commissionAsset'],
                                          profit_loss=logged_profit_loss,
                                          money_flow=money_flow,
                                          fair_market_value_btc_usd=fair_market_value_btc_usd,
                                          fair_market_value_bnb_usd=fair_market_value_bnb_usd,
                                          fair_market_value_com_usd=fair_market_value_com_usd,
                                          is_buy=is_buy,
                                          is_maker=trade['isMaker'],
                                          is_best_match=trade['isBestMatch'])

        return csv_text

    def _data_to_csv(self,
                     time_millis,
                     trade_id,
                     order_id,
                     symbol,
                     base_symbol,
                     quantity,
                     price,
                     commission_fee,
                     commission_symbol,
                     profit_loss,
                     money_flow,
                     fair_market_value_btc_usd,
                     fair_market_value_bnb_usd,
                     fair_market_value_com_usd,
                     is_buy,
                     is_maker,
                     is_best_match
                     ):

        csv_text = ""

        # Time
        csv_text += self._add_field(time_millis)                            # Epoch type time
        csv_text += self._add_field(self._get_my_time_string(time_millis))  # Human readable local time

        # Ids
        csv_text += self._add_field(trade_id)                      # Id
        csv_text += self._add_field(order_id)                      # OrderId
        csv_text += self._add_field(symbol + base_symbol)          # Trading Pair

        # Trade value data aka $$$ MONEY
        csv_text += self._add_field(quantity)                      # Quantity purchased
        csv_text += self._add_field(price)                         # Price in base currency per coin
        csv_text += self._add_field(commission_fee)                # Commission paid to binance
        csv_text += self._add_field(commission_symbol)             # Type of coin used to pay binance
        csv_text += self._add_field(profit_loss)                   # Profit/Loss (+/-)
        csv_text += self._add_field(money_flow)                    # Money Flow
        csv_text += self._add_field(fair_market_value_btc_usd)     # Fair Market value of BTC at time of trade
        csv_text += self._add_field(fair_market_value_bnb_usd)     # Fair Market value of BNB at time of trade
        csv_text += self._add_field(fair_market_value_com_usd)     # Fair Market value of Commission asset, TOT

        # Trade Transaction details
        csv_text += self._add_field('Buy' if is_buy else 'Sell')   # Buy/sell
        csv_text += self._add_field(is_maker)  # isMaker
        csv_text += self._add_field(is_best_match, endl='\r')      # isBestMatch ***last entry gets endl***

        return csv_text

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

    # TODO find profit/loss, this could be a little difficult unless "loss" is when i buy, and "profit" is when I sell?
    def _get_profit_loss(self, money_flow_total):
        return 0  # TODO Low priority, this can always be post processed

    def _write_header(self, f):
        header_csv = ""
        header_len = len(CSV_HEADERS)
        for i, head in enumerate(CSV_HEADERS):
            header_csv += self._add_field(head, endl='\r' if i+1 == header_len else '')
        f.write(header_csv)


if __name__ == "__main__":
    bl = BinanceLogger()
    bl.main()
