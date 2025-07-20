from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os

# Add the project root to Python path
sys.path.append('/opt/airflow/project')

from src.models.weekly_predict import WeeklyPredictionPipeline
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
    'nog_production_pipeline',
    default_args=default_args,
    description='Production NOG pipeline: Force data update first, fallback to weekly predictions if fails',
    schedule_interval='0 9 * * 1',  # Run every Monday at 9 AM
    catchup=False,
    tags=['nog', 'production', 'prediction', 'xgboost', 'ml'],
)

def force_data_update(**context):
    """
    Force data update from Yahoo Finance (fresh data).
    Returns success=True if successful, False if failed.
    """
    try:
        logging.info("🔄 Force data update: Fetching fresh data from Yahoo Finance...")
        
        # Initialize the pipeline
        pipeline = WeeklyPredictionPipeline()
        
        # Try to run with fresh data
        results = pipeline.run_weekly_pipeline(update_data=True)
        
        if results["status"] == "success":
            logging.info("✅ Force data update successful!")
            context['task_instance'].xcom_push(key='force_update_success', value=True)
            context['task_instance'].xcom_push(key='prediction_results', value=results)
            return True
        else:
            logging.warning(f"⚠️ Force data update failed: {results.get('error', 'Unknown error')}")
            context['task_instance'].xcom_push(key='force_update_success', value=False)
            return False
            
    except Exception as e:
        logging.error(f"❌ Error in force data update: {e}")
        context['task_instance'].xcom_push(key='force_update_success', value=False)
        return False

def run_weekly_predictions(**context):
    """
    Run weekly predictions with existing data (fallback).
    """
    try:
        logging.info("🔄 Running weekly predictions with existing data...")
        
        # Initialize the pipeline
        pipeline = WeeklyPredictionPipeline()
        
        # Run with existing data
        results = pipeline.run_weekly_pipeline(update_data=False)
        
        if results["status"] == "success":
            logging.info("✅ Weekly predictions with existing data completed successfully")
            context['task_instance'].xcom_push(key='prediction_results', value=results)
            return results
        else:
            error_msg = f"Weekly predictions failed: {results.get('error', 'Unknown error')}"
            logging.error(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    except Exception as e:
        logging.error(f"❌ Error in weekly predictions: {e}")
        raise

def decide_next_step(**context):
    """
    Decide whether to send email (force update succeeded) or run weekly predictions.
    """
    force_update_success = context['task_instance'].xcom_pull(key='force_update_success')
    
    if force_update_success:
        logging.info("✅ Force data update succeeded, proceeding to send email")
        return 'send_success_email'
    else:
        logging.info("⚠️ Force data update failed, proceeding to run weekly predictions")
        return 'run_weekly_predictions'

def send_success_email(**context):
    """
    Send success email with prediction results.
    """
    try:
        # Get prediction results from XCom
        prediction_results = context['task_instance'].xcom_pull(key='prediction_results')
        force_update_success = context['task_instance'].xcom_pull(key='force_update_success')
        
        if prediction_results:
            predictions = prediction_results.get("predictions", [])
            metrics = prediction_results.get("model_metrics", {})
            
            # Create email content
            data_source = "fresh Yahoo Finance data" if force_update_success else "existing data"
            email_content = f"""
            <h2>✅ NOG Weekly Prediction Results</h2>
            <p><strong>Data Source:</strong> {data_source}</p>
            <p><strong>Model R² Score:</strong> {metrics.get('R2', 'N/A'):.4f}</p>
            <p><strong>Data Points Used:</strong> {prediction_results.get('data_points', 'N/A')}</p>
            
            <h3>Predictions for Next Week:</h3>
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
                task_id='send_success_email',
                to=['ketaki.kolhatkar99@gmail.com'],
                subject=f'✅ NOG Weekly Predictions - {data_source} - {{ ds }}',
                html_content=email_content,
                dag=dag
            )
            
            email_op.execute(context)
            logging.info("✅ Success email sent")
            
        else:
            logging.error("❌ No prediction results found for email")
            
    except Exception as e:
        logging.error(f"❌ Error sending success email: {e}")
        raise

# Define tasks
force_data_update_task = PythonOperator(
    task_id='force_data_update',
    python_callable=force_data_update,
    dag=dag,
)

decide_next_step_task = BranchPythonOperator(
    task_id='decide_next_step',
    python_callable=decide_next_step,
    dag=dag,
)

run_weekly_predictions_task = PythonOperator(
    task_id='run_weekly_predictions',
    python_callable=run_weekly_predictions,
    dag=dag,
)

send_email_task = PythonOperator(
    task_id='send_success_email',
    python_callable=send_success_email,
    dag=dag,
)

# Define task dependencies
force_data_update_task >> decide_next_step_task
decide_next_step_task >> [send_email_task, run_weekly_predictions_task]
run_weekly_predictions_task >> send_email_task 