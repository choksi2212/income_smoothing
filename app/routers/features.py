from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, AIFeature, IncomeSource
from app.schemas import AIFeatureResponse, IncomeSourceResponse
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[AIFeatureResponse])
def get_features(
    weeks: int = Query(12, ge=1, le=52),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI features for current user"""
    features = db.query(AIFeature).filter(
        AIFeature.user_id == current_user.user_id
    ).order_by(AIFeature.week_start_date.desc()).limit(weeks).all()
    
    return features


@router.get("/income-sources", response_model=List[IncomeSourceResponse])
def get_income_sources(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get income sources for current user"""
    sources = db.query(IncomeSource).filter(
        IncomeSource.user_id == current_user.user_id
    ).order_by(IncomeSource.contribution_pct.desc()).all()
    
    return sources
