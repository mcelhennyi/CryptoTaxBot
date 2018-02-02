

class FmvBuffer:
    def __init__(self):
        self._buffer = {}

    def buffer_average(self, sym, date, value):
        """
        This adds an average to the buffer
        :param sym:
        :param date:
        :param value:
        :return:
        """
        sym = sym.upper()

        if self._has_sym(sym):
            if self._sym_has_date(sym, date):
                return False
            else:
                self._buffer[sym][date] = value
                return True
        else:
            # Create a blank dictionary for this symbol
            self._buffer[sym] = {}

            # Reuse above code after adding in the symbol
            return self.buffer_average(sym, date, value)

    def get_average(self, sym, date):
        """
        This gets a buffered average if it exists
        :param sym:
        :param date:
        :return:
        """
        sym = sym.upper()

        if self._sym_has_date(sym, date):
            return self._buffer[sym][date]
        else:
            return None

    def _sym_has_date(self, sym, date):
        """
        Checks if there is a given date entry for a given symbol
        :param sym:
        :param date:
        :return:
        """
        if self._has_sym(sym):
            found = False
            # iterate over each date key for a given symbol
            for date_key in self._buffer[sym]:
                if date == date_key:
                    found = True

            return found
        else:
            return False

    def _has_sym(self, sym):
        """
        Checks if there is this symbol in the buffer
        :param sym:
        :return:
        """
        if sym in self._buffer:
            return True
        else:
            return False


if __name__ == "__main__":
    buf = FmvBuffer()

    buf.buffer_average("btc", 0, 1234)
    buf.buffer_average('btc', 4, 2345)

    buf.buffer_average("eth", 0, 9876)

    print(buf.get_average('btc', 4))