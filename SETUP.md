# Setup Guide

## Prerequisites

1. **PostgreSQL** must be installed and running
2. **Python 3.11+** installed
3. **pip** package manager

## Step 1: Configure Database

1. Open `.env` file
2. Update the `DATABASE_URL` with your PostgreSQL credentials:

```
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/income_smoothing
```

Replace:
- `YOUR_USERNAME` with your PostgreSQL username (default: `postgres`)
- `YOUR_PASSWORD` with your PostgreSQL password

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Initialize Database

```bash
python scripts/init_db.py
```

This will:
- Create the `income_smoothing` database
- Create all required tables

## Step 4: Generate Test Data

```bash
python scripts/generate_test_data.py
```

This will create 3 test users with 6 months of realistic Indian transaction data.

## Step 5: Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## Step 6: Run Tests

```bash
pytest tests/ -v
```

## Test User Credentials

After running `generate_test_data.py`, you'll have 3 test users:

1. **Email:** testuser1@example.com  
   **Password:** TestPass123!  
   **Pattern:** stable

2. **Email:** testuser2@example.com  
   **Password:** TestPass123!  
   **Pattern:** moderate

3. **Email:** testuser3@example.com  
   **Password:** TestPass123!  
   **Pattern:** volatile

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user info

### Transactions
- `POST /transactions/bank-accounts` - Create bank account
- `GET /transactions/bank-accounts` - Get bank accounts
- `POST /transactions/` - Create transaction
- `GET /transactions/` - Get transactions
- `POST /transactions/sync` - Sync and analyze transactions

### Predictions
- `POST /predictions/generate` - Generate cashflow predictions
- `GET /predictions/` - Get predictions
- `GET /predictions/safe-to-spend` - Get safe-to-spend limits

### Features
- `GET /features/` - Get AI features
- `GET /features/income-sources` - Get income sources

### Smoothing
- `GET /smoothing/buffer` - Get buffer status
- `GET /smoothing/weekly-releases` - Get release history
- `POST /smoothing/calculate-release` - Calculate weekly release
- `POST /smoothing/create-release` - Create release record
- `POST /smoothing/execute-release/{release_id}` - Execute release
- `POST /smoothing/process` - Process income smoothing

### Insights
- `GET /insights/` - Get AI insights
- `POST /insights/generate` - Generate insights
- `GET /insights/stability-score` - Get stability score
- `PATCH /insights/{insight_id}/read` - Mark insight as read
- `PATCH /insights/{insight_id}/dismiss` - Dismiss insight

## Troubleshooting

### Database Connection Error

If you get "password authentication failed":
1. Verify PostgreSQL is running
2. Check your password in `.env`
3. Try connecting manually: `psql -U postgres`

### Port Already in Use

If port 8000 is in use:
```bash
uvicorn app.main:app --reload --port 8001
```

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```
