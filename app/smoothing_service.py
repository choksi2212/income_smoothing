from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from app.models import SmoothingBuffer, WeeklyRelease, Transaction, TransactionType
from app.ml_service import MLService
import numpy as np


class SmoothingService:
    """Income smoothing logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ml_service = MLService(db)
    
    def initialize_buffer(self, user_id: str) -> SmoothingBuffer:
        """
        Create smoothing buffer for new user
        """
        existing = self.db.query(SmoothingBuffer).filter(
            SmoothingBuffer.user_id == user_id
        ).first()
        
        if existing:
            return existing
        
        buffer = SmoothingBuffer(
            user_id=user_id,
            buffer_balance_inr=Decimal('0'),
            total_deposited_inr=Decimal('0'),
            total_released_inr=Decimal('0'),
            buffer_risk_score=Decimal('0.5'),
            min_buffer_threshold_inr=Decimal('5000'),
            max_buffer_capacity_inr=Decimal('100000')
        )
        
        self.db.add(buffer)
        self.db.commit()
        self.db.refresh(buffer)
        
        return buffer
    
    def deposit_to_buffer(self, user_id: str, amount: Decimal) -> SmoothingBuffer:
        """
        Deposit excess income to buffer
        """
        buffer = self.db.query(SmoothingBuffer).filter(
            SmoothingBuffer.user_id == user_id
        ).first()
        
        if not buffer:
            buffer = self.initialize_buffer(user_id)
        
        # Check capacity
        if buffer.buffer_balance_inr + amount > buffer.max_buffer_capacity_inr:
            amount = buffer.max_buffer_capacity_inr - buffer.buffer_balance_inr
        
        buffer.buffer_balance_inr += amount
        buffer.total_deposited_inr += amount
        buffer.last_deposit_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(buffer)
        
        return buffer
    
    def calculate_weekly_release(self, user_id: str) -> Dict:
        """
        Calculate recommended weekly release amount
        
        Rules:
        - Based on worst-case predicted income
        - Considers buffer health
        - No negative buffer allowed
        - Conservative approach
        """
        buffer = self.db.query(SmoothingBuffer).filter(
            SmoothingBuffer.user_id == user_id
        ).first()
        
        if not buffer:
            buffer = self.initialize_buffer(user_id)
        
        # Get 7-day prediction
        prediction = self.ml_service.predict_cashflow(user_id, 7)
        worst_case_income = max(0, prediction['lower_bound'])
        
        # Get recent income average
        from app.models import AIFeature
        features = self.db.query(AIFeature).filter(
            AIFeature.user_id == user_id
        ).order_by(AIFeature.week_start_date.desc()).limit(4).all()
        
        if features:
            avg_weekly_income = np.mean([float(f.total_income_inr) for f in features])
        else:
            avg_weekly_income = 15000  # Default
        
        # Buffer health factor
        buffer_balance = float(buffer.buffer_balance_inr)
        min_threshold = float(buffer.min_buffer_threshold_inr)
        
        if buffer_balance < min_threshold:
            buffer_health = buffer_balance / min_threshold
        else:
            buffer_health = 1.0
        
        # Calculate release
        # Base: average of worst-case and average income
        base_release = (worst_case_income + avg_weekly_income) / 2
        
        # Adjust by buffer health
        recommended_release = base_release * buffer_health
        
        # Ensure we don't deplete buffer
        max_safe_release = buffer_balance * 0.8  # Keep 20% reserve
        recommended_release = min(recommended_release, max_safe_release)
        
        # Calculate buffer risk
        if buffer_balance < min_threshold * 0.5:
            risk_score = 0.9
        elif buffer_balance < min_threshold:
            risk_score = 0.6
        elif buffer_balance < min_threshold * 2:
            risk_score = 0.3
        else:
            risk_score = 0.1
        
        buffer.buffer_risk_score = Decimal(str(risk_score))
        self.db.commit()
        
        return {
            'recommended_weekly_release_inr': round(recommended_release, 2),
            'buffer_balance_inr': buffer_balance,
            'buffer_health': buffer_health,
            'buffer_risk_score': risk_score,
            'worst_case_income': worst_case_income,
            'avg_weekly_income': avg_weekly_income,
            'explanation': f"Based on worst-case income ₹{worst_case_income:.0f} and buffer health {buffer_health:.0%}"
        }
    
    def create_weekly_release(self, user_id: str) -> WeeklyRelease:
        """
        Create weekly release record
        """
        buffer = self.db.query(SmoothingBuffer).filter(
            SmoothingBuffer.user_id == user_id
        ).first()
        
        if not buffer:
            buffer = self.initialize_buffer(user_id)
        
        release_calc = self.calculate_weekly_release(user_id)
        
        # Get week start (Monday)
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if release already exists for this week
        existing = self.db.query(WeeklyRelease).filter(
            WeeklyRelease.user_id == user_id,
            WeeklyRelease.week_start_date == week_start
        ).first()
        
        if existing:
            return existing
        
        recommended = Decimal(str(release_calc['recommended_weekly_release_inr']))
        
        release = WeeklyRelease(
            user_id=user_id,
            week_start_date=week_start,
            recommended_weekly_release_inr=recommended,
            actual_release_inr=Decimal('0'),
            buffer_balance_before_inr=buffer.buffer_balance_inr,
            buffer_balance_after_inr=buffer.buffer_balance_inr,
            is_released=False
        )
        
        self.db.add(release)
        self.db.commit()
        self.db.refresh(release)
        
        return release
    
    def execute_weekly_release(self, user_id: str, release_id: str) -> WeeklyRelease:
        """
        Execute the weekly release
        """
        release = self.db.query(WeeklyRelease).filter(
            WeeklyRelease.release_id == release_id,
            WeeklyRelease.user_id == user_id
        ).first()
        
        if not release:
            raise ValueError("Release not found")
        
        if release.is_released:
            raise ValueError("Release already executed")
        
        buffer = self.db.query(SmoothingBuffer).filter(
            SmoothingBuffer.user_id == user_id
        ).first()
        
        if not buffer:
            raise ValueError("Buffer not found")
        
        # Check sufficient balance
        if buffer.buffer_balance_inr < release.recommended_weekly_release_inr:
            actual_release = buffer.buffer_balance_inr
        else:
            actual_release = release.recommended_weekly_release_inr
        
        # Update buffer
        buffer.buffer_balance_inr -= actual_release
        buffer.total_released_inr += actual_release
        buffer.last_release_date = datetime.utcnow()
        
        # Update release
        release.actual_release_inr = actual_release
        release.buffer_balance_after_inr = buffer.buffer_balance_inr
        release.is_released = True
        release.released_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(release)
        
        return release
    
    def process_income_smoothing(self, user_id: str) -> Dict:
        """
        Main smoothing logic:
        1. Analyze recent income
        2. Determine excess vs deficit
        3. Adjust buffer
        4. Calculate releases
        """
        # Get recent transactions
        from app.models import AIFeature
        features = self.db.query(AIFeature).filter(
            AIFeature.user_id == user_id
        ).order_by(AIFeature.week_start_date.desc()).limit(4).all()
        
        if not features:
            return {
                'status': 'insufficient_data',
                'message': 'Need more transaction history'
            }
        
        latest = features[0]
        avg_income = np.mean([float(f.total_income_inr) for f in features])
        
        # Determine if excess or deficit
        current_income = float(latest.total_income_inr)
        
        if current_income > avg_income * 1.2:
            # Excess income - deposit to buffer
            excess = Decimal(str(current_income - avg_income))
            buffer = self.deposit_to_buffer(user_id, excess)
            
            return {
                'status': 'excess_deposited',
                'amount_deposited': float(excess),
                'buffer_balance': float(buffer.buffer_balance_inr),
                'message': f'Deposited ₹{float(excess):.0f} excess income to buffer'
            }
        
        elif current_income < avg_income * 0.8:
            # Deficit - may need buffer draw
            deficit = Decimal(str(avg_income - current_income))
            
            buffer = self.db.query(SmoothingBuffer).filter(
                SmoothingBuffer.user_id == user_id
            ).first()
            
            if buffer and buffer.buffer_balance_inr >= deficit:
                return {
                    'status': 'deficit_covered',
                    'deficit_amount': float(deficit),
                    'buffer_balance': float(buffer.buffer_balance_inr),
                    'message': f'Buffer can cover ₹{float(deficit):.0f} deficit'
                }
            else:
                return {
                    'status': 'deficit_warning',
                    'deficit_amount': float(deficit),
                    'buffer_balance': float(buffer.buffer_balance_inr) if buffer else 0,
                    'message': 'Insufficient buffer to cover deficit'
                }
        
        else:
            # Normal income
            return {
                'status': 'normal',
                'message': 'Income within normal range'
            }
