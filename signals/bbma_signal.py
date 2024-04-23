from typing import List

from MetaTrader5._core import TradePosition

from signals.signal import Signal
import pandas as pd


class BBMASignal(Signal):

    def __init__(self, exit_timeframe, entry_timeframe, window=20, num_std_dev=2):
        super().__init__(exit_timeframe, entry_timeframe)
        self.window = window
        self.num_std_dev = num_std_dev
        self.buy_comment = "buy_bbma"
        self.sell_comment = "sell_bbma"

    def check_buy(self, data: pd.DataFrame):
        # Calculate Bollinger Bands
        data['rolling_mean'] = data['close'].rolling(window=self.window).mean()
        data['upper_band'] = data['rolling_mean'] + self.num_std_dev * data['close'].rolling(window=self.window).std()
        data['lower_band'] = data['rolling_mean'] - self.num_std_dev * data['close'].rolling(window=self.window).std()

        # Generate buy signal if the close price crosses above the lower Bollinger Band
        if (data['close'].iloc[-2] > data['lower_band'].iloc[-2]) and (
                (data['close'].iloc[-3] < data['lower_band'].iloc[-3])):
            return True, self.buy_comment

        else:
            return False, self.buy_comment

    def check_sell(self, data: pd.DataFrame):
        # Calculate Bollinger Bands
        data['rolling_mean'] = data['close'].rolling(window=self.window).mean()
        data['upper_band'] = data['rolling_mean'] + self.num_std_dev * data['close'].rolling(window=self.window).std()
        data['lower_band'] = data['rolling_mean'] - self.num_std_dev * data['close'].rolling(window=self.window).std()

        # Generate sell signal if the close price crosses below the upper Bollinger Band
        if (data['close'].iloc[-2] < data['upper_band'].iloc[-2]) and (
                (data['close'].iloc[-3] > data['upper_band'].iloc[-3])):
            return True, self.sell_comment
        else:
            return False, self.sell_comment


