
# TradBot Documentation

## Overview
This code is for a trading bot named `TradBot` that implements a mean reversion strategy using historical price data. The bot uses the PI42 API for fetching user balance and historical market data, and it logs trading signals to CSV files. The `plotter` module is used to visualize the trading signals and market data.

## Modules and Files
1. **main.py**:
    - Contains the `TradBot` class implementation.
    - Contains functions to generate API signatures, run the mean reversion strategy, and plot trading signals.
2. **.envrc**:
    - Script to activate a virtual environment.
3. **plotter.py**:
    - Contains functions to plot trading signals and market data using matplotlib.

## Classes and Functions

### main.py

1. **generate_signature**:
    - Generates HMAC SHA256 signature for API requests.
    - **Arguments**:
        - `api_secret` (str): Secret API key.
        - `data_to_sign` (str): Data to be signed.

2. **TradBot**:
    - Trading bot class that interacts with the PI42 API to fetch user balance and place orders.
    - **Attributes**:
        - `base_url` (str): API base URL.
        - `api_key` (str): API key.
        - `secret_key` (str): Secret API key.
        - `available_balance` (dict): User's balance in futures and funding wallets.
        - `restrict_sell` (bool): Flag to restrict selling.
    - **Methods**:
        - `__init__(self, restrict_sell=False)`:
            - Initializes the bot and loads API credentials.
        - `get_user_balance(self)`:
            - Fetches and returns the user's balance in futures and funding wallets.
        - `place_order(self, order_params: OrderParams)`:
            - Placeholder method to place an order (not implemented).

3. **mean_reversion_strategy**:
    - Implements the mean reversion trading strategy to determine buy/sell/hold signals.
    - **Arguments**:
        - `close` (float): Current closing price.
        - `mean` (float): Mean of closing prices over the last 24 periods.
        - `std` (float): Standard deviation of closing prices over the last 24 periods.
        - `zscore` (float): Z-score of the current closing price.
        - `skewness` (float): Skewness of the closing prices over the last 24 periods.
        - `kurtosis` (float): Kurtosis of the closing prices over the last 24 periods.
        - `date` (str): Date of the current closing price.
        - `risk` (float): Risk amount for the trade.
    - **Returns**:
        - `sign` (str): Trading signal ("buy", "sell", or "hold").

4. **run_strat**:
    - Runs the mean reversion strategy for a given interval and risk level.
    - **Arguments**:
        - `interval` (str): Data interval for historical market data.
        - `risk` (float): Risk amount for trades.
    - **Process**:
        - Fetches historical market data from PI42 API.
        - Calculates mean, standard deviation, Z-score, skewness, and kurtosis.
        - Applies mean reversion strategy to generate trading signals.
        - Logs trading signals to CSV files.
        - Calculates and prints total profit/loss.
    - **Returns**:
        - None

5. **delete_file**:
    - Deletes a specified file.
    - **Arguments**:
        - `filename` (str): Path to the file to be deleted.
    - **Process**:
        - Attempts to remove the specified file.
        - Suppresses FileNotFoundError if the file doesn't exist.
    - **Returns**:
        - None

### plotter.py

1. **plot**:
    - Plots trading signals and market data using matplotlib.
    - **Arguments**:
        - `csv_path` (str): Path to the CSV file containing trading signals.
    - **Process**:
        - Reads trading signals from the specified CSV file.
        - Processes and cleans the data.
        - Plots close prices, scaled kurtosis, skewness, and z-score.
        - Marks buy and sell signals on the plot.
        - Displays the plot.
    - **Returns**:
        - None
