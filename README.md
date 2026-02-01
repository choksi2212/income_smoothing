# 💰 Income Smoothing Platform

A production-ready Indian fintech platform for freelancers and gig workers to smooth irregular income using ML-powered predictions and intelligent buffer management.

## 🎯 Features

### Core Functionality
- **ML-Powered Predictions** - ARIMA, Prophet, and Rolling Mean models for income forecasting
- **Income Smoothing** - Intelligent buffer management for stable cash flow
- **AI Insights** - Personalized recommendations based on income patterns
- **Manual Data Entry** - Add transactions without bank connections
- **Income Analysis** - Detailed breakdown of income sources and stability

### Technical Highlights
- ✅ 312 pre-trained ML models (19-25x faster predictions)
- ✅ Real-time income smoothing calculations
- ✅ Comprehensive API with 31+ endpoints
- ✅ Responsive React frontend with dark/light mode
- ✅ PostgreSQL database with 13 tables
- ✅ JWT authentication with bcrypt
- ✅ 35/35 tests passing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/choksi2212/income_smoothing.git
cd income_smoothing
```

2. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python scripts/init_db.py

# Generate test data (optional)
python scripts/generate_test_data.py
```

3. **Frontend Setup**
```bash
cd frontend
npm install
cd ..
```

4. **Run the Application**

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Manual:**
```bash
# Terminal 1 - Backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Access
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Test Credentials
- **Email:** testuser1@example.com
- **Password:** TestPass123

## 📊 Architecture

### Backend (FastAPI + PostgreSQL)
```
app/
├── routers/          # API endpoints
│   ├── auth.py       # Authentication
│   ├── predictions.py # ML predictions
│   ├── insights.py   # AI insights
│   ├── transactions.py # Transactions
│   ├── smoothing.py  # Income smoothing
│   ├── features.py   # ML features
│   └── manual_entry.py # Manual data entry
├── models.py         # Database models (13 tables)
├── schemas.py        # Pydantic schemas
├── ml_service.py     # Base ML service
├── ml_service_enhanced.py # Enhanced ML with pre-trained models
├── smoothing_service.py # Smoothing logic
└── main.py          # FastAPI app
```

### Frontend (React + TypeScript)
```
frontend/src/
├── pages/           # 6 pages
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Dashboard.tsx
│   ├── IncomeBreakdown.tsx
│   ├── IncomeSmoothing.tsx
│   ├── Insights.tsx
│   └── ManualEntry.tsx
├── components/      # Reusable components
├── services/        # API integration
└── store/          # State management
```

## 🎨 Features in Detail

### 1. ML-Powered Predictions
- **ARIMA:** Time-series forecasting for stable patterns
- **Prophet:** Complex patterns with seasonality
- **Rolling Mean:** Fast baseline predictions
- **Performance:** 0.13s per prediction (19x faster than real-time)

### 2. Income Smoothing
- Automatic buffer management
- Weekly release calculations
- Risk assessment
- Capacity monitoring

### 3. Manual Data Entry
- Add transactions manually
- Bulk CSV import
- Bank account management
- Trigger ML analysis

### 4. AI Insights
- Income stability scoring
- Trend detection
- Anomaly alerts
- Personalized recommendations

## 📚 Documentation

- [Complete Setup Guide](COMPLETE_SETUP_GUIDE.md)
- [Frontend Documentation](FRONTEND_COMPLETE.md)
- [ML Training Report](ML_TRAINING_VALIDATION_REPORT.md)
- [Manual Entry Feature](MANUAL_ENTRY_FEATURE.md)
- [API Documentation](http://localhost:8000/docs)

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_ml_service.py -v

# Test enhanced ML service
python scripts/test_enhanced_ml.py
```

**Test Results:** 35/35 passing ✅

## 🔐 Security

- JWT authentication with bcrypt
- SQL injection prevention (ORM)
- CORS configuration
- Environment variable protection
- Input validation (Pydantic)
- Account number encryption

## 📈 Performance

- **Prediction Speed:** 0.13s (vs 2.5s real-time)
- **Throughput:** 7.74 predictions/second
- **API Response:** < 200ms average
- **Database:** Optimized queries with indexes
- **Frontend:** < 2s load time

## 🛠️ Tech Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic V2
- statsmodels (ARIMA)
- fbprophet
- scikit-learn
- pandas, numpy

### Frontend
- React 18
- TypeScript
- Vite
- Recharts
- Framer Motion
- Axios
- Zustand

## 📊 Database Schema

13 tables including:
- users
- bank_accounts
- transactions
- ai_features
- cashflow_predictions
- income_sources
- smoothing_buffers
- weekly_releases
- ai_insights

## 🚀 Deployment

### Docker (Coming Soon)
```bash
docker-compose up -d
```

### Manual Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Run database migrations
4. Build frontend: `cd frontend && npm run build`
5. Start backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Serve frontend build

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 👥 Authors

- Tejas Choksi - [GitHub](https://github.com/choksi2212)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Facebook Prophet for time-series forecasting
- statsmodels for ARIMA implementation
- React team for the frontend library

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/choksi2212/income_smoothing/issues)
- Email: [Your email]

## 🎯 Roadmap

### Short Term
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Additional ML models
- [ ] Mobile app

### Long Term
- [ ] Bank API integration
- [ ] Multi-currency support
- [ ] Advanced analytics
- [ ] Tax optimization

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** February 2026

Made with ❤️ for Indian freelancers and gig workers
