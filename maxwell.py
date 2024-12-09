from os import pread

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import scipy.stats as stats


class MaxwellCurveTradingStrategy:
    def __init__(self, initial_balance=1_000_000, risk_per_trade=1):
        """
        Initialize Maxwell Curve Trading Strategy

        Parameters:
        - initial_balance: Starting capital
        - risk_per_trade: Percentage of capital to risk per trade (default 2%)
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.position = 0
        self.entry_price = 0

    def calculate_maxwell_curve(self, prices, window=12):
        print(prices)
        """
        Calculate Maxwell curve components

        Parameters:
        - prices: Price series
        - window: Rolling window for calculations

        Returns:
        Dictionary with key statistical metrics
        """
        # Calculate key statistical measures
        returns = np.log(prices).diff()

        # Ensure price data is of type float
        prices = prices.astype(float)

        maxwell_metrics = {
            "mean": prices.rolling(
                window=window, min_periods=1
            ).mean(),  # Adjust min_periods
            "std_dev": prices.rolling(
                window=window, min_periods=1
            ).std(),  # Adjust min_periods
            "skewness": returns.rolling(window=window, min_periods=1).apply(
                lambda x: (
                    stats.skew(x, nan_policy="omit") if len(x.dropna()) >= 3 else np.nan
                ),
                raw=False,  # Added nan_policy
            ),
            "kurtosis": returns.rolling(window=window, min_periods=1).apply(
                lambda x: (
                    stats.kurtosis(x, nan_policy="omit")
                    if len(x.dropna()) >= 4
                    else np.nan
                ),
                raw=False,  # Added nan_policy
            ),
            "zscore": (prices - prices.rolling(window=window, min_periods=1).mean())
            / prices.rolling(window=window, min_periods=1).std(),  # Adjust min_periods
        }

        print(f"\n{maxwell_metrics['mean']=}")
        maxwell_df = pd.DataFrame(maxwell_metrics).dropna()
        return maxwell_df

    def generate_trading_signal(self, metrics):
        """
        Generate trading signal based on Maxwell curve metrics

        Parameters:
        - metrics: Maxwell curve metrics dictionary
        - current_price: Current market price

        Returns:
        Trading signal (buy, sell, or hold)
        """
        # Extract latest metrics
        latest_zscore = (
            float(metrics["zscore"].iloc[-1])
            if type(metrics["zscore"]) is not int
            and type(metrics["zscore"]) is not np.float64
            and not np.isnan(metrics["zscore"].iloc[-1])
            else 0
        )
        latest_skewness = (
            float(metrics["skewness"].iloc[-1])
            if type(metrics["skewness"]) is not int
            and type(metrics["skewness"]) is not np.float64
            and not np.isnan(metrics["skewness"].iloc[-1])
            else 0
        )
        latest_kurtosis = (
            float(metrics["kurtosis"].iloc[-1])
            if type(metrics["kurtosis"]) is not int
            and type(metrics["kurtosis"]) is not np.float64
            and not np.isnan(metrics["kurtosis"].iloc[-1])
            else 0
        )

        # Define trading logic
        if latest_zscore < -2 and latest_skewness < 0 and latest_kurtosis > 3:
            print(
                f"Buy signal: zscore={latest_zscore}, skewness={latest_skewness}, kurtosis={latest_kurtosis}"
            )
            return "buy"
        elif latest_zscore > 2 and latest_skewness > 0 and latest_kurtosis > 3:
            print(
                f"Sell signal: zscore={latest_zscore}, skewness={latest_skewness}, kurtosis={latest_kurtosis}"
            )
            return "sell"
        else:
            # print(
            #     f"Hold signal: zscore={latest_zscore}, skewness={latest_skewness}, kurtosis={latest_kurtosis}"
            # )
            return "hold"

    def calculate_position_size(self, current_price):
        """
        Calculate optimal position size based on risk management

        Parameters:
        - current_price: Current market price

        Returns:
        Position size in asset units
        """
        risk_amount = self.risk_per_trade
        position_size = risk_amount / current_price
        return position_size

    def execute_trade(self, signal, current_price):
        """
        Execute trading logic

        Parameters:
        - signal: Trading signal
        - current_price: Current market price

        Returns:
        Updated balance and position
        """
        if signal == "buy" and self.position == 0 and not np.isnan(current_price):
            # Enter long position
            position_size = self.calculate_position_size(current_price)
            self.position = position_size
            self.entry_price = current_price
            self.current_balance -= position_size * current_price
            return "Entered long position"

        elif signal == "sell" and self.position > 0 and not np.isnan(current_price):
            # Exit long position
            exit_value = self.position * current_price
            profit_loss = exit_value - (self.position * self.entry_price)
            self.current_balance += exit_value

            # Reset position
            self.position = 0
            self.entry_price = 0

            return f"Exited position. Profit/Loss: {profit_loss}"

        return "No trade executed"

    def backtest(self, price_data):
        """
        Backtest the Maxwell Curve trading strategy

        Parameters:
        - price_data: Pandas Series of historical prices

        Returns:
        Backtest results and performance metrics
        """
        # Calculate Maxwell curve metrics
        metrics = self.calculate_maxwell_curve(price_data)

        # Track performance
        trade_log = []

        for i in range(len(price_data)):
            current_price = price_data.iloc[i]

            # Extract metrics for current point
            current_metrics = {
                key: (
                    metric.iloc[i].astype(float)
                    if metric.iloc[i] and not np.isnan(metric.iloc[i])
                    else 0
                )
                for key, metric in metrics.items()
            }
            # print(f"Current metrics at index {i}: {current_metrics}")

            # Generate signal
            signal = self.generate_trading_signal(current_metrics)

            # Execute trade
            trade_result = self.execute_trade(signal, current_price)

            trade_log.append(
                {
                    "date": price_data.index[i],
                    "price": current_price,
                    "signal": signal,
                    "trade_result": trade_result,
                    "balance": self.current_balance,
                }
            )

        # Calculate final performance
        total_return = (
            (self.current_balance - self.initial_balance) / self.initial_balance * 100
        )

        return {
            "trade_log": pd.DataFrame(trade_log),
            "final_balance": self.current_balance,
            "total_return_percentage": total_return,
        }


def current_price(symbol, interval) -> pd.Series:

    response = requests.post(
        "https://api.pi42.com/v1/market/klines",
        json={
            "pair": symbol,
            "interval": interval,
            "limit": 1000,
            # "startTime": int(time.time()) - (86400 * days_back),
            # "endTime": int(time.time()) - (86400 * (days_back - 1)),
        },
        headers={"Content-Type": "application/json"},
    )
    # print(f"{json.dumps(response.json(), indent=4)}")
    # print(f"{len(response.json())}")
    print(f"\n\n{response.status_code=}\n{len(response.json())=}\n\n")
    response.raise_for_status()
    data = response.json()

    # Calculate mean and standard deviation
    df = pd.DataFrame(data)
    close_prices = df["close"].astype(float)
    # close_prices.index = pd.to_datetime(df["timestamp"], unit="s")
    return close_prices


# Example usage
def main():
    prices = current_price("BTCINR", "1h")
    if prices is None or prices.empty:
        print("No price data available.")
        return

    strategy = MaxwellCurveTradingStrategy()
    results = strategy.backtest(prices)

    print(f"Initial Balance: {strategy.initial_balance}")
    print(f"Final Balance: {results['final_balance']}")
    print(f"Total Return: {results['total_return_percentage']:.2f}%")

    # Optional: Visualize trade log
    plt.figure(figsize=(12, 6))
    plt.plot(prices.index, prices.values, label="Price")
    plt.title("Maxwell Curve Trading Strategy Backtest")
    plt.plot(
        results["trade_log"]["date"], results["trade_log"]["balance"], label="Balance"
    )
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
