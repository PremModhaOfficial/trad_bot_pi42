import hashlib
import hmac
import json
import os
import time
from os import getenv

import pandas as pd
import requests
import scipy.stats as stats
from dotenv import load_dotenv

import plotter
from enums import OrderParams


def generate_signature(api_secret, data_to_sign):
    return hmac.new(
        api_secret.encode("utf-8"), data_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()


class TradBot:

    def __init__(self, restrict_sell=False):
        load_dotenv()
        self.base_url = "https://fapi.pi42.com"
        self.api_key = getenv("PI42_API_KEY")
        self.secret_key = getenv("PI42_API_SECRET")
        self.available_balance = self.get_user_balance()
        self.restrict_sell = restrict_sell

    def get_user_balance(self):
        timestamp = str(int(time.time() * 1000))
        params = {"marginAsset": "INR", "timestamp": timestamp}
        signature = generate_signature(
            self.secret_key, json.dumps(params, separators=(",", ":"))
        )
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "signature": signature,
        }

        # Fetch futures wallet balance
        futures_wallet_url = f"{self.base_url}/v1/wallet/futures-wallet/details"
        try:
            response = requests.get(futures_wallet_url, headers=headers, params=params)
            response.raise_for_status()
            futures_balance = response.json()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(f"Failed {response.status_code}: {response.text}")
            return None

        # Fetch funding wallet balance
        funding_wallet_url = f"{self.base_url}/v1/wallet/funding-wallet/details"
        try:
            response = requests.get(funding_wallet_url, headers=headers, params=params)
            response.raise_for_status()
            funding_balance = response.json()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(f"Failed {response.status_code}: {response.text}")
            return None

        # Combine and return the balances
        user_balance = {"futures": futures_balance, "funding": funding_balance}
        return user_balance

    def place_order(self, order_params: OrderParams):
        pass


# bot = TradBot()
# print(bot.available_balance)


# Set API credentials and parameters
base_url = "https://api.pi42.com"
symbol = "BTCINR"
default_interval = "1h"


# Define mean reversion strategy
def mean_reversion_strategy(close, mean, std, zscore, skewness, kurtosis, date, risk):
    sign = "hold"
    if close < mean - std:
        sign = "buy"
    elif close > mean + std and risk is None:
        sign = "sell"
    else:
        sign = "hold"

    with open("trading_signals.csv", "a+") as f:
        f.seek(0)
        if f.read(1) == "":
            f.write(
                f"{'date'},{'close'},{'mean'},{'stdDev'},{'zscore'},{'skewness'},{'kurtosis'},{'signal'}\n"
            )
        f.write(f"{date},{close},{mean},{std},{zscore},{skewness},{kurtosis},{sign}\n")
    with open("trading_signals_readable.csv", "a+") as f:
        f.seek(0)
        if f.read(1) == "":
            f.write(
                f"{"Date"},{'Close':<13},{'Mean':<13},{'Std Dev':<13},{'Z-Score':<13},{'Skewness':<13},{'Kurtosis':<13},{'Signal'}\n"
            )
        f.write(
            f"{date:<13},{close:<13.4f},{mean:<13.4f},{std:<13.4f},{zscore:<13.4f},{skewness:<13.4f},{kurtosis:<13.4f},{sign:}\n"
        )

    return sign


def run_strat(interval=default_interval, risk=None):
    # Fetch historical data
    response = requests.post(
        f"{base_url}/v1/market/klines",
        json={
            "pair": symbol,
            "interval": interval,
            "limit": 6000,
            # "start_time": 1643723400000,  # January 1, 2022, 00:00:00 UTC,
            # "end_time": 1675259400000,  # January 1, 2023, 00:00:00 UTC
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
    df["close"] = pd.to_numeric(df["close"])
    mean = df["close"].rolling(window=24, min_periods=1).mean()
    std = df["close"].rolling(window=24, min_periods=1).std()

    # print(f" ###########\n\n\n {df.head()=} ###########\n\n\n ")

    # Calculate additional metrics
    df["returns"] = df["close"].pct_change()
    df["zscore"] = (df["close"] - mean) / std
    df["skewness"] = (
        df["returns"].rolling(window=20).apply(lambda x: stats.skew(x), raw=False)
    )
    df["kurtosis"] = (
        df["returns"].rolling(window=20).apply(lambda x: stats.kurtosis(x), raw=False)
    )

    initial_balance = 10_00_000  # Example initial balance in INR
    balance = initial_balance
    initial_price = df["close"].iloc[0]
    position = 0
    entry_price = 0

    for i in range(len(df)):
        close = df["close"].iloc[i]
        zscore = df["zscore"].iloc[i]
        skewness = df["skewness"].iloc[i]
        kurtosis = df["kurtosis"].iloc[i]
        date = pd.to_datetime(df["endTime"].iloc[i], unit="ms").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        signal = mean_reversion_strategy(
            close, mean.iloc[i], std.iloc[i], zscore, skewness, kurtosis, date, risk
        )
        if signal == "buy":
            if risk is not None:
                print(f"{position=}")
                if balance - risk < 0:
                    break
                position += float(risk / close)
            elif risk is None:
                position = float(balance / close)

            entry_price = close
            balance = (0) if risk is None else (balance - risk)
            # print("Buy signal")
        elif signal == "sell" and position > 0:
            balance = position * close
            position = 0
            # print("Sell signal")

    # Calculate final profit/loss
    final_balance = balance + position * df["close"].iloc[-1]
    profit_loss = final_balance - initial_balance
    print(
        f"""
    Total Profit/Loss: {profit_loss} INR.
    Meaning {profit_loss/initial_balance*100:.4f}%
    alpha={profit_loss / (df["close"].iloc[-1] - initial_price) * 100}%
    balance={float(balance)}
    {float(position)=}
        """
    )


def delete_file(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


delete_file("trading_signals.csv")
run_strat("1h", risk=500)
plotter.plot("./trading_signals.csv")
