from signals.signal import Signal
import pandas as pd
from typing import List
from MetaTrader5._core import TradePosition


class RSIDivergenceSignal(Signal):

    def __init__(self, window: int = 14, rsi_threshold: float = 70):
        super().__init__()
        self.window = window
        self.rsi_threshold = rsi_threshold
        self.buy_comment = "buy_rsi_divergence"
        self.sell_comment = "sell_rsi_divergence"

    def calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def check_buy(self, data: pd.DataFrame):
        rsi = self.calculate_rsi(data)

        # Check for bullish divergence
        price_higher_high = data['close'].iloc[-1] > data['close'].iloc[-2]
        rsi_lower_high = rsi.iloc[-1] < rsi.iloc[-2]

        if price_higher_high and rsi_lower_high:
            return True, self.buy_comment
        else:
            return False, self.buy_comment

    def check_sell(self, data: pd.DataFrame):
        rsi = self.calculate_rsi(data)

        # Check for bearish divergence
        price_lower_low = data['close'].iloc[-1] < data['close'].iloc[-2]
        rsi_higher_low = rsi.iloc[-1] > rsi.iloc[-2]

        if price_lower_low and rsi_higher_low:
            return True, self.sell_comment
        else:
            return False, self.sell_comment
