import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.models import TCNModel
import MetaTrader5 as mt5
import talib
from sklearn.metrics import mean_absolute_error, mean_squared_error


def fetch_data(symbol, timeframe, n):
    """
    Fetch historical data for a given symbol and timeframe.

    Parameters:
        symbol (str): The symbol to fetch data for.
        timeframe (int): The timeframe (in MetaTrader 5 format) for the data.
        n (int): The number of bars to fetch.

    Returns:
        pd.DataFrame: A DataFrame containing the fetched historical data.
    """
    # Connect to MetaTrader 5
    mt5.initialize()

    # Get historical data from MetaTrader 5
    historical_data = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    mt5.shutdown()

    # Convert to DataFrame
    data = pd.DataFrame(historical_data)
    data['time'] = pd.to_datetime(data['time'], unit='s')

    # Generate a complete date range and reindex the DataFrame to it
    date_range = pd.date_range(start=data['time'].min(), end=data['time'].max(), freq='1h')
    data = data.set_index('time').reindex(date_range, method='pad')

    return data


if __name__ == '__main__':
    # Define the symbol and timeframe
    symbol = "XAUUSD.ecn"
    timeframe = mt5.TIMEFRAME_H1
    n = 1000  # Number of historical bars to fetch

    # Fetch historical data from MetaTrader 5
    data = fetch_data(symbol, timeframe, n)
    print('Fetched historical data:', data.head())

    # Convert closing prices to a TimeSeries
    closing_series = TimeSeries.from_series(data['close'])

    # Calculate RSI using talib
    rsi_values = talib.RSI(data['close'].values, timeperiod=14)

    # Convert RSI values to a TimeSeries
    rsi_series = TimeSeries.from_times_and_values(data.index, rsi_values)

    # Combine closing prices and RSI values into a single TimeSeries
    combined_series = closing_series.stack(rsi_series)

    # Train-test split
    train_size = int(len(combined_series) * 0.8)  # 80% train, 20% test
    train, val = combined_series.split_before(train_size)

    # Define and train the model
    model = TCNModel(input_chunk_length=50, output_chunk_length=1)
    model.fit(train, val_series=val, verbose=True)

    # Predict the next closing price based on the last observed RSI and closing price
    last_close = closing_series[-1]
    last_rsi = rsi_series[-1]

    last_point = last_close.stack(last_rsi)

    next_close = model.predict(n=1, series=last_point)

    print("Predicted next closing price:", next_close)
