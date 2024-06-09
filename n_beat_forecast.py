import pandas as pd
from darts import TimeSeries
from darts.models import NBEATSModel
from darts.models import NBEATSModel
from darts.datasets import WeatherDataset

import MetaTrader5 as mt5

if __name__ == '__main__':
    # Connect to MetaTrader 5
    mt5.initialize()

    # Define the symbol and timeframe
    symbol = "XAUUSD.ecn"
    timeframe = mt5.TIMEFRAME_M1

    # Get historical data from MetaTrader 5
    historical_data = mt5.copy_rates_from_pos(symbol, timeframe, 0, 80)
    # Extract close prices from the historical data
    data = pd.DataFrame(historical_data)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.set_index('time', inplace=True)
    # Generate a complete date range and reindex the DataFrame to it
    date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='1Min')
    data = data.reindex(date_range,
                        method='pad')  # Fill missing values by propagating the last valid observation forward
    series = TimeSeries.from_times_and_values(data.index, data['close'])
    # Load the saved model
    loaded_model = NBEATSModel.load("nbeats_model.pth")
    # Make predictions with the loaded model
    forecast = loaded_model.predict(n=3, series=series)
    # Print or return the forecast
    print(forecast)
