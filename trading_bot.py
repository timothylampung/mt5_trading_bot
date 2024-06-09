import time
from threading import Thread
from typing import List

import MetaTrader5 as mt5
import numpy as np
import pandas as pd

from metatrader_life_cycle import MetatraderLifeCycle, TradeDirection
from signals.ma_ribbon_signal import MaRibbonSignal
from signals.signal import Signal


class TradingBot(MetatraderLifeCycle):

    def on_signal(self):

        if self.get_profit_loss_percentage() < -3:
            print('the account is floating so much, ignoring signals')
            self.time_delay = 180
            return

        positions = mt5.positions_get(symbol=self.symbol)
        if positions is not None and len(positions) > 0:
            self.time_delay = 180
        else:
            self.time_delay = 0.25

        # stop processing if position is greater than 3
        if len(positions) > 2:
            return

        positions = mt5.positions_get(symbol=self.symbol)
        orders = mt5.orders_get(symbol=self.symbol)

        for ss in self.signals:
            entry_bars = mt5.copy_rates_from_pos(self.symbol, ss.get_entry_timeframe(), 0, 200)
            exit_bars = mt5.copy_rates_from_pos(self.symbol, ss.get_exit_timeframe(), 0, 200)

            action, prices = self.predict_signal()
            maximum = prices.max()
            lowest = prices.min()
            print('PROFITABILITY {} {} {} {}'.format(action, prices, maximum, lowest))

            if entry_bars is not None and len(entry_bars) > 0:
                entry_bars_frame = pd.DataFrame(entry_bars)
                exit_bars_frame = pd.DataFrame(exit_bars)

                buy = ss.check_buy(entry_bars_frame)
                sell = ss.check_sell(entry_bars_frame)
                upper, lower = ss.get_stops(exit_bars_frame)
                if ss.check_profit_take(entry_bars_frame) or ss.check_stop_loss(entry_bars_frame):
                    return
                if action == 1 and buy:

                    multiplier = 0
                    total_profit = 0
                    for position in positions:
                        if position.comment == buy[1]:
                            multiplier = multiplier + 1
                            total_profit = total_profit + position.profit
                    volume_ = 0
                    if multiplier == 0 or total_profit > 0:
                        volume_ = self.volume
                    else:
                        volume_ = self.volume * multiplier

                    if total_profit > 0 and multiplier > 0:
                        return

                    self.execute_market_order(volume_, TradeDirection.BUY,
                                              '{}:{}'.format(buy[1], ss.get_entry_timeframe()),
                                              sl=lower, price=lowest, tp=maximum
                                              )
                    time.sleep(1)
                    self.time_delay = 180

                if action == -1 and sell:
                    multiplier = 0
                    total_profit = 0
                    for position in positions:
                        if position.comment == sell[1]:
                            multiplier = multiplier + 1
                            total_profit = total_profit + position.profit
                    volume_ = 0
                    if multiplier == 0 or total_profit > 0:
                        volume_ = self.volume
                    else:
                        volume_ = self.volume * multiplier

                    if total_profit > 0 and multiplier > 0:
                        return

                    self.execute_market_order(volume_, TradeDirection.SELL,
                                              '{}:{}'.format(sell[1], ss.get_entry_timeframe()),
                                              sl=upper, price=maximum, tp=lowest
                                              )
                    self.time_delay = 180

    def on_manage_risk(self):
        positions = mt5.positions_get(symbol=self.symbol)
        # if len(positions) > 0:
        #     for signal in self.signals:
        #         bars = mt5.copy_rates_from_pos(self.symbol, signal.get_exit_timeframe(), 0, 80)
        #         bars_frame = pd.DataFrame(bars)
        #         if isinstance(signal, Signal):
        #             if signal.check_profit_take(bars_frame):
        #                 print('closing reason, profit take')
        #                 self.close_orders(positions, comment='PT')
        #             if signal.check_stop_loss(bars_frame):
        #                 print('closing reason, stop loss')
        #                 self.close_orders(positions)

        # self.close_orders(signal.check_close_buy(positions, bars))
        # self.close_orders(signal.check_close_sell(positions, bars))


class TradingThread(Thread):
    def __init__(self, symbol, volume, signal_providers: List[Signal]):
        self.trading_bot = TradingBot(symbol, volume)
        print('{} {} {}'.format(symbol, volume, signal_providers))
        for signal_provider in signal_providers:
            self.trading_bot.add_signal_provider(signal_provider)
        super().__init__()

    def add_signal_provider(self, signal: Signal):
        self.trading_bot.add_signal_provider(signal)

    def run(self) -> None:
        self.trading_bot.subscribe_to_tick()
        while True:
            self.trading_bot.check_ticks()
            time.sleep(1)


if __name__ == '__main__':

    # get symbols containing RU in their names
    ru_symbols = mt5.symbols_get(group="*USD.ecn*,!*ETH*,*JPY.ecn*,*AUD.ecn*")

    # List of symbols representing cryptocurrencies to be excluded
    crypto_symbols = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA', 'XLM', 'BNB', 'EOS', 'XMR', 'TRX', 'DOT', 'USDT',
                      'DOGE', 'LINK', 'KSM', 'UNI', 'SOL', 'MAT', 'LNK', 'DOG', 'AVX', 'XNG', 'SEK', 'XPT', 'XPD',
                      'XAG', 'SGD', 'NOK',
                      'XLM']
    filtered_symbols = [s for s in ru_symbols if all(crypto not in s.name for crypto in crypto_symbols)]

    bots = [
    ]

    signals = [
        MaRibbonSignal(mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M1),
    ]

    for signal in signals:
        bots.append(TradingThread('XAUUSD.ecn', 1.0, [signal]))

    for bot in bots:
        bot.daemon = True
        bot.start()
    for bot in bots:
        bot.join()
