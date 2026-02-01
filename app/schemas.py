from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.models import TransactionType, MerchantCategory, RiskLevel, InsightType, InsightSeverity


# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    phone: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: UUID
    email: str
    full_name: str
    phone: Optional[str]
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Transaction Schemas
class TransactionCreate(BaseModel):
    account_id: UUID
    txn_timestamp: datetime
    amount_inr: Decimal
    txn_type: TransactionType
    balance_after_txn: Decimal
    description: str
    merchant_category: MerchantCategory


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    transaction_id: UUID
    user_id: UUID
    account_id: UUID
    txn_timestamp: datetime
    amount_inr: Decimal
    txn_type: TransactionType
    balance_after_txn: Decimal
    description: str
    merchant_category: MerchantCategory
    is_income: bool
    created_at: datetime


# Bank Account Schemas
class BankAccountCreate(BaseModel):
    account_number: str
    bank_name: str
    account_type: str = "savings"
    is_primary: bool = False


class BankAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    account_id: UUID
    user_id: UUID
    bank_name: str
    account_type: str
    is_primary: bool
    current_balance_inr: Decimal
    last_synced_at: Optional[datetime]
    created_at: datetime


# Income Source Schemas
class IncomeSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    source_id: UUID
    source_name: str
    source_category: str
    avg_monthly_inr: Decimal
    contribution_pct: Decimal
    stability_score: Decimal
    last_payment_date: Optional[datetime]


# AI Feature Schemas
class AIFeatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    feature_id: UUID
    user_id: UUID
    week_start_date: datetime
    total_income_inr: Decimal
    total_expense_inr: Decimal
    net_cashflow_inr: Decimal
    avg_daily_income: Decimal
    income_std_dev: Decimal
    income_volatility_ratio: Decimal
    days_with_income: int
    days_without_income: int
    income_source_count: int
    top_income_source_pct: Decimal
    avg_daily_expense: Decimal
    expense_std_dev: Decimal
    buffer_utilization_rate: Decimal
    overspend_events_count: int
    created_at: datetime


# Cashflow Prediction Schemas
class CashflowPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    prediction_id: UUID
    user_id: UUID
    prediction_date: datetime
    prediction_window_days: int
    expected_inflow_inr: Decimal
    expected_outflow_inr: Decimal
    net_cashflow_inr: Decimal
    lower_bound_inr: Decimal
    upper_bound_inr: Decimal
    risk_level: RiskLevel
    model_used: str
    confidence_score: Decimal
    created_at: datetime


# Smoothing Buffer Schemas
class SmoothingBufferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    buffer_id: UUID
    user_id: UUID
    buffer_balance_inr: Decimal
    total_deposited_inr: Decimal
    total_released_inr: Decimal
    buffer_risk_score: Decimal
    min_buffer_threshold_inr: Decimal
    max_buffer_capacity_inr: Decimal
    last_deposit_date: Optional[datetime]
    last_release_date: Optional[datetime]
    updated_at: datetime


# Weekly Release Schemas
class WeeklyReleaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    release_id: UUID
    user_id: UUID
    week_start_date: datetime
    recommended_weekly_release_inr: Decimal
    actual_release_inr: Decimal
    buffer_balance_before_inr: Decimal
    buffer_balance_after_inr: Decimal
    is_released: bool
    released_at: Optional[datetime]
    created_at: datetime


# AI Insight Schemas
class AIInsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    insight_id: UUID
    user_id: UUID
    insight_type: InsightType
    severity: InsightSeverity
    explanation_text: str
    supporting_metrics: Dict[str, Any]
    is_read: bool
    is_dismissed: bool
    created_at: datetime


# Dashboard Schemas
class DashboardResponse(BaseModel):
    daily_safe_spend_inr: Decimal
    weekly_safe_spend_inr: Decimal
    buffer_balance_inr: Decimal
    risk_level: RiskLevel
    predicted_cash_exhaustion_date: Optional[datetime]
    income_stability_score: Decimal
    next_7_days_prediction: CashflowPredictionResponse
    recent_insights: list[AIInsightResponse]


# Safe to Spend Schemas
class SafeToSpendResponse(BaseModel):
    daily_safe_spend_inr: Decimal
    weekly_safe_spend_inr: Decimal
    predicted_cash_exhaustion_date: Optional[datetime]
    buffer_balance_inr: Decimal
    worst_case_income_7d: Decimal
    fixed_expenses_weekly: Decimal
    volatility_multiplier: Decimal
    explanation: str
