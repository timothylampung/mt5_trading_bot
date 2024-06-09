import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.models import NBEATSModel
import MetaTrader5 as mt5
from sklearn.metrics import mean_absolute_error, mean_squared_error

if __name__ == '__main__':
    # Connect to MetaTrader 5
    mt5.initialize()

    # Define the symbol and timeframe
    symbol = "XAUUSD.ecn"
    timeframe = mt5.TIMEFRAME_H1

    # Get historical data   from MetaTrader 5
    historical_data = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)
    print('historical data length {}'.format(len(historical_data)))

    # Extract close prices from the historical data
    data = pd.DataFrame(historical_data)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.set_index('time', inplace=True)

    # Generate a complete date range and reindex the DataFrame to it
    date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='1h')
    data = data.reindex(date_range,
                        method='pad')  # Fill missing values by propagating the last valid observation forward

    series = TimeSeries.from_times_and_values(data.index, data['close'])

    # Initialize NBEATSModel
    model = NBEATSModel(input_chunk_length=14, output_chunk_length=3, random_state=0, n_epochs=100)

    # Train the model
    train, val = series[:997], series[-3:]
    model.fit(train)  # Assuming 80% of data is for training, and last 10 points are for prediction
    model.save("nbeats_model.pth")

    # Make predictions
    forecast = model.predict(n=len(val), series=train)

    # Print or return the forecast
    print(forecast)

    # Convert forecast and actual values to numpy arrays
    forecast = np.array(forecast)
    val = np.array(val)

    # Calculate error metrics
    mae = mean_absolute_error(val, forecast)
    mse = mean_squared_error(val, forecast)
    rmse = np.sqrt(mse)

    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"Mean Squared Error (MSE): {mse}")
    print(f"Root Mean Squared Error (RMSE): {rmse}")

    # Disconnect from MetaTrader 5
    mt5.shutdown()
