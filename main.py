import hashlib
import hmac
import json
import time
from os import getenv

import pandas as pd
import requests
from dotenv import load_dotenv

from enums import OrderParams


def generate_signature(api_secret, data_to_sign):
    return hmac.new(
        api_secret.encode("utf-8"), data_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()


class TradBot:

    def __init__(self):
        load_dotenv()
        self.base_url = "https://fapi.pi42.com"
        self.api_key = getenv("PI42_API_KEY")
        self.secret_key = getenv("PI42_API_SECRET")
        self.available_balance = self.get_user_balance()

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
        """
        quantity 	number 	No 	The amount of the asset to be ordered. Specify the desired quantity.
        price 	number 	Conditional 	The price at which to place the LIMIT/STOP_LIMIT order. Must be specified if orderType is "LIMIT" or "STOP_LIMIT".
        placeType 	string 	Yes 	Fixed value "ORDER_FORM". Indicates the type of order placement.
        side 	string 	Yes 	The side of the order, which is "BUY" in this case.
        symbol 	string 	Yes 	The trading pair symbol, for example, "GRTINR".
        reduceOnly 	boolean 	No 	Indicates whether the order should only reduce the position. Default is false.
        marginAsset 	string 	Yes 	The asset used for margin, such as "INR".
        orderType 	string 	Yes 	The type of the order. It can be MARKET, LIMIT, STOP_MARKET or STOP_LIMIT.
        takeProfitPrice 	number 	No 	Price at which take profit order should be executed.
        stopLossPrice 	number 	No 	Price at which stop loss order should be executed.
        stopPrice 	number 	No 	Compulsory for STOP_MARKET and STOP_LIMIT orders
        """
        pass


# bot = TradBot()
# print(bot.available_balance)


# Set API credentials and parameters
base_url = "https://api.pi42.com"
symbol = "BTCINR"
default_interval = "1h"


def main(interval=default_interval):
    # Fetch historical data
    response = requests.post(
        f"{base_url}/v1/market/klines",
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
    df["close"] = pd.to_numeric(df["close"])
    mean = df["close"].rolling(window=24).mean()
    std = df["close"].rolling(window=24).std()

    # Define mean reversion strategy
    def mean_reversion_strategy(close, mean, std):
        sign = "hold"
        if close < mean - std:
            sign = "buy"
        elif close > mean + std:
            sign = "sell"
        else:
            sign = "hold"

        with open("trading_signals.csv", "a+") as f:
            f.seek(0)
            if f.read(1) == "":
                f.write(f"{'Close'},{'Mean'},{'Std Dev'},{'Signal'}\n")
            f.write(f"{close},{mean},{std},{sign}\n")
        with open("trading_signals_readable.csv", "a+") as f:
            f.seek(0)
            if f.read(1) == "":
                f.write(f"{'Close':<13},{'Mean':<13},{'Std Dev':<13},{'Signal'}\n")
            f.write(f"{close:<13.4f},{mean:<13.4f},{std:<13.4f},{sign:}\n")

        return sign

    initial_balance = 10_00_000  # Example initial balance in INR
    balance = initial_balance
    position = 0
    entry_price = 0

    for i in range(len(df)):
        close = df["close"].iloc[i]
        signal = mean_reversion_strategy(close, mean.iloc[i], std.iloc[i])
        if signal == "buy" and position == 0:
            position = balance / close
            entry_price = close
            balance = 0
            # print("Buy signal")
        elif signal == "sell" and position > 0:
            balance = position * close
            position = 0
            # print("Sell signal")

    # Calculate final profit/loss
    final_balance = balance if position == 0 else position * df["close"].iloc[-1]
    profit_loss = final_balance - initial_balance
    print(
        f"""
    Total Profit/Loss: {profit_loss} INR.
    Meaning {profit_loss/initial_balance*100:.4f}%
            balance={float(balance)}
            {position=}
        """
    )


if __name__ == "__main__":
    main("1h")
