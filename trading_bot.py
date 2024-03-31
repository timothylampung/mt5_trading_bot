import time
from threading import Thread
import MetaTrader5 as mt5

from metatrader_life_cycle import MetatraderLifeCycle


class TradingBot(MetatraderLifeCycle):

    def on_signal(self):
        pass

    def on_manage_risk(self):
        pass


class TradingThread(Thread):
    def __init__(self, symbol, timeframe):
        self.trading_bot = TradingBot(symbol, timeframe)
        super().__init__()

    def run(self) -> None:
        self.trading_bot.subscribe_to_tick()
        while True:
            self.trading_bot.check_ticks()
            time.sleep(.25)


if __name__ == '__main__':
    bots = [TradingThread("BTCUSD.ecn", mt5.TIMEFRAME_M1),
            TradingThread("EURUSD.ecn", mt5.TIMEFRAME_M1),
            TradingThread("BTCUSD.ecn", mt5.TIMEFRAME_H1),
            TradingThread("EURUSD.ecn", mt5.TIMEFRAME_H1), ]

    for bot in bots:
        bot.daemon = True
        bot.start()
    for bot in bots:
        bot.join()
