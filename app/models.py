from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text, Enum, Boolean, Index, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class MerchantCategory(str, enum.Enum):
    FREELANCING = "freelancing"
    PLATFORM_PAYOUT = "platform_payout"
    UPI_CREDIT = "upi_credit"
    RENT = "rent"
    FOOD_DELIVERY = "food_delivery"
    MOBILE_RECHARGE = "mobile_recharge"
    TRAVEL = "travel"
    UTILITIES = "utilities"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InsightType(str, enum.Enum):
    VOLATILITY_SPIKE = "volatility_spike"
    SOURCE_CONCENTRATION = "source_concentration"
    BUFFER_DRAW_FREQUENT = "buffer_draw_frequent"
    EXPENSE_CREEP = "expense_creep"
    LOW_INCOME_WARNING = "low_income_warning"
    POSITIVE_TREND = "positive_trend"


class InsightSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(15))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    bank_accounts = relationship("BankAccount", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    income_sources = relationship("IncomeSource", back_populates="user")
    ai_features = relationship("AIFeature", back_populates="user")
    cashflow_predictions = relationship("CashflowPrediction", back_populates="user")
    smoothing_buffer = relationship("SmoothingBuffer", back_populates="user", uselist=False)
    weekly_releases = relationship("WeeklyRelease", back_populates="user")
    ai_insights = relationship("AIInsight", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, unique=True)
    occupation = Column(String(100))
    primary_income_type = Column(String(100))
    monthly_fixed_expenses_inr = Column(Numeric(12, 2), default=0)
    risk_tolerance = Column(String(20), default="conservative")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="profile")


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    account_number_encrypted = Column(String(255), nullable=False)
    bank_name = Column(String(100), nullable=False)
    account_type = Column(String(50), default="savings")
    is_primary = Column(Boolean, default=False)
    current_balance_inr = Column(Numeric(12, 2), default=0)
    last_synced_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="bank_accounts")
    transactions = relationship("Transaction", back_populates="account")
    
    __table_args__ = (
        Index("idx_bank_accounts_user_id", "user_id"),
    )


class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.account_id"), nullable=False)
    txn_timestamp = Column(DateTime, nullable=False, index=True)
    amount_inr = Column(Numeric(12, 2), nullable=False)
    txn_type = Column(Enum(TransactionType), nullable=False)
    balance_after_txn = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=False)
    merchant_category = Column(Enum(MerchantCategory), nullable=False)
    is_income = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="transactions")
    account = relationship("BankAccount", back_populates="transactions")
    
    __table_args__ = (
        Index("idx_transactions_user_timestamp", "user_id", "txn_timestamp"),
        Index("idx_transactions_user_type", "user_id", "txn_type"),
    )


class IncomeSource(Base):
    __tablename__ = "income_sources"
    
    source_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    source_name = Column(String(100), nullable=False)
    source_category = Column(String(50), nullable=False)
    avg_monthly_inr = Column(Numeric(12, 2), default=0)
    contribution_pct = Column(Numeric(5, 2), default=0)
    stability_score = Column(Numeric(3, 2), default=0)
    last_payment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="income_sources")
    
    __table_args__ = (
        Index("idx_income_sources_user_id", "user_id"),
    )


class AIFeature(Base):
    __tablename__ = "ai_features"
    
    feature_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    week_start_date = Column(DateTime, nullable=False)
    total_income_inr = Column(Numeric(12, 2), default=0)
    total_expense_inr = Column(Numeric(12, 2), default=0)
    net_cashflow_inr = Column(Numeric(12, 2), default=0)
    avg_daily_income = Column(Numeric(12, 2), default=0)
    income_std_dev = Column(Numeric(12, 2), default=0)
    income_volatility_ratio = Column(Numeric(8, 4), default=0)
    days_with_income = Column(Integer, default=0)
    days_without_income = Column(Integer, default=0)
    income_source_count = Column(Integer, default=0)
    top_income_source_pct = Column(Numeric(5, 2), default=0)
    avg_daily_expense = Column(Numeric(12, 2), default=0)
    expense_std_dev = Column(Numeric(12, 2), default=0)
    buffer_utilization_rate = Column(Numeric(5, 2), default=0)
    overspend_events_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="ai_features")
    
    __table_args__ = (
        Index("idx_ai_features_user_week", "user_id", "week_start_date"),
    )


class CashflowPrediction(Base):
    __tablename__ = "cashflow_predictions"
    
    prediction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    prediction_window_days = Column(Integer, nullable=False)
    expected_inflow_inr = Column(Numeric(12, 2), nullable=False)
    expected_outflow_inr = Column(Numeric(12, 2), nullable=False)
    net_cashflow_inr = Column(Numeric(12, 2), nullable=False)
    lower_bound_inr = Column(Numeric(12, 2), nullable=False)
    upper_bound_inr = Column(Numeric(12, 2), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    model_used = Column(String(50), nullable=False)
    confidence_score = Column(Numeric(3, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="cashflow_predictions")
    
    __table_args__ = (
        Index("idx_cashflow_predictions_user_date", "user_id", "prediction_date"),
    )


class SmoothingBuffer(Base):
    __tablename__ = "smoothing_buffers"
    
    buffer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, unique=True)
    buffer_balance_inr = Column(Numeric(12, 2), default=0, nullable=False)
    total_deposited_inr = Column(Numeric(12, 2), default=0)
    total_released_inr = Column(Numeric(12, 2), default=0)
    buffer_risk_score = Column(Numeric(3, 2), default=0)
    min_buffer_threshold_inr = Column(Numeric(12, 2), default=0)
    max_buffer_capacity_inr = Column(Numeric(12, 2), default=0)
    last_deposit_date = Column(DateTime)
    last_release_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="smoothing_buffer")


class WeeklyRelease(Base):
    __tablename__ = "weekly_releases"
    
    release_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    week_start_date = Column(DateTime, nullable=False)
    recommended_weekly_release_inr = Column(Numeric(12, 2), nullable=False)
    actual_release_inr = Column(Numeric(12, 2), default=0)
    buffer_balance_before_inr = Column(Numeric(12, 2), nullable=False)
    buffer_balance_after_inr = Column(Numeric(12, 2), nullable=False)
    is_released = Column(Boolean, default=False)
    released_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="weekly_releases")
    
    __table_args__ = (
        Index("idx_weekly_releases_user_week", "user_id", "week_start_date"),
    )


class AIInsight(Base):
    __tablename__ = "ai_insights"
    
    insight_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    insight_type = Column(Enum(InsightType), nullable=False)
    severity = Column(Enum(InsightSeverity), nullable=False)
    explanation_text = Column(Text, nullable=False)
    supporting_metrics = Column(JSONB, nullable=False)
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="ai_insights")
    
    __table_args__ = (
        Index("idx_ai_insights_user_created", "user_id", "created_at"),
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    version_number = Column(String(20), nullable=False)
    algorithm = Column(String(50), nullable=False)
    parameters = Column(JSONB)
    training_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    metrics = relationship("ModelMetric", back_populates="model_version")


class ModelMetric(Base):
    __tablename__ = "model_metrics"
    
    metric_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.version_id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric(12, 4), nullable=False)
    evaluation_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    model_version = relationship("ModelVersion", back_populates="metrics")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_audit_logs_user_created", "user_id", "created_at"),
    )
