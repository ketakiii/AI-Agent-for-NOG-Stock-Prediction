FROM apache/airflow:2.9.1

# Install additional Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install additional packages that might be missing
RUN pip install --no-cache-dir joblib xgboost scikit-learn 