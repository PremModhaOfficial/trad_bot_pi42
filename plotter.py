import matplotlib.pyplot as plt
import pandas as pd


def plot(csv_path: str):
    df = pd.read_csv(csv_path)

    df = df[24:]
    # print(f" ###########\n\n\n {df.head()=} ###########\n\n\n ")
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
    plt.figure(figsize=(14, 10))

    plt.plot(df["date"], df["close"], label="Close Price", color="blue")

    # Amplify the kurtosis
    kurtosis_scaled = df["kurtosis"] * 10
    plt.plot(
        df["date"],
        kurtosis_scaled,
        label="Kurtosis (scaled)",
        color="red",
        linestyle="--",
    )

    # Amplify the skewness
    skewness_scaled = df["skewness"] * 10
    plt.plot(
        df["date"],
        skewness_scaled,
        label="Skewness (scaled)",
        color="green",
        linestyle=":",
    )

    # Amplify the z-score
    zscore_scaled = df["zscore"] * 10
    plt.plot(
        df["date"],
        zscore_scaled,
        label="Z-Score (scaled)",
        color="orange",
        linestyle="-.",
    )

    # Plot the buy and sell signals
    buy_signals = df[df["signal"] == "buy"]
    sell_signals = df[df["signal"] == "sell"]
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

    # Add annotations to highlight the influence of metrics on signals
    # for i, signal in buy_signals.iterrows():
    #     plt.annotate(
    #         f"Kurtosis: {signal['kurtosis']:.2f}\nSkewness: {signal['skewness']:.2f}\nZ-Score: {signal['zscore']:.2f}",
    #         (signal["date"], signal["close"]),
    #         textcoords="offset points",
    #         xytext=(0, 10),
    #         ha="center",
    #     )

    # for i, signal in sell_signals.iterrows():
    #     plt.annotate(
    #         f"Kurtosis: {signal['kurtosis']:.2f}\nSkewness: {signal['skewness']:.2f}\nZ-Score: {signal['zscore']:.2f}",
    #         (signal["date"], signal["close"]),
    #         textcoords="offset points",
    #         xytext=(0, -10),
    #         ha="center",
    #     )

    plt.title("Close Price and Trading Signals with Metrics")
    plt.xlabel("Date")
    plt.ylabel("Metrics")
    plt.legend()
    plt.tight_layout()
    plt.show()
