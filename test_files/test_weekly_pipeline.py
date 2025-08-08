#!/usr/bin/env python3
"""
Test script for the enhanced weekly prediction pipeline with intelligent data updates.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append('/Users/ketakikolhatkar/Documents/Projects/NOG')

from src.models.weekly_predict import WeeklyPredictionPipeline

def test_weekly_pipeline():
    """Test the enhanced weekly prediction pipeline."""
    print("=== Testing Enhanced NOG Weekly Prediction Pipeline ===\n")
    
    try:
        # Initialize the pipeline
        print("1. Initializing pipeline...")
        pipeline = WeeklyPredictionPipeline()
        print("   ✓ Pipeline initialized successfully")
        
        # Check data update status
        print("\n2. Checking data update status...")
        data_status = pipeline.get_data_update_status()
        print(f"   ✓ Last update: {data_status['last_update']}")
        print(f"   ✓ Days since update: {data_status['days_since_update']}")
        print(f"   ✓ Next scheduled update: {data_status['next_scheduled_update']}")
        
        # Test data fetching
        print("\n3. Testing data fetching...")
        df = pipeline.fetch_latest_data(update_csv=False)
        print(f"   ✓ Data fetched successfully. Shape: {df.shape}")
        print(f"   ✓ Latest date: {df['Date'].max()}")
        
        # Test feature preparation
        print("\n4. Testing feature preparation...")
        features, target = pipeline.prepare_features(df)
        print(f"   ✓ Features prepared. Shape: {features.shape}")
        print(f"   ✓ Target prepared. Shape: {target.shape}")
        print(f"   ✓ Feature columns: {len(pipeline.feature_columns)}")
        
        # Test model training
        print("\n5. Testing model training...")
        performance_data = pipeline.train_weekly_model(features, target)
        print(f"   ✓ Model trained successfully")
        print(f"   ✓ R² Score: {performance_data['metrics']['R2']:.4f}")
        print(f"   ✓ MAE: {performance_data['metrics']['MAE']:.4f}")
        
        # Test prediction generation
        print("\n6. Testing prediction generation...")
        predictions = pipeline.generate_weekly_predictions(features, prediction_days=5)
        print(f"   ✓ Generated {len(predictions)} predictions")
        
        for i, pred in enumerate(predictions, 1):
            print(f"   Day {i} ({pred['date']}): ${pred['predicted_price']:.2f}")
        
        # Test saving functionality
        print("\n7. Testing save functionality...")
        pipeline.save_model()
        pipeline.save_predictions(predictions)
        pipeline.save_performance(performance_data)
        print("   ✓ Model, predictions, and performance data saved")
        
        # Test loading functionality
        print("\n8. Testing load functionality...")
        pipeline2 = WeeklyPredictionPipeline()
        loaded = pipeline2.load_model()
        if loaded:
            print("   ✓ Model loaded successfully")
        else:
            print("   ⚠ Model loading failed")
        
        # Test retrieving saved data
        print("\n9. Testing data retrieval...")
        latest_preds = pipeline.get_latest_predictions()
        performance_history = pipeline.get_performance_history()
        
        if latest_preds:
            print(f"   ✓ Retrieved {len(latest_preds)} saved predictions")
        if performance_history:
            print(f"   ✓ Retrieved {len(performance_history)} performance records")
        
        # Run complete pipeline
        print("\n10. Testing complete pipeline...")
        results = pipeline.run_weekly_pipeline(update_data=False, retrain=False, prediction_days=5)
        
        if results["status"] == "success":
            print("   ✓ Complete pipeline executed successfully")
            print(f"   ✓ Final R² Score: {results['model_metrics']['R2']:.4f}")
            print(f"   ✓ Data points used: {results['data_points']}")
            print(f"   ✓ Data updated: {results['data_updated']}")
        else:
            print(f"   ✗ Pipeline failed: {results.get('error', 'Unknown error')}")
        
        print("\n=== Test Results ===")
        print("✓ All tests completed successfully!")
        print(f"✓ Predictions saved to: {pipeline.predictions_path}")
        print(f"✓ Performance data saved to: {pipeline.performance_path}")
        print(f"✓ Model saved to: {pipeline.model_path}")
        print(f"✓ Data update tracker: {pipeline.data_update_tracker_path}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_force_data_update():
    """Test forcing a data update."""
    print("\n=== Testing Force Data Update ===\n")
    
    try:
        pipeline = WeeklyPredictionPipeline()
        
        print("Forcing data update...")
        results = pipeline.run_weekly_pipeline(update_data=True, retrain=True, prediction_days=5)
        
        if results["status"] == "success":
            print("✓ Force data update completed successfully")
            print(f"  Data updated: {results['data_updated']}")
            print(f"  Model R²: {results['model_metrics']['R2']:.4f}")
            return True
        else:
            print(f"✗ Force data update failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Force data update test failed: {e}")
        return False

def display_results():
    """Display the latest prediction results and data status."""
    try:
        pipeline = WeeklyPredictionPipeline()
        
        print("\n=== Latest Prediction Results ===")
        
        # Get latest predictions
        predictions = pipeline.get_latest_predictions()
        if predictions:
            print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\nPredictions for next 5 business days:")
            for i, pred in enumerate(predictions, 1):
                print(f"  Day {i} ({pred['date']}): ${pred['predicted_price']:.2f}")
                if 'confidence_interval' in pred:
                    ci = pred['confidence_interval']
                    print(f"           Range: ${ci['lower']:.2f} - ${ci['upper']:.2f}")
        else:
            print("No predictions found. Run the pipeline first.")
        
        # Get performance history
        performance_history = pipeline.get_performance_history()
        if performance_history:
            latest_performance = performance_history[-1]
            print(f"\nLatest Model Performance:")
            print(f"  R² Score: {latest_performance['metrics']['R2']:.4f}")
            print(f"  MAE: {latest_performance['metrics']['MAE']:.4f}")
            print(f"  Training Date: {latest_performance['training_date']}")
        
        # Get data update status
        data_status = pipeline.get_data_update_status()
        print(f"\nData Update Status:")
        print(f"  Last update: {data_status['last_update']}")
        print(f"  Days since update: {data_status['days_since_update']}")
        print(f"  Next scheduled update: {data_status['next_scheduled_update']}")
        print(f"  Update success: {data_status['update_success']}")
        
    except Exception as e:
        print(f"Error displaying results: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Enhanced NOG Weekly Prediction Pipeline')
    parser.add_argument('--test', action='store_true', help='Run full pipeline test')
    parser.add_argument('--force-update', action='store_true', help='Test force data update')
    parser.add_argument('--display', action='store_true', help='Display latest results')
    
    args = parser.parse_args()
    
    if args.force_update:
        success = test_force_data_update()
        if success:
            print("\n🎉 Force data update test completed successfully!")
        else:
            print("\n❌ Force data update test failed!")
            sys.exit(1)
    elif args.test:
        success = test_weekly_pipeline()
        if success:
            print("\n🎉 Pipeline test completed successfully!")
        else:
            print("\n❌ Pipeline test failed!")
            sys.exit(1)
    elif args.display:
        display_results()
    else:
        # Default: run test
        success = test_weekly_pipeline()
        if success:
            print("\n🎉 Pipeline test completed successfully!")
            display_results()
        else:
            print("\n❌ Pipeline test failed!")
            sys.exit(1) 