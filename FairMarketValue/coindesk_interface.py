from FairMarketValue import FairMarketValue
import http.client
import time
import json

"""
Powered by https://www.coindesk.com/price/

This only works for BTCUSD pair. So each trade will need to be converted to BTC, meaning <coin>ETH wont work.
"""


class CoindeskInterface(FairMarketValue):
    def __init__(self):
        FairMarketValue.__init__(self, None, None)

    def get_closing_price_bitcoin(self, epoch_millis=None, date=None, debug=False):
        """
        Gets the closing price of the day.
        :param epoch_millis: epoch in millis of the day to retrieve
        :param date: date in YYYY-MM-DD format
        :param debug: Enables debugger printouts
        :return: a integer price on the closing that day for bitcoin
        """
        # Decide if epoch or date entry
        if epoch_millis is not None:
            date = time.strftime('%Y-%m-%d', time.localtime(epoch_millis/1000))
        elif date is not None and epoch_millis is not None:
            raise Exception("Please input a date to get closing price")

        # Debug output
        if debug:
            print("Requesting closing price on " + str(date))

        # Get the response from server and parse for single value
        response = self._send_request(date)
        value = self._parse_response(response, str(date))

        # Debug output
        if debug:
            print("Closing value on " + date + " was " + str(value))

        return value

    def _send_request(self, date):
        connection = http.client.HTTPSConnection('api.coindesk.com', timeout=2)
        connection.request('GET', '/v1/bpi/historical/close.json?start=' + date + '&end=' + date)
        response = connection.getresponse()
        if response.status is not 200:
            raise Exception("Request not good: " + str(response.status))

        return json.loads(response.read().decode('utf-8'))

    def _parse_response(self, response, date_requested):
        return int(response['bpi'][date_requested])


if __name__ == "__main__":
    cd = CoindeskInterface()

    epoch = time.time()*1000 - (86400000 * 3)
    print("3 days ago via epoch: ")
    cd.get_closing_price_bitcoin(epoch_millis=epoch, debug=True)

    date_string = "2017-09-01"
    print("...via date YYY-MM-DD: ")
    cd.get_closing_price_bitcoin(date=date_string, debug=True)

    epoch = 1452680400
    print("Another epoch: ")
    cd.get_closing_price_bitcoin(epoch_millis=epoch, debug=True)