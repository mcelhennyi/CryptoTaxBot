from coinapi_sdk.python_rest.coinapi_v1 import CoinAPIv1
from FairMarketValue import FairMarketValue
import time


class CoinApiInterface(FairMarketValue):
    def __init__(self, key, secret):
        FairMarketValue.__init__(self, key, secret)
        self._client = None
        self._connect(key, secret)

    def _connect(self, key, secret):
        self._client = CoinAPIv1(api_key=key)
        print("Connected to BitcoinAverage as the fair market value api.")

    def get_fmv_on_date(self, epoch_millis=None, date=None, base_currency="BTC"):
        assert isinstance(self._client, CoinAPIv1)
        if epoch_millis is None and date is None:
            raise Exception("There needs to be a date entered for a fair market value")

        if epoch_millis is not None:
            # todo format for api correctly
            date = time.strftime('%Y-%m-%d', time.localtime(epoch_millis))

        # self._client.



if __name__ == "__main__":
    from Binance.binance_logger import BinanceLogger
    _, _, _, akey, asecret = BinanceLogger.load_keys()
    ba = CoinApiInterface(key=akey, secret=asecret)

    print(ba.get_fmv_on_date(epoch_millis=1517285685))
