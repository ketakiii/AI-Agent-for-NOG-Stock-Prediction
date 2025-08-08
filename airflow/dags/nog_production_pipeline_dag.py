from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os
import json
import logging

# Configure detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    description='Production NOG pipeline: Monthly fresh data update, weekly predictions with existing data',
    schedule_interval='0 9 * * 1',  # Run every Monday at 9 AM
    catchup=False,
    tags=['nog', 'production', 'prediction', 'xgboost', 'ml'],
)

def should_update_data_monthly(**context):
    """
    Check if this is the first Monday of the month (monthly data update day).
    Returns True if it's the first Monday of the month, False otherwise.
    """
    execution_date = context['execution_date']
    logger.info(f"Checking if monthly data update is needed for: {execution_date}")
    
    # Check if it's the first Monday of the month
    is_first_monday = execution_date.day <= 7 and execution_date.weekday() == 0  # Monday = 0
    
    logger.info(f"Execution date: {execution_date}")
    logger.info(f"Day of month: {execution_date.day}")
    logger.info(f"Day of week: {execution_date.weekday()} (0=Monday)")
    logger.info(f"Is first Monday of month: {is_first_monday}")
    
    if is_first_monday:
        logger.info("MONTHLY UPDATE: This is the first Monday of the month - will fetch fresh data")
    else:
        logger.info("WEEKLY RUN: This is a regular weekly run - will use existing data")
    
    return is_first_monday

def force_data_update(**context):
    """
    Try to force data update from Yahoo Finance (fresh data).
    This task only runs on the first Monday of each month.
    Returns success=True if successful, False if failed.
    """
    # Import heavy dependencies inside the function to avoid timeout
    sys.path.append('/opt/airflow/project')
    from src.models.weekly_predict import WeeklyPredictionPipeline
    
    logger.info("STARTING: force_data_update task (MONTHLY)")
    logger.info(f"Execution date: {context['execution_date']}")
    logger.info(f"Task instance: {context['task_instance'].task_id}")
    
    try:
        logger.info("STEP 1: Attempting to fetch fresh data from Yahoo Finance...")
        logger.info("Initializing WeeklyPredictionPipeline...")
        
        # Initialize the pipeline
        pipeline = WeeklyPredictionPipeline()
        logger.info("WeeklyPredictionPipeline initialized successfully")
        
        # Try to run with fresh data
        logger.info("STEP 2: Calling pipeline.run_weekly_pipeline(update_data=True)...")
        logger.info("This should fetch fresh data from Yahoo Finance API")
        
        results = pipeline.run_weekly_pipeline(update_data=True)
        
        logger.info(f"STEP 3: Pipeline returned results: {results}")
        
        if results["status"] == "success":
            logger.info("SUCCESS: Force data update completed successfully!")
            logger.info(f"Predictions made: {len(results.get('predictions', []))}")
            logger.info(f"Model metrics: {results.get('model_metrics', {})}")
            logger.info(f"Data points used: {results.get('data_points', 'N/A')}")
            
            context['task_instance'].xcom_push(key='force_update_success', value=True)
            context['task_instance'].xcom_push(key='prediction_results', value=results)
            logger.info("Results saved to XCom for next task")
            return True
        else:
            error_msg = f"FAILED: Force data update failed: {results.get('error', 'Unknown error')}"
            logger.warning(error_msg)
            logger.warning(f"Error details: {results}")
            context['task_instance'].xcom_push(key='force_update_success', value=False)
            return False
            
    except Exception as e:
        logger.error(f"EXCEPTION in force_data_update: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {e}")
        context['task_instance'].xcom_push(key='force_update_success', value=False)
        return False
    
    finally:
        logger.info("COMPLETED: force_data_update task")

def run_weekly_predictions(**context):
    """
    Run weekly predictions. Use fresh data if available (monthly), otherwise use existing data (weekly).
    If fresh data fails, automatically fallback to existing data.
    """
    # Import heavy dependencies inside the function to avoid timeout
    sys.path.append('/opt/airflow/project')
    from src.models.weekly_predict import WeeklyPredictionPipeline
    
    logger.info("STARTING: run_weekly_predictions task")
    logger.info(f"Execution date: {context['execution_date']}")
    logger.info(f"Task instance: {context['task_instance'].task_id}")
    
    try:
        # Check if this is a monthly run (fresh data) or weekly run (existing data)
        is_monthly_update = should_update_data_monthly(**context)
        
        if is_monthly_update:
            # This is a monthly run - check if force_data_update succeeded
            logger.info("STEP 1: Checking force_data_update results from XCom (monthly run)...")
            force_update_success = context['task_instance'].xcom_pull(key='force_update_success')
            logger.info(f"Force update success flag: {force_update_success}")
        else:
            # This is a weekly run - always use existing data
            logger.info("STEP 1: Weekly run detected - will use existing data")
            force_update_success = False  # Always use existing data for weekly runs
        
        # Initialize the pipeline
        logger.info("STEP 2: Initializing WeeklyPredictionPipeline...")
        pipeline = WeeklyPredictionPipeline()
        logger.info("WeeklyPredictionPipeline initialized successfully")
        
        # Determine data source
        if is_monthly_update:
            data_source = "fresh Yahoo Finance data" if force_update_success else "existing data (fallback)"
        else:
            data_source = "existing data (weekly run)"
            force_update_success = False  # Ensure we use existing data for weekly runs
        
        logger.info(f"STEP 3: Running weekly predictions with {data_source}...")
        
        try:
            # Use the existing flag - True for fresh data, False for existing data
            logger.info(f"STEP 4: Calling pipeline.run_weekly_pipeline(update_data={force_update_success})")
            logger.info(f"This should use {'fresh' if force_update_success else 'existing'} data")
            
            results = pipeline.run_weekly_pipeline(update_data=force_update_success)
            
            logger.info(f"STEP 5: Pipeline returned results: {results}")
            
            if results["status"] == "success":
                logger.info(f"SUCCESS: Weekly predictions with {data_source} completed successfully!")
                logger.info(f"Predictions made: {len(results.get('predictions', []))}")
                logger.info(f"Model metrics: {results.get('model_metrics', {})}")
                logger.info(f"Data points used: {results.get('data_points', 'N/A')}")
                
                context['task_instance'].xcom_push(key='prediction_results', value=results)
                logger.info("Results saved to XCom for email task")
                return results
            else:
                error_msg = f"FAILED: Weekly predictions failed: {results.get('error', 'Unknown error')}"
                logger.error(error_msg)
                logger.error(f"Error details: {results}")
                raise Exception(error_msg)
                
        except FileNotFoundError as e:
            # Specific handling for file not found errors
            logger.error(f"FILE NOT FOUND ERROR: {e}")
            if force_update_success:
                logger.warning(f"FALLBACK: File not found with fresh data, falling back to existing data")
                logger.info("Retrying weekly predictions with existing data...")
            else:
                logger.error(f"CRITICAL: File not found with existing data: {e}")
                raise e
        except Exception as e:
            # If fresh data failed but we were trying to use fresh data, fallback to existing data
            logger.error(f"EXCEPTION: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            
            if force_update_success:
                logger.warning(f"FALLBACK: Fresh data failed, falling back to existing data")
                logger.info("STEP 6: Retrying weekly predictions with existing data...")
                
                try:
                    logger.info("Calling pipeline.run_weekly_pipeline(update_data=False)...")
                    results = pipeline.run_weekly_pipeline(update_data=False)
                    
                    logger.info(f"Fallback pipeline returned results: {results}")
                    
                    if results["status"] == "success":
                        logger.info("SUCCESS: Weekly predictions with existing data completed successfully!")
                        logger.info(f"Predictions made: {len(results.get('predictions', []))}")
                        logger.info(f"Model metrics: {results.get('model_metrics', {})}")
                        logger.info(f"Data points used: {results.get('data_points', 'N/A')}")
                        
                        context['task_instance'].xcom_push(key='prediction_results', value=results)
                        # Update the flag to indicate we used existing data
                        context['task_instance'].xcom_push(key='force_update_success', value=False)
                        logger.info("Results saved to XCom for email task")
                        return results
                    else:
                        error_msg = f"FAILED: Weekly predictions with existing data failed: {results.get('error', 'Unknown error')}"
                        logger.error(error_msg)
                        logger.error(f"Error details: {results}")
                        raise Exception(error_msg)
                        
                except Exception as fallback_error:
                    logger.error(f"CRITICAL: Both fresh and existing data failed!")
                    logger.error(f"Fallback exception: {str(fallback_error)}")
                    logger.error(f"Fallback exception type: {type(fallback_error).__name__}")
                    raise fallback_error
            else:
                # If we were already using existing data and it failed, just raise the error
                logger.error(f"CRITICAL: Error in weekly predictions with existing data: {e}")
                raise e
            
    except Exception as e:
        logger.error(f"EXCEPTION in run_weekly_predictions: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise
    
    finally:
        logger.info("COMPLETED: run_weekly_predictions task")

def send_success_email(**context):
    """
    Send success email with prediction results.
    """
    logger.info("STARTING: send_success_email task")
    logger.info(f"Execution date: {context['execution_date']}")
    logger.info(f"Task instance: {context['task_instance'].task_id}")
    
    try:
        # Get prediction results from XCom
        logger.info("STEP 1: Retrieving prediction results from XCom...")
        prediction_results = context['task_instance'].xcom_pull(key='prediction_results')
        force_update_success = context['task_instance'].xcom_pull(key='force_update_success')
        
        # Check if this was a monthly or weekly run
        is_monthly_update = should_update_data_monthly(**context)
        
        logger.info(f"Force update success flag: {force_update_success}")
        logger.info(f"Prediction results available: {prediction_results is not None}")
        logger.info(f"Run type: {'Monthly' if is_monthly_update else 'Weekly'}")
        
        if prediction_results:
            predictions = prediction_results.get("predictions", [])
            metrics = prediction_results.get("model_metrics", {})
            
            logger.info(f"Number of predictions: {len(predictions)}")
            logger.info(f"Model metrics: {metrics}")
            
            # Create email content
            if is_monthly_update:
                data_source = "fresh Yahoo Finance data" if force_update_success else "existing data (fallback)"
                run_type = "Monthly Update"
            else:
                data_source = "existing data"
                run_type = "Weekly Prediction"
            
            logger.info(f"STEP 2: Preparing email with data source: {data_source}")
            
            email_content = f"""
            <h2>NOG {run_type} Results</h2>
            <p><strong>Run Type:</strong> {run_type}</p>
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
            
            logger.info("STEP 3: Sending email...")
            
            # Send email using Airflow's built-in email functionality
            from airflow.utils.email import send_email
            
            subject = f'NOG {run_type} - {data_source} - {context["ds"]}'
            
            send_email(
                to=['ketaki.kolhatkar99@gmail.com'],
                subject=subject,
                html_content=email_content
            )
            
            logger.info("SUCCESS: Email sent successfully")
            
        else:
            logger.error("FAILED: No prediction results found for email")
            
    except Exception as e:
        logger.error(f"EXCEPTION in send_success_email: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise
    
    finally:
        logger.info("COMPLETED: send_success_email task")

# Define tasks
force_data_update_task = PythonOperator(
    task_id='force_data_update',
    python_callable=force_data_update,
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

# Define task dependencies - ALWAYS run predictions, then email
force_data_update_task >> run_weekly_predictions_task >> send_email_task 