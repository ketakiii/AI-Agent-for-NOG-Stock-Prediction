from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from src.data.data_pipeline import run_data_pipeline
from src.models.xgb import train_model, save_model, load_model, predict

default_args = {
    'owner':'airflow',
    'start_date':datetime(2025, 5, 18),
    'retries':1
}

def predict_nog():
    """
    Predict stock prices using trained model
    """
    model = load_model()
    fetchdata = run_data_pipeline(csvflag=False)
    preds = predict(model, fetchdata)
    print(preds)

with DAG('nog_dag', default_args=default_args, schedule_interval='@daily') as dag:
    t1 = PythonOperator(task_id='run_pipeline', python_callable=run_data_pipeline)
    t2 = PythonOperator(task_id='load_model', python_callable=load_model)
    t3 = PythonOperator(task_id='predict', python_callable=predict_nog)

    t1 >> t2 >> t3


