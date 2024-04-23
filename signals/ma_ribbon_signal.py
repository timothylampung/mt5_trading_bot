from signals.signal import Signal
import pandas as pd
import talib


class MaRibbonSignal(Signal):

    def __init__(self, exit_timeframe, entry_timeframe):
        super().__init__(exit_timeframe, entry_timeframe)
        self.buy_comment = "buy_scalping"
        self.sell_comment = "sell_scalping"

    def check_buy(self, data: pd.DataFrame):
        try:
            # Calculate SMAs using TALib
            data['sma_5'] = talib.SMA(data['close'], timeperiod=5)
            data['sma_8'] = talib.SMA(data['close'], timeperiod=8)
            data['sma_13'] = talib.SMA(data['close'], timeperiod=13)

            buy_condition = (((data['sma_5'].shift(1) < data['sma_13'].shift(1)) & (
                        data['sma_5'] > data['sma_13'])).any() or
                             ((data['sma_5'].shift(1) < data['sma_8'].shift(1)) & (
                                         data['sma_5'] > data['sma_8'])).any()) and \
                            ((data['sma_5'] > data['sma_8']) & (data['sma_8'] > data['sma_13'])).iloc[-1]

            if buy_condition:
                # Calculate Stochastics
                slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'], fastk_period=5, slowk_period=3,
                                           slowk_matype=0, slowd_period=3, slowd_matype=0)
                # Check Stochastics conditions
                if (slowk > 20).iloc[-1] and (slowk > slowd).iloc[-1]:
                    return True, self.buy_comment

            return False, self.buy_comment

        except Exception as e:
            print(e)
            exit()

    def check_sell(self, data: pd.DataFrame):
        try:
            # Calculate SMAs using TALib
            data['sma_5'] = talib.SMA(data['close'], timeperiod=5)
            data['sma_8'] = talib.SMA(data['close'], timeperiod=8)
            data['sma_13'] = talib.SMA(data['close'], timeperiod=13)

            sell_condition = (((data['sma_5'].shift(1) > data['sma_13'].shift(1)) & (
                        data['sma_5'] < data['sma_13'])).any() or
                              ((data['sma_5'].shift(1) > data['sma_8'].shift(1)) & (
                                          data['sma_5'] < data['sma_8'])).any()) and \
                             ((data['sma_5'] < data['sma_8']) & (data['sma_8'] < data['sma_13'])).iloc[-1]

            if sell_condition:
                # Calculate Stochastics
                slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'], fastk_period=5, slowk_period=3,
                                           slowk_matype=0, slowd_period=3, slowd_matype=0)
                # Check Stochastics conditions
                if (slowk < 80).iloc[-1] and (slowk < slowd).iloc[-1]:
                    return True, self.sell_comment

            return False, self.sell_comment

        except Exception as e:
            print(e)
            exit()

    def check_profit_take(self, data: pd.DataFrame):
        # Calculate Bollinger Bands using TALib
        upper_band, middle_band, lower_band = talib.BBANDS(data['close'], timeperiod=13, nbdevup=3, nbdevdn=3)

        # Check for profit-taking based on Bollinger Bands
        if (data['high'] >= upper_band).iloc[-1] or (data['low'] <= lower_band).iloc[-1]:
            return True
        return False

    def get_stops(self, data: pd.DataFrame):
        # Calculate Bollinger Bands using TALib
        upper_band, middle_band, lower_band = talib.BBANDS(data['close'], timeperiod=13, nbdevup=3, nbdevdn=3)
        return upper_band.iloc[-1], lower_band.iloc[-1]

    def check_stop_loss(self, data: pd.DataFrame):
        # Calculate Stochastics using TALib
        slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'], fastk_period=5, slowk_period=3,
                                   slowk_matype=0, slowd_period=3, slowd_matype=0)

        # Check for stop-loss based on Stochastics
        if (slowk < 20).iloc[-1] and (slowk < slowd).iloc[-1]:
            return True
        return False
