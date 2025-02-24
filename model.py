import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import requests
import eventlet
import time
import socketio as io
import websocket
import json
import threading
import asyncio
import websockets
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from flask import Flask, request, jsonify
# from binance.client import Client
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

"""## **Gathering Data**"""

data_ticker = yf.Ticker("BTC-USD")
data = data_ticker.history(period="max")

"""## **Preparing Data**"""

def calculate_rsi(data, window=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def prepare_data(data):
    data.index = pd.to_datetime(data.index)
    data.index = data.index.tz_convert(None)

    del data["Dividends"]
    del data["Stock Splits"]

    data["SMA50"] = data["Close"].rolling(window=50).mean()
    data["SMA100"] = data["Close"].rolling(window=100).mean()
    data["SMA200"] = data["Close"].rolling(window=200).mean()
    data['Volatility'] = data['Close'].pct_change().rolling(window=30).std()

    data["Future_Close"] = data["Close"].shift(-7)

    data["MACD"] = data["Close"].ewm(span=12, adjust=False).mean() - data["Close"].ewm(span=26, adjust=False).mean()
    data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

    data["RSI"] = calculate_rsi(data)

    data.dropna(inplace=True)

    return data

data = prepare_data(data)

features = ['SMA50', 'SMA100', 'SMA200', 'Volatility', 'MACD', 'Signal', 'RSI']
target = 'Future_Close'

scaler = MinMaxScaler()
data[features] = scaler.fit_transform(data[features])

X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2)

model = RandomForestRegressor()
model.fit(X_train, y_train)
joblib.dump(model, "models/model.pkl")
prediction = model.predict(X_test)

mse = np.sqrt(mean_squared_error(y_test, prediction))
print("MSE:", mse)

future_features = data[features].iloc[-7:]
future_predictions = model.predict(future_features)
print("Predicted Prices for Next 7 Days:", future_predictions)

r2 = r2_score(y_test, prediction)
print("R² Score:", r2)

"""## **Using XGBoost**"""

model = XGBRegressor(n_estimators=200, learning_rate=0.05)
model.fit(X_train, y_train)
prediction = model.predict(X_test)

mse = np.sqrt(mean_squared_error(y_test, prediction))
print("XGBoost MSE:", mse)

"""## **DCA Strategy**"""

investment_amount = 100
investment_threshold = np.percentile(future_predictions, 30)

def dca_strategy(prediction, threshold, investment_amount=100, max_multiplier=2.5, min_multiplier=0.5, volatility_factor=0.2):
    investment_schedule = []
    
    price_volatility = np.std(prediction) / np.mean(prediction)

    for price in prediction:
        deviation = (threshold - price) / threshold

        if price < threshold:
            multiplier = max_multiplier - (1 - price / threshold) * (1 + volatility_factor * price_volatility)
        else:
            multiplier = min_multiplier + (1 - threshold / price) * (1 - volatility_factor * price_volatility)

        multiplier = max(min_multiplier, min(multiplier, max_multiplier))

        investment = round(investment_amount * multiplier, 2)
        investment_schedule.append(investment)

    return investment_schedule

dca_investments = dca_strategy(future_predictions, investment_threshold)
print("Investment Schedule:", dca_investments)

"""## **Live Data**"""

def train_model():
    data_ticker = yf.Ticker("SOL-USD")
    new_data = data_ticker.history(period="1d")
    new_data = prepare_data(new_data)

    model = joblib.load("models/data_model.pkl")
    model.fit(new_data[features], new_data[target])
    joblib.dump(model, "models/model.pkl")

scheduler = BackgroundScheduler()
scheduler.add_job(train_model, 'interval', hours=24)
scheduler.start()

async def get_live_features():
    data_ticker = yf.Ticker("BTC-USD")
    data_newdata = data_ticker.history(period="1d")

    if data_newdata.empty:
        print("⚠️ No data retrieved, skipping prediction...")
        return None

    last_row = data_newdata.iloc[-1]
    live_features = np.array([
        last_row["Close"],
        last_row["High"] - last_row["Low"],
        last_row["Volume"],
        last_row["Close"] - last_row["Open"],
        last_row["Close"] / last_row["Open"],
        np.log(last_row["Volume"] + 1),
        np.random.rand()
    ]).reshape(1, -1)

    return live_features

"""## **WebSocket Integration**"""


async def send_predictions():
    uri = "ws://localhost:8080"  # WebSocket server URL

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                live_features = await get_live_features()
                if live_features is not None:
                    weekly_predictions = [round(float(model.predict(np.random.rand(1, 7))[0]), 2) for _ in range(7)]

                    weekly_dca = dca_strategy(weekly_predictions, investment_threshold)

                    message = {
                        "type": "PREDICTION",
                        "payload" : {
                            "coin": "SOL",
                            "weekly_predictions": weekly_predictions,
                            "weekly_dca_strategy": weekly_dca
                        }
                    }

                    await websocket.send(json.dumps(message))
                    print(f"📢 Sent Prediction Data: {message}")
                    
                else:
                    print("⚠️ No live features available, skipping prediction.")

            except Exception as e:
                print(f"❌ Error in prediction loop: {e}")

            await asyncio.sleep(10)  # Wait for 10 seconds

asyncio.run(send_predictions())