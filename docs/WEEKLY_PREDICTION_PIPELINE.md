# NOG Weekly Prediction Pipeline

A comprehensive weekly prediction pipeline for Northern Oil & Gas (NOG) stock price forecasting using XGBoost. This pipeline automatically fetches latest data, retrains the model, generates predictions, and provides monitoring capabilities.

## 🚀 Quick Start

### 1. Test the Pipeline
```bash
# Run the complete pipeline test
python test_weekly_pipeline.py --test

# Display latest results
python test_weekly_pipeline.py --display

# Run the pipeline directly
python src/models/weekly_predict.py
```

### 2. Set up Airflow (Optional)
```bash
# Copy the DAG to your Airflow dags folder
cp airflow/dags/nog_weekly_prediction_dag.py /path/to/airflow/dags/

# The DAG will run every Monday at 9 AM UTC
```

## 📊 Pipeline Overview

```
Data Fetching → Feature Engineering → Model Training → Prediction Generation → Validation → Reporting
```

### Components

1. **Data Pipeline** (`src/data/data_pipeline.py`)
   - Fetches latest NOG data from Yahoo Finance
   - Updates local CSV with new data
   - Integrates with macroeconomic indicators

2. **Feature Engineering** (`src/features/feature_engineering.py`)
   - Technical indicators (RSI, VWAP, Bollinger Bands)
   - Macroeconomic data (oil prices, Fed funds rate)
   - News sentiment analysis

3. **XGBoost Model** (`src/models/xgb.py`)
   - Optimized hyperparameters for time series forecasting
   - Feature importance analysis
   - Model evaluation metrics

4. **Weekly Pipeline** (`src/models/weekly_predict.py`)
   - Orchestrates the complete workflow
   - Handles model training and prediction
   - Saves results and performance metrics

## 🔧 Configuration

The pipeline is configured via `config/prediction_config.json`:

```json
{
  "model": {
    "parameters": {
      "n_estimators": 200,
      "learning_rate": 0.05,
      "max_depth": 6
    }
  },
  "prediction": {
    "days_ahead": 5,
    "confidence_level": 0.95
  }
}
```

## 📈 Output Files

### Predictions
- **Location**: `data/weekly_predictions.json`
- **Format**: JSON with predictions for next 5 business days
- **Example**:
```json
{
  "generated_date": "2025-01-20T10:30:00",
  "predictions": [
    {
      "date": "2025-01-21",
      "predicted_price": 25.34,
      "confidence_interval": {
        "lower": 24.83,
        "upper": 25.85
      }
    }
  ]
}
```

### Performance Metrics
- **Location**: `data/model_performance.json`
- **Metrics**: R², MAE, MSE, feature importance
- **Retention**: Last 52 weeks

### Model Files
- **Location**: `saved_models/xgb_model.pkl`
- **Format**: Pickled XGBoost model

## 🛠️ Usage Examples

### Basic Usage
```python
from src.models.weekly_predict import WeeklyPredictionPipeline

# Initialize pipeline
pipeline = WeeklyPredictionPipeline()

# Run complete pipeline
results = pipeline.run_weekly_pipeline(retrain=True, prediction_days=5)

# Get latest predictions
predictions = pipeline.get_latest_predictions()

# Get performance history
performance = pipeline.get_performance_history()
```

### Custom Configuration
```python
# Custom paths
pipeline = WeeklyPredictionPipeline(
    model_path='custom/path/model.pkl',
    predictions_path='custom/path/predictions.json'
)

# Run with custom settings
results = pipeline.run_weekly_pipeline(
    retrain=False,  # Use existing model
    prediction_days=10  # Predict 10 days ahead
)
```

## 📊 Monitoring & Validation

### Automatic Validation
The pipeline includes built-in validation checks:

1. **Price Range Check**: Predictions within $10-$100
2. **Negative Price Check**: No negative stock prices
3. **Volatility Check**: Reasonable day-to-day changes
4. **Confidence Interval Check**: Valid uncertainty bounds

### Performance Monitoring
- **R² Score**: Model accuracy (target: >0.7)
- **MAE**: Mean Absolute Error (target: <$2.0)
- **Feature Importance**: Track important features over time

### Alerts
- Email notifications on pipeline completion/failure
- Performance degradation alerts
- Data quality warnings

## 🔄 Airflow Integration

### DAG Structure
```
run_weekly_prediction
    ↓
[generate_report, validate_predictions]
    ↓
send_notification
```

### Schedule
- **Frequency**: Every Monday at 9 AM UTC
- **Retries**: 1 retry with 5-minute delay
- **Email Notifications**: On completion and failure

### Customization
Edit `airflow/dags/nog_weekly_prediction_dag.py`:
```python
# Change schedule
schedule_interval='0 9 * * 1'  # Cron expression

# Update email recipients
'email': ['your-email@example.com']
```

## 🧪 Testing

### Unit Tests
```bash
# Test individual components
python -m pytest tests/test_weekly_predict.py

# Test complete pipeline
python test_weekly_pipeline.py --test
```

### Integration Tests
```bash
# Test with Airflow
airflow tasks test nog_weekly_prediction run_weekly_prediction 2025-01-20
```

## 📝 Logging

The pipeline uses structured logging:

```python
import logging
logger = logging.getLogger(__name__)

# Log levels: INFO, WARNING, ERROR
logger.info("Pipeline started")
logger.warning("High volatility detected")
logger.error("Data fetch failed")
```

Logs are saved to `logs/prediction/` with rotation.

## 🔍 Troubleshooting

### Common Issues

1. **Data Fetch Error**
   - Check internet connection
   - Verify Yahoo Finance API access
   - Check date ranges in config

2. **Model Training Failure**
   - Insufficient data points
   - Missing features
   - Memory constraints

3. **Prediction Validation Failures**
   - Unusual market conditions
   - Data quality issues
   - Model drift

### Debug Mode
```python
# Enable debug logging
logging.getLogger().setLevel(logging.DEBUG)

# Run with verbose output
pipeline = WeeklyPredictionPipeline()
results = pipeline.run_weekly_pipeline(retrain=True)
```

## 📚 API Reference

### WeeklyPredictionPipeline

#### Methods
- `fetch_latest_data(update_csv=True)` → DataFrame
- `prepare_features(df)` → (features, target)
- `train_weekly_model(features, target)` → Dict
- `generate_weekly_predictions(features, days=5)` → List[Dict]
- `run_weekly_pipeline(retrain=True, days=5)` → Dict
- `get_latest_predictions()` → List[Dict]
- `get_performance_history()` → List[Dict]

#### Properties
- `model_path`: Path to saved model
- `predictions_path`: Path to predictions file
- `performance_path`: Path to performance metrics
- `feature_columns`: List of feature column names

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/prediction/`
3. Open an issue on GitHub
4. Contact the development team 