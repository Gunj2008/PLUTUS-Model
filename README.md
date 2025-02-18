# **DCA Crypto Prediction Model**

This repository contains an AI-driven **Dollar-Cost Averaging (DCA) Strategy** for cryptocurrency investments. The model predicts future Bitcoin (BTC) prices using **Random Forest and XGBoost** machine learning algorithms, integrating **technical indicators** such as SMA, MACD, RSI, and volatility.

## **Features**
- **Data Gathering** – Fetches real-time BTC price data using `yfinance`
- **Feature Engineering** – Computes SMA, MACD, RSI, and volatility indicators
- **Machine Learning Models** – Uses **RandomForestRegressor** & **XGBoost** for BTC price predictions
- **DCA Investment Strategy** – Generates an optimized **investment schedule**
- **Live Model Retraining** – Uses **APScheduler** for automated daily updates
- **WebSocket Integration** – Sends predictions via WebSocket for real-time insights

## **Installation**
### **1. Clone the Repository**
```bash
git clone https://github.com/Gunj2008/PLUTUS-Model.git
cd PLUTUS-Model
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

## **Usage**
Run the script to fetch BTC data, train the model, and generate predictions:
```bash
python model.py
```

## **API & WebSocket Integration**
- **Flask API**: Can be extended to serve predictions via an API
- **WebSockets**: Sends live price predictions & investment strategies

## **Project Structure**
```
├── model.py                  # Main script for data processing, training, and prediction
├── requirements.txt        # Dependencies for the project
├── README.md               # Project documentation
├── models/                 # Trained machine learning models
├── data/                   # Historical cryptocurrency data
```

## **Future Improvements**
- 🔹 Support for more cryptocurrencies (e.g., Ethereum, Solana)
- 🔹 Advanced deep learning models for improved accuracy
- 🔹 Interactive frontend dashboard for visualization

## **License**
This project is open-source and available under the **MIT License**.

## **Contributing**
Feel free to fork this repository, open issues, or submit pull requests to improve the project.

🚀 **Happy Investing!**

