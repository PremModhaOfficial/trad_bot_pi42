import hashlib
import hmac
import json
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from icecream import ic
from scipy.stats import kurtosis, skew


def generate_signature(api_secret, data_to_sign):
    # ic(data_to_sign)
    return hmac.new(
        api_secret.encode("utf-8"),
        data_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class TradingBot:
    def __init__(self, restrict_sell=False):
        load_dotenv()
        self.base_url = "https://fapi.pi42.com"
        self.api_key = os.getenv("PI42_API_KEY")
        self.secret_key = os.getenv("PI42_API_SECRET")
        self.available_balance = self.get_user_balance()
        self.restrict_sell = restrict_sell
        self.initial_balance = 10_00_000  # Example initial balance in INR
        self.balance = self.initial_balance
        self.position = 0
        self.entry_price = 0
        self.historical_data = pd.DataFrame(columns=["close"])

    def get_user_balance(self):
        if True:
            return 206
        timestamp = str(int(time.time() * 1000))
        params = {"marginAsset": "INR", "timestamp": timestamp}
        data_to_sign = json.dumps(params, separators=(",", ":"))
        signature = generate_signature(self.secret_key, data_to_sign)
        headers = {
            "api-key": self.api_key,
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

    def place_order(self, symbol, close_price=None, is_buing=True):
        # Generate the current timestamp in milliseconds
        timestamp = str(int(time.time() * 1000))

        # Define the order parameters
        params = {
            "timestamp": timestamp,  # Current timestamp in milliseconds
            "placeType": "ORDER_FORM",  # Type of order placement, e.g., 'ORDER_FORM'
            "quantity": 0.005,  # Quantity of the asset to trade
            "side": "BUY",  # Order side, either 'BUY' or 'SELL'
            "symbol": f"{symbol}",  # Trading pair, e.g., Bitcoin to USDT
            "type": "MARKET",  # Order type, either 'MARKET' or 'LIMIT'
            "reduceOnly": False,  # Whether to reduce an existing position only
            "marginAsset": "INR",  # The asset used as margin (INR in this case)
            "deviceType": "WEB",  # Device type (e.g., WEB, MOBILE)
            "userCategory": "EXTERNAL",  # User category (e.g., EXTERNAL, INTERNAL)
            # "price": 500,  # Price for the limit order (included here but irrelevant for market orders)
        }

        # Convert the parameters to a JSON string to sign
        data_to_sign = json.dumps(params, separators=(",", ":"))
        print(f"{data_to_sign=}")

        # Generate the signature for authentication
        signature = generate_signature(self.secret_key, data_to_sign)

        # Define the headers including the API key and the signature
        headers = {
            "api-key": self.api_key,
            "signature": signature,
            "Content-Type": "application/json",
        }

        try:
            # Send the POST request to place the order
            response = requests.post(
                f"{self.base_url}/v1/order/place-order", json=params, headers=headers
            )

            # Raise an HTTPError if the response status is 4xx or 5xx
            response.raise_for_status()

            # Parse the JSON response data
            response_data = response.json()

            # Print the success message with the order details
            res = json.dumps(response_data, indent=4)
            print(f"Order placed successfully: {res}")
            return response_data

        except requests.exceptions.HTTPError as err:
            # Handle HTTP errors specifically
            print(f"Error: {err.response.text if err.response else err}")
            return False

        except Exception as e:
            # Handle any other unexpected errors
            print(f"An unexpected error occurred: {str(e)}")
            return False

    def fetch_real_time_data(self):
        base_url = "https://api.pi42.com"
        symbol = "ETHINR"
        interval = "1m"  # Real-time data interval

        while True:
            try:
                response = requests.post(
                    f"{base_url}/v1/market/klines",
                    json={
                        "pair": symbol,
                        "interval": interval,
                        "limit": 1 if len(self.historical_data) >= 24 else 24,
                    },
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
                last_data = data[-1]
                if len(self.historical_data) < 24:
                    data = pd.DataFrame(data)
                    data.drop(
                        ["open", "startTime", "high", "low", "volume"],
                        inplace=True,
                        axis=1,
                    )
                    for i in range(len(data)):
                        yield {
                            "close": float(data.iloc[i]["close"]),
                            "date": pd.to_datetime(
                                int(last_data["endTime"]), unit="ms"
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                        }
                else:
                    yield {
                        "close": float(last_data["close"]),
                        "date": pd.to_datetime(
                            int(last_data["endTime"]), unit="ms"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
            except requests.exceptions.HTTPError as err:
                print(f"HTTP Error: {err}")
                print(f"Failed {response.status_code}: {response.text}")
            # except Exception as e:
            #     print(f"Unexpected Error: {e}")
            finally:
                time.sleep(60)  # Wait for the next interval

    def calculate_metrics(self, close):
        rolling_window = 24
        new_row = pd.DataFrame({"close": close}, index=[0])
        self.historical_data = pd.concat(
            [self.historical_data, new_row], ignore_index=True
        )

        if len(self.historical_data) < rolling_window:
            print(
                f"lenght is {len(self.historical_data)} {rolling_window - len(self.historical_data)}"
            )
            return None  # Not enough data to calculate rolling statistics

        self.historical_data["close"] = pd.to_numeric(self.historical_data["close"])
        mean = (
            self.historical_data["close"]
            .rolling(window=rolling_window, min_periods=1)
            .mean()
            .iloc[-1]
        )
        std = (
            self.historical_data["close"]
            .rolling(window=rolling_window, min_periods=1)
            .std()
            .iloc[-1]
        )

        self.historical_data["returns"] = self.historical_data["close"].pct_change()
        self.historical_data["zscore"] = (self.historical_data["close"] - mean) / std
        self.historical_data["skewness"] = (
            self.historical_data["returns"]
            .rolling(window=20)
            .apply(lambda x: skew(x), raw=False)
            .iloc[-1]
        )
        self.historical_data["kurtosis"] = (
            self.historical_data["returns"]
            .rolling(window=20)
            .apply(lambda x: kurtosis(x), raw=False)
            .iloc[-1]
        )

        return {
            "mean": mean,
            "std": std,
            "zscore": self.historical_data["zscore"].iloc[-1],
            "skewness": self.historical_data["skewness"].iloc[-1],
            "kurtosis": self.historical_data["kurtosis"].iloc[-1],
        }

    def close_all(self):
        endpoint = "/v1/positions/close-all-positions"

        # Generate the current timestamp
        timestamp = str(int(time.time() * 1000))

        # Prepare the request payload
        params = {"timestamp": timestamp}

        # Convert the request body to a JSON string for signing
        data_to_sign = json.dumps(params, separators=(",", ":"))

        # Generate the signature (ensure `generate_signature` is properly defined)
        signature = generate_signature(self.secret_key, data_to_sign)

        # Headers for the DELETE request
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "signature": signature,
        }

        # Construct the full URL
        cancel_orders_url = f"{self.base_url}{endpoint}"

        try:
            # Send the DELETE request to cancel all orders
            response = requests.delete(cancel_orders_url, json=params, headers=headers)
            response.raise_for_status()  # Raises an error for 4xx/5xx responses
            response_data = response.json()
            print(
                "All orders canceled successfully:", json.dumps(response_data, indent=4)
            )
            return response_data
        except requests.exceptions.HTTPError as err:
            ic(err)
            print(f"Failed {response.status_code}: {response.text}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return False

    def mean_reversion_strategy(self, close, metrics, date, risk):
        sign = "hold"
        if close < metrics["mean"] - metrics["std"]:
            sign = "buy"
        elif close > metrics["mean"] + metrics["std"] and risk is not None:
            sign = "sell"
        else:
            sign = "buy"

        with open("trading_signals.csv", "a+") as f:
            f.seek(0)
            if f.read(1) == "":
                f.write(
                    f"{'date'},{'close'},{'mean'},{'stdDev'},{'zscore'},{'skewness'},{'kurtosis'},{'signal'}\n"
                )
            f.write(
                f"{date},{close},{metrics['mean']},{metrics['std']},{metrics['zscore']},{metrics['skewness']},{metrics['kurtosis']},{sign}\n"
            )

        with open("trading_signals_readable.csv", "a+") as f:
            f.seek(0)
            if f.read(1) == "":
                f.write(
                    f"{'Date'},{'Close':<13},{'Mean':<13},{'Std Dev':<13},{'Z-Score':<13},{'Skewness':<13},{'Kurtosis':<13},{'Signal'}\n"
                )
            f.write(
                f"{date:<13},{close:<13.4f},{metrics['mean']:<13.4f},{metrics['std']:<13.4f},{metrics['zscore']:<13.4f},{metrics['skewness']:<13.4f},{metrics['kurtosis']:<13.4f},{sign:}\n"
            )

        return sign

    def execute_trade(self, signal, close, risk):
        if signal == "buy":
            if self.balance - risk < 0:
                return
            self.position += risk / close
            self.entry_price = close
            self.balance -= risk

            did_place = self.place_order("ETHINR")
            if did_place:
                with open("./logs.csv", "a") as report:
                    report.write(json.dumps(did_place, separators=(",", ":")))

        elif signal == "sell" and self.position > 0:
            self.balance += self.position * close
            self.position = 0
            did_close = self.close_all()
            if did_close:
                with open("./logs.csv", "a") as f:
                    try:
                        f.write(json.dumps(did_close, separators=(",", ":")))
                    except Exception as E:
                        ic(E)

    def run(self):
        for data in self.fetch_real_time_data():
            if data is None:
                continue
            close = data["close"]
            date = data["date"]

            metrics = self.calculate_metrics(close)
            if metrics is None:
                continue

            signal = self.mean_reversion_strategy(close, metrics, date, risk=30)
            self.execute_trade(signal, close, risk=30)

            final_balance = self.balance + self.position * close
            profit_loss = final_balance - self.initial_balance
            print(
                f"Current Balance: {float(self.balance)} INR.\n"
                f"Position: {float(self.position)}\n"
                f"Total Profit/Loss: {profit_loss} INR.\n"
                f"Meaning {profit_loss/self.initial_balance*100:.4f}%\n"
                # f"alpha={profit_loss / (close - self.entry_price) * 100 if self.entry_price != 0 else 0}%\n"
                f"{signal=}"
            )

            # plotter.plot("./trading_signals.csv")


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
