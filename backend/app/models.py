"""
SQLAlchemy models for the comprehensive launch orchestrator
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Launch(Base):
    __tablename__ = "launches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    product_type = Column(String(100), nullable=True)
    target_market = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed, cancelled
    phase = Column(String(50), default="planning")  # planning, development, testing, launch, post_launch
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    launch_date = Column(DateTime(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
    prd_content = Column(Text, nullable=True)
    risk_register = Column(JSON, nullable=True)
    compliance_status = Column(String(50), default="pending")
    readiness_score = Column(Float, default=0.0)
    
    # Relationships
    agent_results = relationship("AgentResult", back_populates="launch", cascade="all, delete-orphan")
    market_intelligence = relationship("MarketIntelligence", back_populates="launch", cascade="all, delete-orphan")
    customer_insights = relationship("CustomerInsights", back_populates="launch", cascade="all, delete-orphan")
    timeline_items = relationship("TimelineItem", back_populates="launch", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="launch", cascade="all, delete-orphan")
    communications = relationship("Communication", back_populates="launch", cascade="all, delete-orphan")
    metrics = relationship("LaunchMetric", back_populates="launch", cascade="all, delete-orphan")

class AgentResult(Base):
    __tablename__ = "agent_results"
    
    id = Column(Integer, primary_key=True, index=True)
    launch_id = Column(Integer, ForeignKey("launches.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)  # market_intelligence, customer_pulse, etc.
    agent_type = Column(String(50), nullable=False)  # research, analysis, coordination, monitoring
    output = Column(Text, nullable=True)
    agent_metadata = Column(JSON, nullable=True)  # Store structured data
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    error_flag = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    execution_time = Column(Float, nullable=True)  # Time taken in seconds
    
    # Relationships
    launch = relationship("Launch", back_populates="agent_results")

class MarketIntelligence(Base):
    __tablename__ = "market_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    launch_id = Column(Integer, ForeignKey("launches.id"), nullable=False)
    competitor_analysis = Column(JSON, nullable=True)
    market_trends = Column(JSON, nullable=True)
    pricing_insights = Column(JSON, nullable=True)
    feature_comparison = Column(JSON, nullable=True)
    market_size = Column(String(100), nullable=True)
    growth_rate = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    launch = relationship("Launch", back_populates="market_intelligence")

class CustomerInsights(Base):
    __tablename__ = "customer_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    launch_id = Column(Integer, ForeignKey("launches.id"), nullable=False)
    pain_points = Column(JSON, nullable=True)
    feature_requests = Column(JSON, nullable=True)
    sentiment_analysis = Column(JSON, nullable=True)
    nps_score = Column(Float, nullable=True)
    support_tickets = Column(JSON, nullable=True)
    social_mentions = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    launch = relationship("Launch", back_populates="customer_insights")

class TimelineItem(Base):
    __tablename__ = "timeline_items"
    
    id = Column(Integer, primary_key=True, index=True)
    launch_id = Column(Integer, ForeignKey("launches.id"), nullable=False)
    task_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, blocked
    assigned_to = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)  # dev, qa, marketing, legal, etc.
    dependencies = Column(JSON, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    progress_percentage = Column(Float, default=0.0)
    
    # Relationships
    launch = relationship("Launch", back_populates="timeline_items")

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    launch_id = Column(Integer, ForeignKey("launches.id"), nullable=False)
    risk_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # technical, legal, market, operational
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    probability = Column(Float, default=0.5)  # 0.0 to 1.0
    impact = Column(String(20), default="medium")  # low, medium, high, critical
    mitigation_plan = Column(Text, nullable=True)
    owner = Column(String(100), nullable=True)
    status = Column(String(50), default="open")  # open, mitigated, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    launch = relationship("Launch", back_populates="risks")

class Communication(Base):
    __tablename__ = "communications"
    
    id = Column(Integer, primary_key=True, index=True)
    launch_id = Column(Integer, ForeignKey("launches.id"), nullable=False)
    communication_type = Column(String(50), nullable=False)  # internal, external, stakeholder
    audience = Column(String(100), nullable=True)  # team, customers, partners, media
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    channel = Column(String(50), nullable=True)  # email, slack, social, press
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="draft")  # draft, scheduled, sent, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    launch = relationship("Launch", back_populates="communications")

class LaunchMetric(Base):
    __tablename__ = "launch_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    launch_id = Column(Integer, ForeignKey("launches.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=True)
    metric_unit = Column(String(50), nullable=True)
    target_value = Column(Float, nullable=True)
    category = Column(String(50), nullable=True)  # adoption, usage, performance, business
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    
    # Relationships
    launch = relationship("Launch", back_populates="metrics")
