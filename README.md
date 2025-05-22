# Northern Oil & Gas (NOG) Stock Price Forecasting

An end-to-end time series forecasting pipeline that predicts the stock price of Northern Oil & Gas (NOG) using 15+ years of historical market and macroeconomic data. The project integrates advanced statistical models, deep learning, data pipelines, model monitoring, and real-time visual analytics.

---

## Why Analyze Northern Oil & Gas (NOG)?

Northern Oil & Gas (NYSE: NOG) is a key player in the U.S. shale oil industry, specializing in non-operating interests in high-quality oil & gas assets. It presents a compelling forecasting challenge for several reasons:

- **High Sensitivity to Macroeconomic Trends**: NOG's stock is closely tied to crude oil prices, interest rates, and global energy demand—making it ideal for studying the interplay between commodity markets and equities.
- **Energy Sector Volatility**: The energy sector is inherently cyclical and volatile, offering rich patterns for time series modeling and anomaly detection.
- **Market Relevance**: As a mid-cap stock in a critical sector, NOG is a useful proxy for understanding broader market behavior in energy and commodities.
- **Actionable Use Case**: Forecasting NOG prices has real-world use cases in portfolio allocation, algorithmic trading strategies, and hedging oil price exposure.

---

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

---

## Key Features

- **SARIMA model reduced RMSE by ~30%**, outperforming classical and ML-based models.
- Designed modular, orchestrated workflows using **Apache Airflow**.
- **Logged and tracked models** with MLflow; integrated **experiment reproducibility**.
- Built and deployed containerized services using **Docker** and **FastAPI**.
- Maintained a clean CI/CD pipeline using **GitHub Actions**.
- Enabled **drift detection and monitoring** via Prometheus + Grafana.
- Delivered real-time **interactive analytics via Tableau dashboard**.

---

## Modeling Approach

- **Exploratory Analysis**: ACF/PACF plots, stationarity tests, rolling statistics.
- **Feature Engineering**:
- Technical: RSI, VWAP, Bollinger Bands, moving averages
- Macroeconomic: oil prices, interest rates (optional extensions)
- **Modeling Techniques**:
- Classical: SARIMA (winner)
- ML: Linear Regression, XGBoost, Random Forest
- DL: Prophet, LSTM
- Hybrid comparisons against baselines

## Visualization
Tableau dashboard 1 - https://public.tableau.com/app/profile/ketaki.kolhatkar/viz/NOG-stock-dashboard-1/NOG-dashboard-1?publish=yes

Tableau dashboard 2 - https://public.tableau.com/app/profile/ketaki.kolhatkar/viz/NOG-stock-dashboard-1/NOG-dashboard-2?publish=yes

Tableau dashboard 3 - https://public.tableau.com/app/profile/ketaki.kolhatkar/viz/NOG-stock-dashboard-1/NOG-dashboard-3?publish=yes

## Repository Structure
```bash
nog-stock-forecasting/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── notebooks/
│   └── NOG_forecasting.ipynb    
│
├── data/  
│   └── NOG_2012-01-01_2025-04-27.csv                       
|
├── saved_models/  
│   └── xgb_model.pkl  
|
├── src/
│   ├── data
│       ├── __init__.py
│       └── data_pipeline.py 
│   └── features  
│       ├── __init__.py
│       └── feature_engineering.py 
│   └── models     
│       ├── __init__.py
│       └── xgb.py 
│       └── embed.py 
│   └── llm     
│       ├── __init__.py
│       └── llm_inference.py     
│       └── rag_retrieval.py   
```

## Repository Structure
                      ┌───────────────────────┐
                      │ Yahoo Finance (2 yrs) │
                      └──────────┬────────────┘
                                 ▼
                         Price/Volume Features
                                 ▼
                            XGBoost Model
                                 ▼
                        Price Forecast + Residual
                                 ▼
                     ┌────────────────────────────┐
                     │ LLM + News Retrieval Agent │
                     └────────────┬───────────────┘
                                  ▼
             ┌─────────────────────────────────────────────────────┐
             │ RAG: News Embeddings (CLIP/SBERT) + FAISS/Chroma DB │
             └────────────────────┬────────────────────────────────┘
                                  ▼
             Recent, relevant news context about NOG or oil sector
                                  ▼
                LLM interprets context & prediction
                                  ▼
             Generates explanation, risk insights, actions
