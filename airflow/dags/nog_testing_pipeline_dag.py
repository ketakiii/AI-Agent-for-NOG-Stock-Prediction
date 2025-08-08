from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os
import json
import logging

# Default arguments for the DAG
default_args = {
    'owner': 'nog_team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['ketaki.kolhatkar99@gmail.com'],  # Your email for notifications
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'nog_testing_pipeline',
    default_args=default_args,
    description='Testing NOG pipeline: Standalone weekly predictions with existing data',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['nog', 'testing', 'prediction', 'xgboost', 'ml'],
)

def run_testing_predictions(**context):
    """
    Run weekly predictions with existing data for testing purposes.
    """
    # Import heavy dependencies inside the function to avoid timeout
    sys.path.append('/opt/airflow/project')
    from src.models.weekly_predict import WeeklyPredictionPipeline
    
    try:
        logging.info("Starting testing predictions with existing data...")
        
        # Initialize the pipeline
        pipeline = WeeklyPredictionPipeline()
        
        # Run with existing data
        results = pipeline.run_weekly_pipeline(update_data=False)
        
        if results["status"] == "success":
            logging.info("Testing predictions completed successfully")
            
            # Log key metrics
            metrics = results.get("model_metrics", {})
            logging.info(f"Model R² Score: {metrics.get('R2', 'N/A')}")
            logging.info(f"Data Points Used: {results.get('data_points', 'N/A')}")
            
            # Log predictions
            predictions = results.get("predictions", [])
            for pred in predictions:
                logging.info(f"Prediction for {pred['date']}: ${pred['predicted_price']:.2f}")
            
            # Store results in XCom for email
            context['task_instance'].xcom_push(key='prediction_results', value=results)
            
            return results
        else:
            error_msg = f"Testing predictions failed: {results.get('error', 'Unknown error')}"
            logging.error(f"{error_msg}")
            raise Exception(error_msg)
            
    except Exception as e:
        logging.error(f"Error in testing predictions: {e}")
        raise

def send_testing_email(**context):
    """
    Send testing results email.
    """
    try:
        # Get prediction results from XCom
        prediction_results = context['task_instance'].xcom_pull(key='prediction_results')
        
        if prediction_results:
            predictions = prediction_results.get("predictions", [])
            metrics = prediction_results.get("model_metrics", {})
            
            # Create email content
            email_content = f"""
            <h2>NOG Testing Predictions Results</h2>
            <p><strong>Data Source:</strong> Existing data (testing mode)</p>
            <p><strong>Model R² Score:</strong> {metrics.get('R2', 'N/A'):.4f}</p>
            <p><strong>Data Points Used:</strong> {prediction_results.get('data_points', 'N/A')}</p>
            
            <h3>Test Predictions for Next Week:</h3>
            <ul>
            """
            
            for pred in predictions:
                email_content += f"<li><strong>{pred['date']}:</strong> ${pred['predicted_price']:.2f}</li>"
            
            email_content += """
            </ul>
            <p><em>Generated on: {{ ds }}</em></p>
            """
            
            # Send email
            email_op = EmailOperator(
                task_id='send_testing_email',
                to=['ketaki.kolhatkar99@gmail.com'],
                subject=f'NOG Testing Predictions - {{ ds }}',
                html_content=email_content,
                dag=dag
            )
            
            email_op.execute(context)
            logging.info("Testing email sent successfully")
            
        else:
            logging.error("No prediction results found for testing email")
            
    except Exception as e:
        logging.error(f"Error in testing email: {e}")
        raise

# Define tasks
run_testing_task = PythonOperator(
    task_id='run_testing_predictions',
    python_callable=run_testing_predictions,
    dag=dag,
)

send_testing_email_task = PythonOperator(
    task_id='send_testing_email',
    python_callable=send_testing_email,
    dag=dag,
)

# Define task dependencies
run_testing_task >> send_testing_email_task 