from signals.signal import Signal
import pandas as pd
from typing import List
from MetaTrader5._core import TradePosition


class RSIOversoldOverboughtSignal(Signal):

    def __init__(self, window: int = 14, buy_rsi_threshold: float = 30, sell_rsi_threshold: float = 70):
        super().__init__()
        self.window = window
        self.buy_rsi_threshold = buy_rsi_threshold
        self.sell_rsi_threshold = sell_rsi_threshold
        self.buy_comment = "buy_over_sold"
        self.sell_comment = "sell_over_bought"

    def calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def check_buy(self, data: pd.DataFrame):
        rsi = self.calculate_rsi(data)

        # Generate buy signal if RSI is below the threshold
        if (rsi.iloc[-2] < self.buy_rsi_threshold) and (rsi.iloc[-1] > self.buy_rsi_threshold):
            return True, self.buy_comment
        else:
            return False, self.buy_comment

    def check_sell(self, data: pd.DataFrame):
        rsi = self.calculate_rsi(data)

        # Generate sell signal if RSI is above the threshold
        if (rsi.iloc[-2] > self.sell_rsi_threshold) and (rsi.iloc[-1] < self.sell_rsi_threshold):
            return True, self.sell_comment

        else:
            return False, self.sell_comment


