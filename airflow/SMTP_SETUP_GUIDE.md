# 📧 SMTP Setup Guide for Airflow Email Notifications

## 🚨 **SECURITY WARNING**
**NEVER commit .env files containing passwords to git!** Always add them to .gitignore.

## 🎯 Overview
This guide will help you configure Gmail SMTP for Airflow email notifications so you can receive prediction results via email.

## 🔧 Step 1: Generate Gmail App Password

### Why App Password?
Gmail requires an "App Password" for third-party applications like Airflow to send emails securely.

### How to Generate:
1. **Go to your Google Account**: https://myaccount.google.com/
2. **Navigate to Security**: Click "Security" in the left sidebar
3. **Enable 2-Step Verification** (if not already enabled):
   - Click "2-Step Verification"
   - Follow the setup process
4. **Generate App Password**:
   - Go back to Security
   - Click "2-Step Verification" again
   - Scroll down to "App passwords"
   - Click "App passwords"
   - Select "Mail" and "Other (Custom name)"
   - Name it "Airflow NOG Predictions"
   - Click "Generate"
   - **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

## 🔧 Step 2: Update Environment File

1. **Open the `.env` file** in the `airflow/` directory
2. **Replace the placeholder** with your actual app password:

```bash
# Current content:
GMAIL_APP_PASSWORD=your_gmail_app_password_here

# Replace with your actual password (remove spaces):
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

## 🔧 Step 3: Restart Airflow

```bash
# Stop Airflow
docker-compose down

# Start Airflow with new SMTP config
docker-compose up -d
```

## 🔧 Step 4: Test Email Configuration

### Test via Airflow CLI:
```bash
# Test SMTP connection
docker-compose exec webserver airflow config get-value smtp smtp_host
docker-compose exec webserver airflow config get-value smtp smtp_user
```

### Test via DAG:
```bash
# Trigger the testing pipeline to test email
docker-compose exec webserver airflow dags trigger nog_testing_pipeline
```

## 🔧 Step 5: Verify Email Delivery

1. **Check your email** (ketaki.kolhatkar99@gmail.com)
2. **Check spam folder** if not in inbox
3. **Check Airflow logs** for email status

## 🚨 Troubleshooting

### Common Issues:

#### 1. "Authentication failed"
- **Solution**: Double-check your app password
- **Make sure**: 2-Step Verification is enabled
- **Verify**: App password is for "Mail" service

#### 2. "Connection refused"
- **Solution**: Check if port 587 is blocked
- **Alternative**: Try port 465 with SSL

#### 3. "Email not received"
- **Check**: Spam/junk folder
- **Verify**: Email address is correct
- **Test**: Send a test email manually

### Alternative SMTP Providers:

#### Outlook/Hotmail:
```yaml
AIRFLOW__SMTP__SMTP_HOST: smtp-mail.outlook.com
AIRFLOW__SMTP__SMTP_PORT: 587
```

#### Yahoo:
```yaml
AIRFLOW__SMTP__SMTP_HOST: smtp.mail.yahoo.com
AIRFLOW__SMTP__SMTP_PORT: 587
```

## 📋 Current Configuration

Your current SMTP settings in `docker-compose.yaml`:

```yaml
# SMTP Configuration for Gmail
AIRFLOW__SMTP__SMTP_HOST: smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT: 587
AIRFLOW__SMTP__SMTP_USER: ketaki.kolhatkar99@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD: ${GMAIL_APP_PASSWORD}
AIRFLOW__SMTP__SMTP_MAIL_FROM: ketaki.kolhatkar99@gmail.com
AIRFLOW__SMTP__SMTP_STARTTLS: 'true'
AIRFLOW__SMTP__SMTP_SSL: 'false'
```

## ✅ Success Indicators

When SMTP is configured correctly, you should see:
- ✅ Email tasks complete successfully (green in Airflow UI)
- ✅ Receive prediction results in your email
- ✅ No "SMTP connection refused" errors in logs

## 🔒 Security Notes

### 🚨 **CRITICAL SECURITY WARNING**
**NEVER commit your `.env` file to git!** It contains your Gmail app password.

**What to do:**
- ✅ **ALWAYS** add `.env` files to `.gitignore`
- ✅ **NEVER** commit files containing passwords or API keys
- ✅ **ROTATE** app passwords immediately if accidentally exposed
- ❌ **NEVER** share .env files in code repositories
- ❌ **NEVER** include real credentials in documentation

**If you accidentally commit sensitive data:**
1. **IMMEDIATELY** revoke the exposed app password in Google Account
2. **GENERATE** a new app password
3. **REMOVE** the file from git history using `git filter-branch`
4. **FORCE PUSH** to update remote repository

**Best Practices:**
- **Use app passwords** instead of your main Gmail password
- **Rotate app passwords** periodically for security
- **Monitor** email sending for unusual activity
- **Keep** `.env` files local only

---

**Need help?** Check the Airflow logs or try the troubleshooting steps above! 