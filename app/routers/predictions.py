from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, CashflowPrediction
from app.schemas import CashflowPredictionResponse, SafeToSpendResponse
from app.auth import get_current_active_user
from app.ml_service_enhanced import EnhancedMLService
from decimal import Decimal

router = APIRouter()


@router.post("/generate")
def generate_predictions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate cashflow predictions for 7, 30, 60 days using pre-trained models"""
    ml_service = EnhancedMLService(db)
    
    predictions = []
    for days in [7, 30, 60]:
        pred = ml_service.save_prediction(str(current_user.user_id), days)
        predictions.append(pred)
    
    return {
        "status": "success",
        "predictions_generated": len(predictions)
    }


@router.get("/", response_model=List[CashflowPredictionResponse])
def get_predictions(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recent predictions"""
    predictions = db.query(CashflowPrediction).filter(
        CashflowPrediction.user_id == current_user.user_id
    ).order_by(CashflowPrediction.created_at.desc()).limit(limit).all()
    
    return predictions


@router.get("/safe-to-spend", response_model=SafeToSpendResponse)
def get_safe_to_spend(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate safe-to-spend limits using enhanced ML service"""
    ml_service = EnhancedMLService(db)
    
    safe_spend = ml_service.calculate_safe_to_spend(str(current_user.user_id))
    
    return SafeToSpendResponse(
        daily_safe_spend_inr=Decimal(str(safe_spend['daily_safe_spend_inr'])),
        weekly_safe_spend_inr=Decimal(str(safe_spend['weekly_safe_spend_inr'])),
        predicted_cash_exhaustion_date=safe_spend['predicted_cash_exhaustion_date'],
        buffer_balance_inr=Decimal(str(safe_spend['buffer_balance_inr'])),
        worst_case_income_7d=Decimal(str(safe_spend['worst_case_income_7d'])),
        fixed_expenses_weekly=Decimal(str(safe_spend['fixed_expenses_weekly'])),
        volatility_multiplier=Decimal(str(safe_spend['volatility_multiplier'])),
        explanation=safe_spend['explanation']
    )


@router.get("/model-info")
def get_model_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get information about available pre-trained models for current user"""
    ml_service = EnhancedMLService(db)
    
    model_info = ml_service.get_model_info(str(current_user.user_id))
    
    return model_info
