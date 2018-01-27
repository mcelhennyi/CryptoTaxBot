from bitcoinaverage import RestfulClient
from FairMarketValue import FairMarketValue
import time


class BitcoinAverage(FairMarketValue):
    def __init__(self, key, secret):
        FairMarketValue.__init__(self, key, secret)
        self._client = None
        self._connect()

    def _connect(self):
        self._client = RestfulClient(secret_key=self._secret, public_key=self._key)
        print("Connected to BitcoinAverage as the fair market value api.")

    def get_fmv_on_date(self, epoch_millis=None, date=None, base_currency="BTC"):
        if epoch_millis is None and date is None:
            raise Exception

        if epoch_millis is not None:
            # todo format for api correctly
            date = time.strftime('%Y-%m-%d', time.localtime(epoch_millis))

