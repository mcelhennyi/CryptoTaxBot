from FairMarketValue import FairMarketValue
from FairMarketValue.fmv_buffer import FmvBuffer
import http.client
import json
import time
import datetime
import requests

class CryptoCompareInterface(FairMarketValue):
    def __init__(self):
        FairMarketValue.__init__(self, None, None)

        # Buffer to speed up average querying
        self._buf = FmvBuffer()

    def get_average_usd_price_of_btc(self, epoch_millis):
        symbol = 'btc'
        date_string = self._get_date_string(epoch_millis)
        ret_avg = self._buf.get_average(symbol, date_string)
        if ret_avg is not None:
            # print("Average found in buffer")
            return ret_avg
        else:
            # print("Requesting average")
            avg = float(self._request_day_average(epoch_seconds=epoch_millis/1000, from_sym=symbol, to_sym='usd')['USD'])
            assert self._buf.buffer_average(symbol, date_string, avg)
            return avg

    def get_average_usd_price_of_bnb(self, epoch_millis):
        symbol = 'bnb'
        date_string = self._get_date_string(epoch_millis)
        ret_avg = self._buf.get_average(symbol, date_string)
        if ret_avg is not None:
            # print("Average found in buffer")
            return ret_avg
        else:
            # print("Requesting average")
            avg = float(self._request_day_average(epoch_seconds=epoch_millis/1000, from_sym=symbol, to_sym='usd')['USD'])
            assert self._buf.buffer_average(symbol, date_string, avg)
            return avg

    def get_average_usd_price_of_(self, symbol, epoch_millis):
        date_string = self._get_date_string(epoch_millis)
        ret_avg = self._buf.get_average(symbol, date_string)
        if ret_avg is not None:
            # print("Average found in buffer")
            return ret_avg
        else:
            # print("Requesting average")
            avg = float(self._request_day_average(epoch_seconds=epoch_millis/1000, from_sym=symbol, to_sym='usd')['USD'])
            assert self._buf.buffer_average(symbol, date_string, avg)
            return avg

    def get_average_btc_price_of_(self, symbol, epoch_millis):
        # WARNING Don't buffer, because buffer assumes USD
        # print("Requesting average")
        return float(self._request_day_average(epoch_seconds=epoch_millis/1000, from_sym=symbol, to_sym='btc')['BTC'])

    def _request_day_average(self, epoch_seconds, from_sym, to_sym='BTC'):
        # Example request:
        #    https://min-api.cryptocompare.com/data/dayAvg?fsym=BTC&tsym=USD&toTs=1517460356&extraParams=your_app_name

        try_count = 0
        max_try = 5
        while try_count < max_try:
            try:
                r = requests.get('https://min-api.cryptocompare.com/data/dayAvg?fsym=' + str(from_sym).upper() +
                                 '&tsym=' + to_sym.upper() + '&toTs=' + str(int(epoch_seconds)) +
                                 '&extraParams=CryptoTaxBot', timeout=2)
                if r.status_code is not 200:
                    raise Exception("Request not good: " + str(r.status_code))

                return json.loads(r.text)
            except Exception as e:
                print("Warning, Error getting day average price: " + str(e) + "...trying again (" + str(try_count) +
                      "/" + str(max_try) + "...")
                try_count += 1
                time.sleep(1)

        # If we get here we didnt get the response to work, die hard
        assert False

    def _get_date_string(self, epoch_millis):
        st = datetime.datetime.fromtimestamp(epoch_millis/1000).strftime('%Y-%m-%d')
        return st


if __name__ == "__main__":
    cci = CryptoCompareInterface()

    timenow = time.time()

    time_then = timenow #- (86400/3)

    print("then: " + str(time_then) + ", time now: " + str(timenow))

    data = cci._request_day_average(time_then, 'BTC', to_sym="usd")

    # for i in data:
    print(data)
    # print(time.strftime('%Y-%m-%d', time.gmtime(i['time'])))
    print('\n')




"""
Day Avg Documentation:
https://min-api.cryptocompare.com/

        "DayAvg": {
    "Simple": "https://min-api.cryptocompare.com/data/dayAvg?fsym=BTC&tsym=USD&extraParams=your_app_name",
    "Info": {
        "Description": "Get day average price. The values are based on hourly vwap data and the average can be calculated in different waysIt uses BTC conversion if data is not available because the coin is not trading in the specified currency. If tryConversion is set to false it will give you the direct data. If no toTS is given it will automatically do the current day. Also for different timezones use the UTCHourDiff paramThe calculation types are: VWAP - a VWAP of the hourly close price,MidHighLow - the average between the 24 H high and low.VolFVolT - the total volume from / the total volume to (only avilable with tryConversion set to false so only for direct trades but the value should be the most accurate average day price) ",
        "Parameters": [
            {
                "name": "tryConversion",
                "type": "bool",
                "required": false,
                "defaultVal": true,
                "info": "If set to false, it will try to get values without using any conversion at all"
            },
            {
                "name": "fsym",
                "type": "string",
                "required": true,
                "minLen": 1,
                "maxLen": 10,
                "transform": "Uppercase",
                "extraValidation": "KeyInGlobalInfo"
            },
            {
                "name": "tsym",
                "type": "string",
                "required": true,
                "minLen": 1,
                "maxLen": 10,
                "transform": "Uppercase",
                "extraValidation": "KeyInTradePairsOrConversionSymbolTradePairs",
                "baseKey": "fsym"
            },
            {
                "name": "e",
                "type": "string",
                "required": false,
                "defaultVal": "CCCAGG",
                "minLen": 2,
                "maxLen": 30,
                "extraValidation": "MarketInPairMarketList"
            },
            {
                "name": "avgType",
                "type": "string",
                "required": false,
                "defaultVal": "HourVWAP",
                "minLen": 2,
                "maxLen": 30,
                "extraValidation": "AverageType"
            },
            {
                "name": "UTCHourDiff",
                "type": "int",
                "required": false,
                "defaultVal": 0,
                "minValue": -12,
                "maxValue": 14,
                "info": "By deafult it does UTC, if you want a different time zone just pass the hour difference. For PST you would pass -8 for example."
            },
            {
                "name": "toTs",
                "type": "timestamp",
                "required": false,
                "extraValidation": "DayAvgTimestampValidation",
                "secondsInUnit": 3600,
                "cacheLength": 610,
                "maxUnits": 2000,
                "unit": "hour"
            },
            {
                "name": "extraParams",
                "type": "string",
                "required": false,
                "defaultVal": "NotAvailable",
                "minLen": 1,
                "maxLen": 50
            },
            {
                "name": "sign",
                "type": "bool",
                "required": false,
                "defaultVal": false,
                "info": "If set to true, the server will sign the requests."
            }
        ],
        "Examples": [
            "https://min-api.cryptocompare.com/data/dayAvg?fsym=BTC&tsym=USD&UTCHourDiff=-8&extraParams=your_app_name",
            "https://min-api.cryptocompare.com/data/dayAvg?fsym=ETH&tsym=GBP&toTs=1487116800&extraParams=your_app_name",
            "https://min-api.cryptocompare.com/data/dayAvg?fsym=ETH&tsym=GBP&toTs=1487116800&tryConversion=false&extraParams=your_app_name",
            "https://min-api.cryptocompare.com/data/dayAvg?fsym=ETH&tsym=GBP&toTs=1487116800&avgType=MidHighLow&extraParams=your_app_name",
            "https://min-api.cryptocompare.com/data/dayAvg?fsym=ETH&tsym=GBP&toTs=1487116800&avgType=MidHighLow&tryConversion=false&extraParams=your_app_name",
            "https://min-api.cryptocompare.com/data/dayAvg?fsym=ETH&tsym=GBP&toTs=1487116800&avgType=VolFVolT&tryConversion=false&extraParams=your_app_name",
            "https://min-api.cryptocompare.com/data/dayAvg?fsym=BTC&tsym=USD&toTs=1487116800&e=Bitfinex&extraParams=your_app_name"
        ],
        "CacheDuration": "610 seconds",
        "RateLimit": {
            "Hour": 8000,
            "Minute": 300,
            "Second": 15
        }
    }
},




"""