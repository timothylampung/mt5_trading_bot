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
    bot1 = TradingThread("BTCUSD.ecn", mt5.TIMEFRAME_M1)
    bot5 = TradingThread("BTCUSD.ecn", mt5.TIMEFRAME_M5)
    bot15 = TradingThread("BTCUSD.ecn", mt5.TIMEFRAME_M15)
    # bot1.daemon = False
    # bot5.daemon = False
    # bot15.daemon = False

    bot1.start()
    bot5.start()
    bot15.start()

    bot1.join()
    bot5.join()
    bot15.join()
