import matplotlib.pyplot as plt
import pandas as pd


def plot(csv_path: str):
    df = pd.read_csv(csv_path)

    df = df[24:]
    print(f" ###########\n\n\n {df.head()=} ###########\n\n\n ")
    # Convert date column to datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    # Handle missing values

    # Ensure data types are correct
    df["close"] = df["close"].astype(float)
    df["zscore"] = df["zscore"].astype(float)
    df["skewness"] = df["skewness"].astype(float)
    df["kurtosis"] = df["kurtosis"].astype(float)

    # Optionally, filter out any outliers or erroneous data points
    df = df[(df["close"] > 0) & (df["close"] < df["close"].quantile(0.99))]

    # Plot the data
    buy_signals = df[df["signal"] == "buy"]
    sell_signals = df[df["signal"] == "sell"]
    plt.figure(figsize=(14, 10))

    plt.plot(df["date"], df["close"], label="Close Price", color="blue")
    plt.plot(df["date"], df["zscore"], label="Z-Score", color="orange")
    plt.plot(df["date"], df["skewness"], label="Skewness", color="green")
    plt.plot(df["date"], df["kurtosis"], label="Kurtosis", color="red")
    plt.scatter(
        buy_signals["date"],
        buy_signals["close"],
        marker="^",
        color="green",
        label="Buy Signal",
        alpha=1,
    )
    plt.scatter(
        sell_signals["date"],
        sell_signals["close"],
        marker="v",
        color="red",
        label="Sell Signal",
        alpha=1,
    )
    plt.title("Trading Strategy Metrics and Signals")
    plt.xlabel("Date")
    plt.ylabel("Metrics")
    plt.legend()
    plt.tight_layout()
    plt.show()
