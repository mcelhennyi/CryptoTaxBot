from binance.client import Client
from FairMarketValue import FairMarketValue
from FairMarketValue.bitcoin_average import BitcoinAverage
import time
import datetime
import os, sys


KEY_FILE = "../.keys"
CSV_BASE_LOCATION = "../logs"
CSV_HEADERS = ['Epoch Time', 'Date/Time', 'Id', 'OrderId', 'Trading Pair', 'Quantity', 'Price in base currency',
               'Commission paid to exchange', 'Commision coin type', 'Profit/Loss (+/-)', 'Fair Market Value',
               'Buy/Sell', 'isMaker', 'isBestMatch']

if not os.path.isdir(CSV_BASE_LOCATION):
    os.mkdir(CSV_BASE_LOCATION)

# ASSUMES BASE CURRENCY TICKER IS ONLY 3 CHARS LONG!!!!
# Due to Binance's api limits of 120 requests per-minute, this will only send one call per second.
#  Therefore, pulling records for every coin can take about 2 minutes (as of Jan 2018)


class BinanceLogger:
    def __init__(self):
        api_key, api_secret, fmv_api_name, fmv_key, fmv_secret = self.load_keys()
        print("Connecting to binance...")
        self.client = Client(api_key, api_secret)
        print("Connected!")

        self._fmv = None
        if fmv_api_name == "btcavg":
            self._fmv = BitcoinAverage(key=fmv_key, secret=fmv_secret)
        else:
            print("Please check name of key for your FMV api, if it is not supported this program will not work.")
            exit(-1)

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
        fmv_api_name_key = lines_split[2].split('=')[0].split('-')[0].strip(' ')
        fmv_key = lines_split[2].split('=')[1].strip(' ')
        fmv_api_name_secret = lines_split[2].split('=')[0].split('-')[0].strip(' ')
        fmv_secret = lines_split[3].split('=')[1].strip(' ')

        # Make sure the fmv client name is the same
        if fmv_api_name_key != fmv_api_name_secret:
            print("Error: FMV client is not the same name for both keys in .keys file.")
            exit()

        return key, secret, fmv_api_name_key, fmv_key, fmv_secret

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
        for sym in avail_symbols:
            # Get sym and base
            base = sym[-3:]
            sym = str(sym).split(base)[0]

            # if base == 'BTC' or base == 'ETH':
            # print(sym+base)

            # Open up a log for this coin only
            trades_csv, trades_obj = self._get_my_trades_for_symbol(symbol=sym, base=base)
            if len(trades_obj) > 0:
                # Log this trade away
                print("Logging for " + str(sym))
                full_csv_txt += trades_csv
                with open(os.path.join(CSV_BASE_LOCATION, date + "_" + sym + ".csv"), mode='w') as f:
                    # Add the Header
                    self._write_header(f)
                    f.write(trades_csv)

            time.sleep(1)
        # Now log all to one file
        with open(os.path.join(CSV_BASE_LOCATION, date + "_all_pairs" + ".csv"), mode='w') as f:
            print("Logging all pairs to one file")
            self._write_header(f)
            f.write(full_csv_txt)

        print("Done!")

    @staticmethod
    def _get_my_time_string(time_millis):
        return datetime.datetime.fromtimestamp(time_millis/1000).strftime('%c')

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

    def _get_my_trades_for_symbol(self, symbol, base):
        """
        trades is an array of dictionaries. Each dictionary is a different trade I made.
        Each dictionary contains the following tags:
            commission: The cost of the transaction that binance takes
            isMaker: ?
            isBuyer: True if this was a buy, false if it was a sell
            time: time since epoch, use _get_my_time_string(time_millis) to get string time
            qty: The amount of coin filled
            id: ? (A unique id, seems like this value is the ID for this symbol) This is the same ID that is used to
                modify the return in the 'fromId' field for the client.get_my_trades() call. If the ID sent
                is less than or equal to other Ids, those trades are returned.
            isBestMatch: ?
            orderId: ? (A unique id, seems like this value is a global trade ID)
            price: price of the coin, in base currency.
            commissionAsset: The currency used to pay the commission to binance.

        :param symbol:
        :return: trades array
        """

        trades_obj = self.client.get_my_trades(symbol=symbol+base) #, fromId=0)  # todo: fromId can be used to reduce response
        trades_csv = self._get_csv_from_trades(trades_obj, base_currency=base, symbol=symbol)
        # -- Stupid debug code to test what the ids are for --
        # if len(trades) > 0:
        #     if self.temp_time <= trades[0]['time']:
        #         if self.temp_id <= trades[0]['orderId']:
        #             print("GOOD 1")
        #         else:
        #             print("BAD 1")
        #     elif self.temp_time >= trades[0]['time']:
        #         if self.temp_id >= trades[0]['orderId']:
        #             print("GOOD 2")
        #         else:
        #             print("BAD 2")
        #
        #     self.temp_time = trades[0]['time']
        #     self.temp_id = trades[0]['id']

        return trades_csv, trades_obj

    def _add_field(self, value, endl=''):
        return str(value) + "," + endl

    def _get_csv_from_trades(self, trades, base_currency='BTC', symbol=''):
        csv_text = ""
        for trade in trades:
            is_buy = trade['isBuyer']
            fair_market_value = self._fmv.get_fmv_on_date(epoch_millis=trade['time'], base_currency=base_currency)
            profit_loss = self._get_profit_loss(trade['price'], trade['qty'], fair_market_value)

            # Time
            csv_text += self._add_field(trade['time'])                              # Epoch type time
            csv_text += self._add_field(self._get_my_time_string(trade['time']))    # Human readable local time

            # Ids
            csv_text += self._add_field(trade['id'])                                # Id
            csv_text += self._add_field(trade['orderId'])                           # OrderId
            csv_text += self._add_field(symbol+base_currency)                       # Trading Pair

            # Trade value data aka $$$ MONEY
            csv_text += self._add_field(trade['qty'])                       # Quantity purchased
            csv_text += self._add_field(trade['price'])                     # Price in base currency per coin
            csv_text += self._add_field(trade['commission'])                # Commission paid to binance
            csv_text += self._add_field(trade['commissionAsset'])           # Type of coin used to pay binance
            csv_text += self._add_field(profit_loss)                        # Profit/Loss (+/-)
            csv_text += self._add_field(fair_market_value)                  # Fair Market value of BTC at time of trade

            # Trade Transaction details
            csv_text += self._add_field('Buy' if is_buy else 'Sell')        # Buy/sell
            csv_text += self._add_field(trade['isMaker'])                   # isMaker
            csv_text += self._add_field(trade['isBestMatch'], endl='\r')    # isBestMatch ***last entry gets endl***

        return csv_text

    # TODO find profit/loss, this could be a little difficult unless "loss" is when i buy, and "profit" is when I sell?
    def _get_profit_loss(self, price, qty, fair_market_value):
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
