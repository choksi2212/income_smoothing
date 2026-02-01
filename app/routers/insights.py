from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, AIInsight
from app.schemas import AIInsightResponse
from app.auth import get_current_active_user
from app.ml_service_enhanced import EnhancedMLService
from decimal import Decimal

router = APIRouter()


@router.get("/", response_model=List[AIInsightResponse])
def get_insights(
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI insights for current user"""
    query = db.query(AIInsight).filter(
        AIInsight.user_id == current_user.user_id,
        AIInsight.is_dismissed == False
    )
    
    if unread_only:
        query = query.filter(AIInsight.is_read == False)
    
    insights = query.order_by(AIInsight.created_at.desc()).limit(20).all()
    
    return insights


@router.post("/generate")
def generate_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate new insights using enhanced ML service"""
    ml_service = EnhancedMLService(db)
    
    insights = ml_service.generate_insights(str(current_user.user_id))
    
    return {
        "status": "success",
        "insights_generated": len(insights)
    }


@router.patch("/{insight_id}/read")
def mark_insight_read(
    insight_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark insight as read"""
    insight = db.query(AIInsight).filter(
        AIInsight.insight_id == insight_id,
        AIInsight.user_id == current_user.user_id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_read = True
    db.commit()
    
    return {"status": "success"}


@router.patch("/{insight_id}/dismiss")
def dismiss_insight(
    insight_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Dismiss insight"""
    insight = db.query(AIInsight).filter(
        AIInsight.insight_id == insight_id,
        AIInsight.user_id == current_user.user_id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_dismissed = True
    db.commit()
    
    return {"status": "success"}


@router.get("/stability-score")
def get_stability_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get income stability score using enhanced ML service"""
    ml_service = EnhancedMLService(db)
    
    score = ml_service.calculate_income_stability_score(str(current_user.user_id))
    
    return {
        "stability_score": float(score),
        "interpretation": "High" if score > 0.7 else "Medium" if score > 0.4 else "Low"
    }
