from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, transactions, features, predictions, smoothing, insights, manual_entry

app = FastAPI(
    title="Income Smoothing Platform API",
    description="Production-ready Indian fintech backend for income prediction and smoothing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(features.router, prefix="/features", tags=["Features"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(smoothing.router, prefix="/smoothing", tags=["Smoothing"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(manual_entry.router, prefix="/manual", tags=["Manual Entry"])


@app.get("/")
def root():
    return {
        "message": "Income Smoothing Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
