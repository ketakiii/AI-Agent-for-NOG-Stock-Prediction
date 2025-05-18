# Northern Oil and Gas (NOG) Stock Prediction 

An end-to-end time series forecasting pipeline that predicts the stock price of Northern Oil & Gas (NOG) using 13+ years of historical market and macroeconomic data. The project intergrates statistical, machine learning and deep learning models, data pipelines, model monitoring and visualizations. 

---

## Why Analyse Northern Oil & Gas (NOG)?
NOG is a key player in in the US oil industry, specializing in non-operating interests in high-quality oil & gas assets. There a multiple compelling reasons for analyzing this stock:

- **High Sensitivity to Macroeconomic Trends**: NOG's stock is closely tied to crude oil prices, interest rates, and global energy demand—making it ideal for studying the interplay between commodity markets and equities.
- **Energy Sector Volatility**: The energy sector is inherently cyclical and volatile, offering rich patterns for time series modeling and anomaly detection.
- **Market Relevance**: As a mid-cap stock in a critical sector, NOG is a useful proxy for understanding broader market behavior in energy and commodities.
- **Actionable Use Case**: Forecasting NOG prices has real-world use cases in portfolio allocation, algorithmic trading strategies, and hedging oil price exposure.

## Project Overview

| Area | Stack |
|------|-------|
| **Data Source** | Yahoo Finance API |
| **Feature Engineering** | Technical indicators (RSI, VWAP, Bollinger Bands), macroeconomic signals |
| **Models** | SARIMA (best), ARIMA, Prophet, LSTM (TensorFlow), Ridge, RF, XGBoost |
| **Pipeline** | Apache Airflow (ETL + modeling), Docker, PostgreSQL |
| **Serving** | FastAPI RESTful endpoints |
| **Tracking & CI/CD** | MLflow, Prometheus, Grafana, GitHub Actions |
| **Visualization** | Real-time Tableau dashboard |


## Key Features

- **SARIMA model reduced RMSE by ~30%**, outperforming classical and ML-based models.
- Designed modular, orchestrated workflows using **Apache Airflow**.
- **Logged and tracked models** with MLflow; integrated **experiment reproducibility**.
- Built and deployed containerized services using **Docker** and **FastAPI**.
- Maintained a clean CI/CD pipeline using **GitHub Actions**.
- Enabled **drift detection and monitoring** via Prometheus + Grafana.
- Delivered real-time **interactive analytics via Tableau dashboard**.

## Modeling Approach

- **Exploratory Analysis**: ACF/PACF plots, stationarity tests, rolling statistics.
- **Feature Engineering**:
- Technical: RSI, VWAP, Bollinger Bands, moving averages
- Macroeconomic: oil prices, interest rates (optional extensions)
- **Modeling Techniques**:
- Classical: SARIMA (winner)
- ML: Linear Regression, XGBoost
- DL: Prophet, LSTM using TensorFlow
- Hybrid comparisons against baselines


