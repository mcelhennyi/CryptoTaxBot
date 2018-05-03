from FairMarketValue.cryptocompare_interface import CryptoCompareInterface
from Binance.binance_logger import BinanceLogger
import time
import os, sys

LOGS_DIR = 'logs'


class Main:
    def __init__(self):
        self.fmv = CryptoCompareInterface()
        self.binance = BinanceLogger(self.fmv)

    def run_state(self):
        # Cache old log files, get start IDS for this pull
        self._cache_old_logs()

        # Log the exchanges
        self._run_binance_logger()
        # self._run_binance_logger()

        # Upload logs to google
        # self._upload_to_google()

    def _run_binance_logger(self):
        self.binance.main()
        # self.binance.test("EDO")

    def _run_kucoin_logger(self):
        pass

    def _upload_to_google(self):
        print("Preparing to upload to google drive...")

        print("Upload complete.")

    def _cache_old_logs(self):
        # Move old logs to cached folder, so they overwritten
        print("Preparing to cache old logs, if any...")
        is_initial_file = True
        if os.path.isdir(LOGS_DIR):
            for file in os.listdir(LOGS_DIR):

                date = file.split('_')
                new_folder = os.path.join(os.getcwd(), "cached_logs_" + date[0] + "_" + date[1] + "_" + date[2])

                if os.path.isdir(new_folder) and is_initial_file:
                    print("WARNING: This project already contains a cached log folder for the date: " + new_folder)
                    exit(-1)

                new_filename = os.path.join( new_folder, file)
                old_filename = os.path.join(os.getcwd(), os.path.join(LOGS_DIR, file))
                print("Old file: " + str(old_filename))
                print("New file: " + str(new_filename))
                # Make sure the dir is there
                if not os.path.isdir(new_folder):
                    os.mkdir(new_folder)

                # Move files
                os.rename(old_filename, new_filename)
                is_initial_file = False
        print("Caching complete.")


if __name__ == "__main__":
    m = Main()
    m.run_state()
