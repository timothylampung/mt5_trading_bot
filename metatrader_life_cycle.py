from enum import Enum
import pandas as pd
import MetaTrader5 as mt5
import random


def initialize_mt5():
    if not mt5.initialize():
        print("failed to initialized mt5 {}".format(mt5.last_error()))
        disconnect_mt5()
        quit()


def disconnect_mt5():
    mt5.shutdown()


class TradeDirection(Enum):
    BUY = 0
    SELL = 0


initialize_mt5()


class MetatraderLifeCycle:
    def __init__(self, symbol: str, timeframe=mt5.TIMEFRAME_M15):
        self.symbol = symbol
        self.timeframe = timeframe
        self.previous_bid = self.get_symbol_info().bid
        self.previous_ask = self.get_symbol_info().ask
        self.PLOT_DATA = {
            'signal_data': {}
        }

    def on_signal(self):
        pass

    def on_manage_risk(self):
        pass

    def subscribe_to_tick(self):
        return mt5.symbol_select(self.symbol, True)

    def get_symbol_info(self):
        return mt5.symbol_info(self.symbol)

    def check_ticks(self):
        symbol_info = self.get_symbol_info()
        if symbol_info is not None:
            current_ask_ = symbol_info.ask
            current_bid_ = symbol_info.bid

            if current_bid_ != self.previous_bid or current_ask_ != self.previous_ask:
                self.previous_bid = current_bid_
                self.previous_ask = current_ask_
                self.on_manage_risk()
                print('new tick {} {}'.format(self.symbol, self.timeframe))
                return self.on_tick()

    def on_tick(self):
        bars = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 80)
        positions = mt5.positions_get(symbol=self.symbol)
        if bars is not None and len(bars) > 0:
            bars_frame = pd.DataFrame(bars)

            position_prices = None
            position_volumes = None

            if positions is not None and len(positions) > 0:
                position_prices = [position.price_open for position in positions]
                position_volumes = [position.volume for position in positions]
            if position_prices is not None:
                position_prices = [0 if price is None else price for price in position_prices]
                position_volumes = [0 if volume is None else volume for volume in position_volumes]

            bars_frame = bars_frame.iloc[:40]

            # calling on signal
            signal_data = self.on_signal()

            ask = self.get_symbol_info().ask
            bid = self.get_symbol_info().bid
            account_info = mt5.account_info()

            self.PLOT_DATA = {
                'sentiment': 'to be added soon',
                'positions': {
                    'time': bars_frame['time'].values.tolist(),
                    'prices': position_prices,
                    'sizes': position_volumes
                },
                'ohlc': {
                    'time': bars_frame['time'].values.tolist(),
                    'open': bars_frame['open'].values.tolist(),
                    'close': bars_frame['close'].values.tolist(),
                    'high': bars_frame['high'].values.tolist(),
                    'low': bars_frame['low'].values.tolist(),
                },
                'account': {
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'gain': ((account_info.equity - account_info.balance) / account_info.balance) * 100
                },
                'chart_info': {
                    'timeframe': self.timeframe,
                    'symbol': self.symbol,
                    'ask': ask,
                    'bid': bid
                },
                'signal_data': signal_data
            }

            return self.PLOT_DATA

    def close_all_orders(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is not None and len(positions) > 0:
            print('closing positions')
            for position in positions:
                ticket = position.ticket
                mt5.Close(self.symbol, ticket=ticket)

    def execute_market_order(self, volume: float, direction: TradeDirection, comment: str):
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

        price = self.get_symbol_info().previous_ask if direction == TradeDirection.BUY else self.get_symbol_info().previous_bid

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

        initialize_mt5()
        result = mt5.order_send(request)

        if result is None:
            print("order was not sent {}".format(request))

        if request.retcode != mt5.TRADE_RETCODE_DONE:
            print("order was not sent {}".format(request))
            result_dict = result.as_dict()
            for field in result_dict.keys():
                print("{}={}".format(field, result_dict[field]))
                if field == "request":
                    trade_request_dict = result_dict[field].as_dict()
                    for trade_request_field in trade_request_dict:
                        print(" Trade request: {}={}".format(trade_request_field,
                                                             trade_request_dict[trade_request_field]))
        else:
            print("order was sent successfully")
