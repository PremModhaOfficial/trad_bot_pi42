import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats


class MaxwellCurveTradingStrategy:
    def __init__(self, initial_balance=1_000_000, risk_per_trade=0.02):
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

    def calculate_maxwell_curve(self, prices, window=24):
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

        maxwell_metrics = {
            "mean": prices.rolling(window=window).mean(),
            "std_dev": prices.rolling(window=window).std(),
            "skewness": returns.rolling(window=window).apply(lambda x: stats.skew(x)),
            "kurtosis": returns.rolling(window=window).apply(
                lambda x: stats.kurtosis(x)
            ),
            "zscore": (prices - prices.rolling(window=window).mean())
            / prices.rolling(window=window).std(),
        }

        return maxwell_metrics

    def generate_trading_signal(self, metrics, current_price):
        """
        Generate trading signal based on Maxwell curve metrics

        Parameters:
        - metrics: Maxwell curve metrics dictionary
        - current_price: Current market price

        Returns:
        Trading signal (buy, sell, or hold)
        """
        # Extract latest metrics
        latest_zscore = metrics["zscore"]
        latest_skewness = metrics["skewness"]
        latest_kurtosis = metrics["kurtosis"]

        # Define trading logic
        if latest_zscore < -2 and latest_skewness < 0 and latest_kurtosis > 3:
            return "buy"
        elif latest_zscore > 2 and latest_skewness > 0 and latest_kurtosis > 3:
            return "sell"
        else:
            return "hold"

    def calculate_position_size(self, current_price):
        """
        Calculate optimal position size based on risk management

        Parameters:
        - current_price: Current market price

        Returns:
        Position size in asset units
        """
        risk_amount = self.current_balance * self.risk_per_trade
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
        if signal == "buy" and self.position == 0:
            # Enter long position
            position_size = self.calculate_position_size(current_price)
            self.position = position_size
            self.entry_price = current_price
            self.current_balance -= position_size * current_price
            return "Entered long position"

        elif signal == "sell" and self.position > 0:
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
            current_metrics = {key: metric.iloc[i] for key, metric in metrics.items()}

            # Generate signal
            signal = self.generate_trading_signal(current_metrics, current_price)

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


# Example usage
def main():
    # Simulated price data (replace with your actual data fetching method)
    dates = pd.date_range(start="2023-01-01", end="2024-01-01", freq="D")
    prices = pd.Series(np.random.normal(100, 10, len(dates)), index=dates)

    strategy = MaxwellCurveTradingStrategy()
    results = strategy.backtest(prices)

    print(f"Initial Balance: {strategy.initial_balance}")
    print(f"Final Balance: {results['final_balance']}")
    print(f"Total Return: {results['total_return_percentage']:.2f}%")

    # Optional: Visualize trade log
    plt.figure(figsize=(12, 6))
    plt.plot(prices.index, data=prices.values, label="Price")
    plt.title("Maxwell Curve Trading Strategy Backtest")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
