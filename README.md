# AI Stock Price Prediction Backend ( Python + Flask + Dialogflow )

This repository contains a set of Python scripts for stock prediction and analysis, utilizing various machine learning techniques and data visualization tools.

## Features

- Stock data retrieval from Alpha Vantage API
- Linear regression-based stock price prediction
- LSTM-based stock price prediction
- Moving average calculations
- Bollinger Bands visualization
- Firebase integration for data storage and retrieval
- Plotly-based interactive charts

## Main Components

### 1. Stock Data Retrieval

- `stock_to_firebase.py`: Fetches stock information and stores it in Firebase.
- `stock_yahoo.py`: Retrieves stock news from Yahoo Finance.

### 2. Stock Prediction

- `stockPrediction_linear.py`: Implements linear regression for stock price prediction.
- `stockPrediction_lstm.py`: Uses LSTM neural networks for stock price prediction.

### 3. Data Visualization

- Both prediction scripts include functions to create interactive Plotly charts.

### 4. Firebase Integration

- Firebase is used for storing and retrieving stock data and prediction results.

## Setup

1. Install required dependencies:

   ```
   pip install pandas numpy sklearn tensorflow plotly firebase-admin requests-html
   ```

2. Set up Firebase:

   - Place your Firebase credentials JSON file in the project root.
   - Update the Firebase configuration in the scripts.

3. Set up Alpha Vantage API:
   - Obtain an API key from Alpha Vantage.
   - Add the API key to the `.env` file:
     ```
     ALPHAVANTAGE_API_KEY=your_api_key_here
     ```

## Usage

1. To fetch stock data and store it in Firebase:

   ```
   python stock_to_firebase.py
   ```

2. To run linear regression prediction:

   ```
   python stockPrediction_linear.py
   ```

3. To run LSTM prediction:
   ```
   python stockPrediction_lstm.py
   ```

## Note

This project is for educational purposes only. Always do your own research and consult with financial professionals before making investment decisions.
