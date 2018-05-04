from FairMarketValue.cryptocompare_interface import CryptoCompareInterface
from Binance.binance_logger_v2 import BinanceLogger

LOGS_DIR = 'logs'


class Main:
    def __init__(self):
        self.fmv = CryptoCompareInterface()
        self.binance = BinanceLogger(self.fmv)

    def run_state(self):
        # Log the exchanges
        self._run_binance_logger()

        # Upload logs to google
        # self._upload_to_google()

    def _run_binance_logger(self):
        self.binance.main()
        # self.binance.test("EDO")

    def _run_kucoin_logger(self):
        pass


if __name__ == "__main__":
    m = Main()
    m.run_state()
