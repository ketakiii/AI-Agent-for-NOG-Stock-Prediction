import pandas as pd 
import joblib
import datetime
import numpy as np
import os
import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Import your existing modules
from src.data.data_pipeline import run_data_pipeline
from src.models.xgb import train_model, evaluate_model, predict
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyPredictionPipeline:
    """
    Weekly prediction pipeline for NOG stock price forecasting using XGBoost.
    Intelligently updates data on a weekly basis.
    """
    
    def __init__(self, model_path: str = 'saved_models/xgb_model.pkl', 
                 predictions_path: str = 'data/weekly_predictions.json',
                 performance_path: str = 'data/model_performance.json',
                 data_update_tracker_path: str = 'data/data_update_tracker.json'):
        """
        Initialize the weekly prediction pipeline.
        
        Args:
            model_path: Path to save/load the XGBoost model
            predictions_path: Path to save weekly predictions
            performance_path: Path to save model performance metrics
            data_update_tracker_path: Path to track data update schedule
        """
        self.model_path = model_path
        self.predictions_path = predictions_path
        self.performance_path = performance_path
        self.data_update_tracker_path = data_update_tracker_path
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs(os.path.dirname(predictions_path), exist_ok=True)
        
        self.model = None
        self.feature_columns = None
        
    def should_update_data(self) -> bool:
        """
        Check if data should be updated based on weekly schedule.
        
        Returns:
            True if data should be updated, False otherwise
        """
        try:
            with open(self.data_update_tracker_path, 'r') as f:
                tracker = json.load(f)
            
            last_update = datetime.datetime.fromisoformat(tracker['last_update'])
            days_since_update = (datetime.datetime.now() - last_update).days
            
            # Update data if:
            # 1. It's been more than 7 days since last update, OR
            # 2. It's Monday and we haven't updated this week
            should_update = (
                days_since_update >= 7 or 
                (datetime.datetime.now().weekday() == 0 and days_since_update >= 1)
            )
            
            logger.info(f"Days since last update: {days_since_update}")
            logger.info(f"Should update data: {should_update}")
            
            return should_update
            
        except FileNotFoundError:
            # First time running - should update
            logger.info("No update tracker found - will update data")
            return True
    
    def update_data_tracker(self, success: bool = True):
        """
        Update the data update tracker.
        
        Args:
            success: Whether the data update was successful
        """
        tracker = {
            'last_update': datetime.datetime.now().isoformat(),
            'update_success': success,
            'next_scheduled_update': (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
        }
        
        with open(self.data_update_tracker_path, 'w') as f:
            json.dump(tracker, f, indent=2)
        
        logger.info(f"Data update tracker updated: {tracker['last_update']}")
    
    def fetch_latest_data(self, update_csv: bool = False) -> pd.DataFrame:
        """
        Fetch the latest data using the data pipeline.
        
        Args:
            update_csv: Whether to fetch new data (False=use existing, True=fetch new)
            
        Returns:
            DataFrame with latest processed data
        """
        logger.info(f"Fetching data (update_csv={update_csv})...")
        
        try:
            df = run_data_pipeline(csvflag=not update_csv)
            logger.info(f"Successfully fetched data with shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for modeling.
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            Tuple of (features, target)
        """
        # Store feature columns for later use
        self.feature_columns = [col for col in df.columns if col not in ['Date', 'Close']]
        
        features = df[self.feature_columns].copy()
        target = df['Close'].copy()
        
        # Handle any missing values
        features = features.fillna(method='ffill').fillna(method='bfill')
        
        return features, target
    
    def train_weekly_model(self, features: pd.DataFrame, target: pd.Series, 
                          test_size: float = 0.2) -> Dict:
        """
        Train the XGBoost model with latest data.
        
        Args:
            features: Feature DataFrame
            target: Target Series
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training results and metrics
        """
        logger.info("Training weekly model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=test_size, random_state=42, shuffle=False
        )
        
        # Train model with optimized parameters
        model_params = {
            "objective": "reg:squarederror",
            "n_estimators": 200,
            "learning_rate": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42
        }
        
        self.model = train_model(X_train, y_train, model_params)
        
        # Evaluate model
        metrics = evaluate_model(self.model, X_test, y_test)
        
        # Convert numpy values to Python floats for JSON serialization
        metrics = {k: float(v) for k, v in metrics.items()}
        
        # Feature importance
        if self.feature_columns and hasattr(self.model, 'feature_importances_'):
            feature_importance = dict(zip(self.feature_columns, 
                                        [float(x) for x in self.model.feature_importances_]))
        else:
            feature_importance = {}
        
        results = {
            "training_date": datetime.datetime.now().isoformat(),
            "metrics": metrics,
            "feature_importance": feature_importance,
            "data_shape": features.shape,
            "train_size": len(X_train),
            "test_size": len(X_test)
        }
        
        logger.info(f"Model training completed. R²: {metrics['R2']:.4f}")
        return results
    
    def save_model(self) -> None:
        """Save the trained model."""
        if self.model is not None:
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
        else:
            logger.warning("No model to save")
    
    def load_model(self) -> bool:
        """Load the saved model."""
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
            return True
        except FileNotFoundError:
            logger.warning(f"No saved model found at {self.model_path}")
            return False
    
    def generate_weekly_predictions(self, features: pd.DataFrame, 
                                  prediction_days: int = 5) -> List[Dict]:
        """
        Generate predictions for the upcoming week.
        
        Args:
            features: Latest feature data
            prediction_days: Number of days to predict ahead
            
        Returns:
            List of prediction dictionaries
        """
        if self.model is None:
            raise ValueError("Model not loaded or trained")
        
        logger.info(f"Generating predictions for next {prediction_days} days...")
        
        # Use the most recent data for predictions
        latest_features = features.tail(1)
        
        predictions = []
        current_date = datetime.datetime.now()
        
        for i in range(prediction_days):
            # Predict next day
            pred = self.model.predict(latest_features)[0]
            
            # Calculate next business day
            next_date = current_date + datetime.timedelta(days=i+1)
            while next_date.weekday() >= 5:  # Skip weekends
                next_date += datetime.timedelta(days=1)
            
            prediction_data = {
                "date": next_date.strftime("%Y-%m-%d"),
                "predicted_price": float(pred),
                "prediction_date": current_date.strftime("%Y-%m-%d"),
                "model_version": self.model_path,
                "confidence_interval": self._calculate_confidence_interval(float(pred))
            }
            
            predictions.append(prediction_data)
        
        return predictions
    
    def _calculate_confidence_interval(self, prediction: float, 
                                     confidence_level: float = 0.95) -> Dict:
        """
        Calculate confidence interval for prediction.
        
        Args:
            prediction: Predicted value
            confidence_level: Confidence level (0.95 = 95%)
            
        Returns:
            Dictionary with lower and upper bounds
        """
        # Simple confidence interval based on historical volatility
        # In a production system, you'd use more sophisticated methods
        margin = prediction * 0.02  # 2% margin
        
        return {
            "lower": prediction - margin,
            "upper": prediction + margin,
            "confidence_level": confidence_level
        }
    
    def save_predictions(self, predictions: List[Dict]) -> None:
        """Save weekly predictions to JSON file."""
        prediction_data = {
            "generated_date": datetime.datetime.now().isoformat(),
            "predictions": predictions
        }
        
        with open(self.predictions_path, 'w') as f:
            json.dump(prediction_data, f, indent=2)
        
        logger.info(f"Predictions saved to {self.predictions_path}")
    
    def save_performance(self, performance_data: Dict) -> None:
        """Save model performance metrics."""
        # Load existing performance data if available
        existing_data = []
        if os.path.exists(self.performance_path):
            try:
                with open(self.performance_path, 'r') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("Corrupted performance file found, starting fresh")
                existing_data = []
        
        # Add new performance data
        existing_data.append(performance_data)
        
        # Keep only last 52 weeks (1 year) of performance data
        if len(existing_data) > 52:
            existing_data = existing_data[-52:]
        
        with open(self.performance_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        logger.info(f"Performance data saved to {self.performance_path}")
    
    def run_weekly_pipeline(self, update_data: bool = False, 
                           retrain: bool = True, 
                           prediction_days: int = 5) -> Dict:
        """
        Run the complete weekly prediction pipeline.
        
        Args:
            force_data_update: Force data update regardless of schedule
            retrain: Whether to retrain the model
            prediction_days: Number of days to predict ahead
            
        Returns:
            Dictionary with pipeline results
        """
        logger.info("Starting weekly prediction pipeline...")
        
        try:
            # 1. Fetch latest data
            df = self.fetch_latest_data(update_csv=update_data)
            
            # 2. Prepare features
            features, target = self.prepare_features(df)
            
            # 3. Train or load model
            if retrain:
                performance_data = self.train_weekly_model(features, target)
                self.save_model()
                self.save_performance(performance_data)
            else:
                if not self.load_model():
                    logger.warning("No saved model found, training new model...")
                    performance_data = self.train_weekly_model(features, target)
                    self.save_model()
                    self.save_performance(performance_data)
            
            # 4. Generate predictions
            predictions = self.generate_weekly_predictions(features, prediction_days)
            
            # 5. Save predictions
            self.save_predictions(predictions)
            
            # 6. Prepare results
            results = {
                "status": "success",
                "timestamp": datetime.datetime.now().isoformat(),
                "predictions": predictions,
                "model_metrics": performance_data.get("metrics", {}),
                "data_points": len(features),
                "data_updated": update_data
            }
            
            logger.info("Weekly prediction pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return {
                "status": "error",
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_latest_predictions(self) -> Optional[List[Dict]]:
        """Get the latest saved predictions."""
        try:
            with open(self.predictions_path, 'r') as f:
                data = json.load(f)
            return data.get("predictions", [])
        except FileNotFoundError:
            logger.warning("No predictions file found")
            return None
    
    def get_performance_history(self) -> List[Dict]:
        """Get historical performance data."""
        try:
            with open(self.performance_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No performance file found")
            return []
    
    def get_data_update_status(self) -> Dict:
        """Get data update status and schedule."""
        try:
            with open(self.data_update_tracker_path, 'r') as f:
                tracker = json.load(f)
            
            last_update = datetime.datetime.fromisoformat(tracker['last_update'])
            next_update = datetime.datetime.fromisoformat(tracker['next_scheduled_update'])
            
            return {
                "last_update": tracker['last_update'],
                "next_scheduled_update": tracker['next_scheduled_update'],
                "days_since_update": (datetime.datetime.now() - last_update).days,
                "days_until_next_update": (next_update - datetime.datetime.now()).days,
                "update_success": tracker.get('update_success', True)
            }
        except FileNotFoundError:
            return {
                "last_update": "Never",
                "next_scheduled_update": "Unknown",
                "days_since_update": float('inf'),
                "days_until_next_update": 0,
                "update_success": False
            }

def main():
    """Main function to run the weekly prediction pipeline."""
    pipeline = WeeklyPredictionPipeline()
    
    # Run the pipeline
    results = pipeline.run_weekly_pipeline(update_data=False, retrain=True, prediction_days=5)
    
    if results["status"] == "success":
        print("\n=== Weekly Prediction Results ===")
        print(f"Model R² Score: {results['model_metrics']['R2']:.4f}")
        print(f"Data Points Used: {results['data_points']}")
        print(f"Data Updated: {results['data_updated']}")
        print("\nPredictions for next 5 business days:")
        
        for pred in results["predictions"]:
            print(f"  {pred['date']}: ${pred['predicted_price']:.2f}")
        
        print(f"\nResults saved to: {pipeline.predictions_path}")
        
        # Show data update status
        status = pipeline.get_data_update_status()
        print(f"\nData Update Status:")
        print(f"  Last update: {status['last_update']}")
        print(f"  Days since update: {status['days_since_update']}")
        print(f"  Next scheduled update: {status['next_scheduled_update']}")
    else:
        print(f"Pipeline failed: {results['error']}")

if __name__ == "__main__":
    main()