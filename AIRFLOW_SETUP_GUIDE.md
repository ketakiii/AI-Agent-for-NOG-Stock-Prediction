# Airflow Setup and Usage Guide

## 🚀 Quick Start

### 1. Start Docker Desktop
- Open Docker Desktop on your Mac
- Wait for it to fully start (green icon in menu bar)

### 2. Start Airflow
```bash
cd airflow
docker-compose up -d
```

### 3. Access Airflow UI
- **URL**: http://localhost:8080
- **Username**: `admin`
- **Password**: `admin`

## 📋 Airflow Commands

### Start/Stop Airflow
```bash
# Start Airflow
docker-compose up -d

# Stop Airflow
docker-compose down

# Restart Airflow
docker-compose down && docker-compose up -d

# View logs
docker-compose logs scheduler
docker-compose logs webserver
```

### Check Status
```bash
# Check if containers are running
docker-compose ps

# Check DAG loading
docker-compose logs scheduler | grep "nog_weekly_prediction"
```

## 🎯 Running Your DAGs

### **Production Pipeline** (`nog_production_pipeline`)
**Purpose**: Weekly production runs with smart fallback
**Schedule**: Every Monday at 9 AM (automatic)
**Logic**: 
1. Force data update (try fresh data from Yahoo Finance)
2. If force update fails → Run weekly predictions with existing data
3. Send email with results from either path

### **Testing Pipeline** (`nog_testing_pipeline`)
**Purpose**: Manual testing with existing data
**Schedule**: Manual trigger only
**Logic**: Run predictions with existing data (fast, no API calls)

### Method 1: Airflow UI (Recommended)
1. Go to http://localhost:8080
2. Choose your DAG:
   - **Production**: `nog_production_pipeline` (automatic weekly)
   - **Testing**: `nog_testing_pipeline` (manual trigger)
3. Click **"Trigger DAG"** button

### Method 2: Command Line
```bash
# Test pipeline (existing data, fast)
docker-compose exec webserver airflow dags trigger nog_testing_pipeline

# Production pipeline (try fresh, fallback to existing)
docker-compose exec webserver airflow dags trigger nog_production_pipeline
```

## 🔧 Troubleshooting

### DAG Not Visible
```bash
# Check if DAG loaded successfully
docker-compose logs scheduler | grep "nog_weekly_prediction"

# Check for import errors
docker-compose exec webserver python -c "import sys; sys.path.append('/opt/airflow/project'); from src.models.weekly_predict import WeeklyPredictionPipeline; print('✅ Import successful')"
```

### Tasks Failing
```bash
# Check task logs
docker-compose logs scheduler | tail -50

# Check webserver logs
docker-compose logs webserver | tail -50
```

### Rebuild with Code Changes
```bash
# If you modify the DAG or dependencies
docker-compose down
docker-compose up -d --build
```

## 📁 File Structure
```
airflow/
├── docker-compose.yaml    # Airflow configuration
├── Dockerfile            # Custom image with dependencies
├── requirements.txt      # Python packages
└── dags/
    └── nog_weekly_prediction_dag.py  # Your DAG
```

## 🎯 Common Use Cases

### Daily Testing (Use existing data)
1. Trigger DAG with: `{"update_data": false}`
2. Fast execution, no API rate limits

### Weekly Production Run (Fresh data)
1. Trigger DAG with: `{"update_data": true}`
2. Gets latest data from Yahoo Finance
3. May take longer due to API calls

### Force Data Update Only
1. Go to DAG graph view
2. Click on `force_data_update` task
3. Click "Trigger Task"
4. Only updates data, doesn't run predictions

## 🔄 DAG Schedule
- **Schedule**: Every Monday at 9 AM (`0 9 * * 1`)
- **Manual trigger**: Available anytime
- **Configuration**: JSON parameters for data update control

## 📊 Monitoring
- **DAG Status**: Green = success, Red = failed
- **Task Logs**: Click on individual tasks to see detailed logs
- **XCom**: Stores results between tasks
- **Email Notifications**: Sent on completion (configure email in DAG)

## 🛠️ Development Workflow

### 1. Make Code Changes
- Edit your Python files in the main project
- Changes are automatically available in Airflow (volume mount)

### 2. Test Changes
```bash
# Test locally first
python test_simple.py

# Then test in Airflow
# Trigger DAG with {"update_data": false}
```

### 3. Deploy
- No deployment needed - changes are live immediately
- Just restart Airflow if you modify DAG structure

## 🚨 Important Notes

### Yahoo Finance Rate Limits
- Use `update_data: false` for frequent testing
- Use `update_data: true` only for weekly production runs
- Yahoo may block requests if called too frequently

### Data Persistence
- Predictions saved to: `data/weekly_predictions.json`
- Performance metrics: `data/model_performance.json`
- Model file: `saved_models/xgb_model.pkl`

### Email Configuration
- Update email address in DAG file
- Currently set to: `your-email@example.com`

## 🎉 Success Indicators
- ✅ DAG visible in Airflow UI
- ✅ Tasks complete with green status
- ✅ Predictions generated and saved
- ✅ Email notification received
- ✅ Logs show successful execution

## 📞 Quick Reference

| Action | Command |
|--------|---------|
| Start Airflow | `docker-compose up -d` |
| Stop Airflow | `docker-compose down` |
| Check status | `docker-compose ps` |
| View logs | `docker-compose logs scheduler` |
| Test import | `docker-compose exec webserver python -c "import sys; sys.path.append('/opt/airflow/project'); from src.models.weekly_predict import WeeklyPredictionPipeline; print('✅ Import successful')"` |
| **Test Pipeline** (existing data) | `docker-compose exec webserver airflow dags trigger nog_testing_pipeline` |
| **Production Pipeline** (smart fallback) | `docker-compose exec webserver airflow dags trigger nog_production_pipeline` |

---
**Last Updated**: July 19, 2025
**Version**: 1.0 