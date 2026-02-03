"""
TASK_207: Database Integration - SQLite + SQLAlchemy ORM
Uses existing skills: InputValidator for data validation
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./ai_employee.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ========== MODELS ==========

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(10), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="NEEDS_ACTION")
    level = Column(String(10), default="Gold")
    priority = Column(String(10), default="MEDIUM")
    assigned_to = Column(String(50), default="AI_Employee")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)
    target = Column(Text, nullable=True)
    result = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class MetricRecord(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    tags = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    owner = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== PLATINUM TIER MODELS (TASK_213) ==========

class PlatinumTask(Base):
    __tablename__ = "platinum_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(50), unique=True, index=True)
    domain = Column(String(20))          # email, social, accounting, monitoring
    title = Column(String(200))
    body = Column(Text)
    status = Column(String(30))          # NEEDS_ACTION, CLAIMED, DRAFTING, PENDING_APPROVAL, APPROVED, DONE
    owner = Column(String(20))           # cloud, local, None
    author = Column(String(20))
    approver = Column(String(20), nullable=True)
    reject_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentStatus(Base):
    __tablename__ = "agent_status"

    id = Column(Integer, primary_key=True)
    agent_name = Column(String(20), unique=True)
    status = Column(String(20))          # online, offline, busy
    current_task = Column(String(50), nullable=True)
    last_heartbeat = Column(DateTime)
    tasks_completed = Column(Integer, default=0)


class PlatinumAuditLog(Base):
    __tablename__ = "platinum_audit_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent = Column(String(20))
    action = Column(String(50))
    task_id = Column(String(50), nullable=True)
    details = Column(Text)


# ========== DATABASE OPERATIONS ==========

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency: Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_existing_tasks(db):
    """Seed database with existing completed tasks"""
    existing_tasks = [
        {"task_id": "TASK_201", "description": "Multi-Agent Code Quality Assessment",
         "status": "DONE", "level": "Gold", "duration": "46m"},
        {"task_id": "TASK_202", "description": "System Cleanup - Remove Legacy Files",
         "status": "DONE", "level": "Gold", "duration": "22m 30s"},
        {"task_id": "TASK_203", "description": "Advanced Multi-Agent Performance Analysis",
         "status": "DONE", "level": "Gold", "duration": "21h 58m"},
        {"task_id": "TASK_204", "description": "Critical Security Hardening Sprint",
         "status": "DONE", "level": "Gold", "duration": "36h 30m"},
        {"task_id": "TASK_205", "description": "Testing Infrastructure Foundation",
         "status": "DONE", "level": "Gold", "duration": "76h 15m"},
        {"task_id": "TASK_206", "description": "REST API Development",
         "status": "IN_PROGRESS", "level": "Gold", "duration": None},
    ]

    for task_data in existing_tasks:
        existing = db.query(Task).filter(Task.task_id == task_data["task_id"]).first()
        if not existing:
            task = Task(**task_data)
            db.add(task)

    db.commit()


# Initialize on import
init_db()
