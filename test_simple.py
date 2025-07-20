#!/usr/bin/env python3
"""
Simple test script for the weekly prediction pipeline.
"""

from src.models.weekly_predict import WeeklyPredictionPipeline

def main():
    print("=== Testing Weekly Prediction Pipeline ===\n")
    
    # Initialize pipeline
    pipeline = WeeklyPredictionPipeline()
    
    # Run the pipeline
    print("Running weekly prediction pipeline...")
    results = pipeline.run_weekly_pipeline(retrain=True, prediction_days=5)
    
    # Display results
    print(f"\nStatus: {results['status']}")
    
    if results['status'] == 'success':
        print(f"Model R² Score: {results['model_metrics']['R2']:.4f}")
        print(f"Data Points Used: {results['data_points']}")
        
        print("\nPredictions for next 5 business days:")
        for i, pred in enumerate(results['predictions'], 1):
            print(f"  Day {i} ({pred['date']}): ${pred['predicted_price']:.2f}")
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"📁 Predictions saved to: {pipeline.predictions_path}")
        print(f"📊 Performance saved to: {pipeline.performance_path}")
    else:
        print(f"❌ Pipeline failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 