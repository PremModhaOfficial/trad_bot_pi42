import csv
from datetime import datetime, timedelta

import requests


def fetch():

    # Set API URL
    url = "https://api.binance.com/api/v3/klines"

    # Define parameters
    params = {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "startTime": int(
            (datetime.now() - timedelta(days=3650)).timestamp() * 1000
        ),  # Last 10 years
        "endTime": int(datetime.now().timestamp() * 1000),
    }

    # Make API request
    response = requests.get(url, params=params)
    data = response.json()

    # Prepare data for CSV
    csv_data = []
    for kline in data:
        timestamp = datetime.fromtimestamp(int(kline[0]) / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        open_price = float(kline[1])
        high_price = float(kline[2])
        low_price = float(kline[3])
        close_price = float(kline[4])
        volume = float(kline[5])
        csv_data.append(
            [timestamp, open_price, high_price, low_price, close_price, volume]
        )

    # Write to CSV
    with open("btcusdt_1hr_klines.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Open", "High", "Low", "Close", "Volume"])
        writer.writerows(csv_data)
