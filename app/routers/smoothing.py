from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, SmoothingBuffer, WeeklyRelease
from app.schemas import SmoothingBufferResponse, WeeklyReleaseResponse
from app.auth import get_current_active_user
from app.smoothing_service import SmoothingService

router = APIRouter()


@router.get("/buffer", response_model=SmoothingBufferResponse)
def get_buffer(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get smoothing buffer status"""
    buffer = db.query(SmoothingBuffer).filter(
        SmoothingBuffer.user_id == current_user.user_id
    ).first()
    
    if not buffer:
        smoothing_service = SmoothingService(db)
        buffer = smoothing_service.initialize_buffer(str(current_user.user_id))
    
    return buffer


@router.get("/weekly-releases", response_model=List[WeeklyReleaseResponse])
def get_weekly_releases(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get weekly release history"""
    releases = db.query(WeeklyRelease).filter(
        WeeklyRelease.user_id == current_user.user_id
    ).order_by(WeeklyRelease.week_start_date.desc()).limit(12).all()
    
    return releases


@router.post("/calculate-release")
def calculate_release(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate recommended weekly release"""
    smoothing_service = SmoothingService(db)
    
    release_calc = smoothing_service.calculate_weekly_release(str(current_user.user_id))
    
    return release_calc


@router.post("/create-release", response_model=WeeklyReleaseResponse)
def create_release(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create weekly release record"""
    smoothing_service = SmoothingService(db)
    
    release = smoothing_service.create_weekly_release(str(current_user.user_id))
    
    return release


@router.post("/execute-release/{release_id}", response_model=WeeklyReleaseResponse)
def execute_release(
    release_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Execute a weekly release"""
    smoothing_service = SmoothingService(db)
    
    try:
        release = smoothing_service.execute_weekly_release(
            str(current_user.user_id),
            release_id
        )
        return release
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/process")
def process_smoothing(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process income smoothing logic"""
    smoothing_service = SmoothingService(db)
    
    result = smoothing_service.process_income_smoothing(str(current_user.user_id))
    
    return result
