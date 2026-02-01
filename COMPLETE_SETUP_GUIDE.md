# Complete Setup Guide - Income Smoothing Platform

This guide will walk you through setting up the complete Income Smoothing Platform from scratch.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11+** installed
- ✅ **Node.js 18+** and npm installed
- ✅ **PostgreSQL 14+** installed and running
- ✅ **Git** installed (optional)

## Step-by-Step Setup

### Part 1: Backend Setup (15 minutes)

#### 1.1 Configure PostgreSQL

First, make sure PostgreSQL is running. Then update the `.env` file with your credentials:

```bash
# Open .env file and update:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/income_smoothing
```

Replace `YOUR_PASSWORD` with your actual PostgreSQL password.

#### 1.2 Install Python Dependencies

```bash
# From the project root directory
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI, Uvicorn
- PostgreSQL drivers
- ML libraries (pandas, numpy, scikit-learn, statsmodels, prophet)
- Authentication libraries

#### 1.3 Initialize Database

```bash
python scripts/init_db.py
```

Expected output:
```
Initializing database...
✓ Database 'income_smoothing' created successfully
✓ All tables created successfully
✓ Database initialization complete!
```

#### 1.4 Generate Test Data

```bash
python scripts/generate_test_data.py
```

This creates 3 test users with 6 months of realistic Indian transaction data.

Expected output:
```
Generating test users and data...

Creating user: testuser1@example.com
  Generating 6 months of transactions...
  Generated 559 transactions
  Extracting features...
  Updating income sources...
  Generating predictions...
  Generating insights...
  Initializing income smoothing...
✓ User testuser1@example.com created successfully

[... similar for testuser2 and testuser3 ...]

✓ Test data generation complete!
```

#### 1.5 Start Backend Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is now running!**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Part 2: Frontend Setup (10 minutes)

#### 2.1 Navigate to Frontend Directory

```bash
cd frontend
```

#### 2.2 Install Node Dependencies

```bash
npm install
```

This will install:
- React, React Router
- TypeScript
- Vite (build tool)
- Recharts (charts)
- Framer Motion (animations)
- Axios (API client)
- And more...

#### 2.3 Start Development Server

```bash
npm run dev
```

Expected output:
```
  VITE v5.0.11  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

✅ **Frontend is now running!**
- App: http://localhost:3000

### Part 3: Test the Application (5 minutes)

#### 3.1 Open the Application

Open your browser and navigate to: http://localhost:3000

#### 3.2 Login with Test Credentials

Use any of these test accounts:

**Stable Income Pattern:**
- Email: `testuser1@example.com`
- Password: `TestPass123`

**Moderate Income Pattern:**
- Email: `testuser2@example.com`
- Password: `TestPass123`

**Volatile Income Pattern:**
- Email: `testuser3@example.com`
- Password: `TestPass123`

#### 3.3 Explore the Features

1. **Dashboard** - View your financial overview
   - Daily & weekly safe-to-spend
   - Buffer balance
   - 7-day prediction
   - Cash flow chart

2. **Income Breakdown** - Analyze income sources
   - Pie chart of income distribution
   - Source stability indicators
   - Monthly averages

3. **Income Smoothing** - Manage your buffer
   - Buffer balance and capacity
   - Weekly release recommendations
   - Release history

4. **Insights** - AI-powered recommendations
   - Volatility warnings
   - Expense alerts
   - Positive trends

## Troubleshooting

### Backend Issues

**Problem: Database connection error**
```
psycopg2.OperationalError: password authentication failed
```

**Solution:**
1. Check PostgreSQL is running
2. Verify password in `.env` file
3. Try connecting manually: `psql -U postgres`

**Problem: Module not found**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**Problem: Port 3000 already in use**

**Solution:**
```bash
# Use a different port
npm run dev -- --port 3001
```

**Problem: API connection error**

**Solution:**
1. Ensure backend is running on port 8000
2. Check `frontend/vite.config.ts` proxy configuration
3. Clear browser cache

### General Issues

**Problem: CORS errors**

**Solution:**
The backend is configured to allow requests from `localhost:3000`. If you change the frontend port, update `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:YOUR_PORT"],
    ...
)
```

## Running Tests

### Backend Tests

```bash
# From project root
python -m pytest tests/ -v
```

### Frontend Tests

```bash
# From frontend directory
cd frontend
npm run test
```

## Building for Production

### Backend

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`.

To preview the production build:
```bash
npm run preview
```

## Next Steps

### 1. Generate More Data

To create more test users with more data:

Edit `scripts/generate_test_data.py` and change:
```python
test_users = generate_test_users(10)  # Create 10 users instead of 3
```

And in `app/data_generator.py`, change:
```python
transactions = generator.generate_transactions(
    str(user.user_id),
    str(account.account_id),
    months=12  # Generate 12 months instead of 6
)
```

### 2. Train ML Models

The ML models currently use real-time prediction. To train and save models:

1. Collect sufficient historical data (6+ months)
2. Train ARIMA models on user data
3. Save model artifacts using joblib
4. Load models for faster predictions

### 3. Security Hardening

For production deployment:

1. **Enable HTTPS**
2. **Add rate limiting**
3. **Implement CSRF protection**
4. **Add input sanitization**
5. **Enable security headers**
6. **Set up monitoring**
7. **Configure backups**

### 4. Deploy to Production

Options for deployment:

**Backend:**
- Heroku
- AWS (EC2, ECS, Lambda)
- Google Cloud Run
- DigitalOcean

**Frontend:**
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

**Database:**
- AWS RDS
- Google Cloud SQL
- Heroku Postgres
- DigitalOcean Managed Database

## Support

If you encounter any issues:

1. Check the logs in the terminal
2. Review the API documentation at http://localhost:8000/docs
3. Verify all prerequisites are installed
4. Ensure PostgreSQL is running
5. Check that ports 3000 and 8000 are available

## Summary

You now have a fully functional Income Smoothing Platform with:

✅ Backend API with ML-powered predictions
✅ PostgreSQL database with test data
✅ React frontend with responsive design
✅ Automatic dark/light mode
✅ Real-time charts and visualizations
✅ AI-powered insights
✅ Income smoothing calculations

The platform is ready for development, testing, and further customization!
