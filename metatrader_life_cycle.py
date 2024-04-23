import asyncio
from enum import Enum
from typing import List

import pandas as pd
import MetaTrader5 as mt5
import random
from datetime import datetime, timedelta

from signals.bbma_signal import BBMASignal
from signals.ma_ribbon_signal import MaRibbonSignal
from signals.rsi_oversold_overbought_signal import RSIOversoldOverboughtSignal
from signals.signal import Signal
from telegram_bot import send_message


def initialize_mt5():
    if not mt5.initialize():
        print("failed to initialized mt5 {}".format(mt5.last_error()))
        disconnect_mt5()
        quit()


def disconnect_mt5():
    mt5.shutdown()


class TradeDirection(Enum):
    BUY = 0
    SELL = 1


initialize_mt5()


class MetatraderLifeCycle:
    def __init__(self, symbol: str, volume=0.01):
        self.symbol = symbol
        self.previous_bid = self.get_symbol_info().bid
        self.previous_ask = self.get_symbol_info().ask
        self.time_delay = 0.25
        self.signal_start_time = datetime.now()
        self.volume = volume
        self.signals = []

    def add_signal_provider(self, signal: Signal):
        self.signals.append(signal)

    def get_profit_loss_percentage(self):
        account_info = mt5.account_info()
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is not None and account_info is not None:
            balance = account_info.balance
            total_profit = 0
            for position in positions:
                ticket = position.ticket
                total_profit = position.profit + total_profit
            profit_loss_percentage = (total_profit / balance) * 100
            return profit_loss_percentage
        return 0

    def get_time_delay(self):
        return self.time_delay

    def on_signal(self):
        pass

    def on_manage_risk(self):
        pass

    def subscribe_to_tick(self):
        return mt5.symbol_select(self.symbol, True)

    def get_symbol_info(self):
        return mt5.symbol_info(self.symbol)

    def check_ticks(self):
        if len(self.signals) < 0:
            return
        symbol_info = self.get_symbol_info()
        self.on_manage_risk()
        if symbol_info is not None:
            current_ask_ = symbol_info.ask
            current_bid_ = symbol_info.bid

            if current_bid_ != self.previous_bid or current_ask_ != self.previous_ask:
                self.previous_bid = current_bid_
                self.previous_ask = current_ask_
                self.on_tick()

    def on_tick(self):
        delta = datetime.now() - self.signal_start_time
        if delta > timedelta(seconds=self.get_time_delay()):
            signal_data = self.on_signal()
            self.signal_start_time = datetime.now()

    def close_all_orders(self):
        positions = mt5.positions_get(symbol=self.symbol)
        total_profit_loss = 0
        if positions is not None and len(positions) > 0:
            print('closing positions')
            for position in positions:
                total_profit_loss = total_profit_loss + position.profit
                ticket = position.ticket
                mt5.Close(self.symbol, ticket=ticket)
        if total_profit_loss != 0:
            send_message('close {} -> {} USD'.format(self.symbol, round(total_profit_loss, 2)))

    def close_orders(self, positions: List[mt5.TradePosition], comment=None):
        total_profit_loss = 0
        if positions is not None and len(positions) > 0:
            print('closing positions')
            for position in positions:
                total_profit_loss = total_profit_loss + position.profit
                ticket = position.ticket
                mt5.Close(self.symbol, ticket=ticket, comment='{}:{}'.format(position.comment, comment))
        if total_profit_loss != 0:
            send_message('close {} -> {} USD'.format(self.symbol, round(total_profit_loss, 2)))

    def execute_market_order(self, volume: float, direction: TradeDirection, comment: str, sl: float = None):
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            print("not found, can not call order_check()")
            disconnect_mt5()

        if not symbol_info.visible:
            print(self.symbol, "is not visible, trying to switch on")
            if not self.subscribe_to_tick():
                print("symbol_select({}) failed. exit".format(self.symbol))
                disconnect_mt5()

        account_info = mt5.account_info()
        if account_info is None:
            print("failed to get account info")
            disconnect_mt5()

        order_type = mt5.ORDER_TYPE_BUY if direction == TradeDirection.BUY else mt5.ORDER_TYPE_SELL

        symbol_info = self.get_symbol_info()
        point = symbol_info.point
        price = symbol_info.ask if direction == TradeDirection.BUY else symbol_info.bid
        deviation = 20

        margin_required = mt5.order_calc_margin(mt5.TRADE_ACTION_DEAL, self.symbol, volume, price)
        if margin_required is None:
            print("Failed to calculate margin")
            disconnect_mt5()

        if account_info.margin_free < margin_required:
            print("Not enough free margin to execute the trade")
            return

        price = self.get_symbol_info().ask if direction == TradeDirection.BUY else self.get_symbol_info().ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": deviation,
            "magic": random.randint(10000, 90000),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC
        }

        if sl is not None:
            request['sl'] = sl

            if direction == TradeDirection.BUY:
                tp = price + 2 * (price - sl)
                request['tp'] = tp

            else:
                tp = price - 2 * (sl - price)
                request['tp'] = tp

        initialize_mt5()
        try:
            result = mt5.order_send(request)
            print(result)

            if result is None:
                print("order was not sent {}".format(request))

            elif request.get('retcode') != mt5.TRADE_RETCODE_DONE:
                pass
                # print("order was not sent {}".format(result))
            else:
                print("order was sent successfully")
                send_message('new order {} {}'.format(self.symbol, request))

        except Exception as e:
            print(e)
