from typing import List

import pandas as pd
import MetaTrader5 as mt5


class Signal:

    def __init__(self, exit_timeframe, entry_timeframe):
        self.buy_comment = ''
        self.sell_comment = ''
        self._exit_timeframe = exit_timeframe
        self._entry_timeframe = entry_timeframe

    def set_exit_timeframe(self, timeframe):
        self._exit_timeframe = timeframe

    def get_exit_timeframe(self):
        return self._exit_timeframe

    def set_entry_timeframe(self, timeframe):
        self._entry_timeframe = timeframe

    def get_entry_timeframe(self):
        return self._entry_timeframe

    def check_buy(self, data: pd.DataFrame):
        pass

    def check_sell(self, data: pd.DataFrame):
        pass

    def check_close_sell(self, positions: List[mt5.TradePosition], data: pd.DataFrame):
        account_info = mt5.account_info()

        if positions is not None and account_info is not None:
            balance = account_info.balance
            total_profit = 0
            profit_loss_percentage = 0
            # Loop through each position
            tobe_closed = []
            for position in positions:
                if position.comment == self.sell_comment:
                    ticket = position.ticket
                    total_profit = position.profit + total_profit
                    profit_loss_percentage = (total_profit / balance) * 100
                    tobe_closed.append(position)

            if len(positions) >= 2:
                if profit_loss_percentage >= 1 or profit_loss_percentage <= -10.0:
                    return tobe_closed
            elif len(positions) < 2:
                if profit_loss_percentage >= .5 or profit_loss_percentage <= -10.0:
                    return tobe_closed
            return []

    def check_close_buy(self, positions: List[mt5.TradePosition], data: pd.DataFrame):
        account_info = mt5.account_info()

        if positions is not None and account_info is not None:
            balance = account_info.balance
            total_profit = 0
            profit_loss_percentage = 0
            # Loop through each position
            tobe_closed = []
            for position in positions:
                if position.comment == self.buy_comment:
                    ticket = position.ticket
                    total_profit = position.profit + total_profit
                    profit_loss_percentage = (total_profit / balance) * 100
                    tobe_closed.append(position)

            if len(positions) >= 2:
                if profit_loss_percentage >= 1 or profit_loss_percentage <= -2.0:
                    return tobe_closed
            elif len(positions) < 2:
                if profit_loss_percentage >= .5 or profit_loss_percentage <= -2.0:
                    return tobe_closed
            return []

    def check_profit_take(self, data: pd.DataFrame):
        pass

    def check_stop_loss(self, data: pd.DataFrame):
        pass

    def get_stops(self, data: pd.DataFrame):
        pass
