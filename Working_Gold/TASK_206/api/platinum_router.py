"""
TASK_213: Platinum Tier API Endpoints
FastAPI APIRouter for Platinum dual-agent architecture.

Endpoints:
    GET    /api/v1/platinum/status          - System status (both agents)
    GET    /api/v1/platinum/tasks           - List all Platinum tasks
    POST   /api/v1/platinum/tasks           - Create task in Needs_Action
    GET    /api/v1/platinum/tasks/{id}      - Get task details
    GET    /api/v1/platinum/pending         - List pending approvals
    POST   /api/v1/platinum/approve/{id}    - Approve a draft
    POST   /api/v1/platinum/reject/{id}     - Reject a draft
    GET    /api/v1/platinum/agents          - Agent heartbeat status
    POST   /api/v1/platinum/demo           - Run demo workflow
    GET    /api/v1/platinum/audit           - Audit log
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.database import (
    get_db, PlatinumTask, AgentStatus, PlatinumAuditLog
)

router = APIRouter(prefix="/api/v1/platinum", tags=["Platinum"])

# Vault path for file-based operations
VAULT_PATH = Path(__file__).parent.parent.parent.parent


# ========== SCHEMAS ==========

class PlatinumTaskCreate(BaseModel):
    domain: str
    title: str
    body: str = ""

class PlatinumTaskResponse(BaseModel):
    task_id: str
    domain: str
    title: str
    body: str
    status: str
    owner: Optional[str] = None
    author: Optional[str] = None
    approver: Optional[str] = None

    class Config:
        from_attributes = True

class RejectRequest(BaseModel):
    reason: str

class DemoResponse(BaseModel):
    success: bool
    steps: List[dict]
    audit_trail: List[dict]


# ========== HELPER ==========

def _log_audit(db: Session, agent: str, action: str, task_id: str = None, details: str = ""):
    """Write an audit log entry."""
    entry = PlatinumAuditLog(
        agent=agent, action=action, task_id=task_id, details=details
    )
    db.add(entry)
    db.commit()


# ========== ENDPOINTS ==========

@router.get("/status")
async def platinum_status(db: Session = Depends(get_db)):
    """System status overview for both agents."""
    agents = db.query(AgentStatus).all()
    tasks = db.query(PlatinumTask).all()

    status_counts = {}
    for t in tasks:
        status_counts[t.status] = status_counts.get(t.status, 0) + 1

    return {
        "tier": "Platinum",
        "agents": [
            {
                "name": a.agent_name,
                "status": a.status,
                "current_task": a.current_task,
                "last_heartbeat": a.last_heartbeat.isoformat() if a.last_heartbeat else None,
                "tasks_completed": a.tasks_completed,
            }
            for a in agents
        ],
        "tasks": {
            "total": len(tasks),
            "by_status": status_counts,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/tasks", response_model=List[PlatinumTaskResponse])
async def list_platinum_tasks(
    domain: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all Platinum tasks, optionally filtered."""
    query = db.query(PlatinumTask)
    if domain:
        query = query.filter(PlatinumTask.domain == domain)
    if status:
        query = query.filter(PlatinumTask.status == status)
    return query.order_by(PlatinumTask.created_at.desc()).all()


@router.post("/tasks", response_model=PlatinumTaskResponse)
async def create_platinum_task(task: PlatinumTaskCreate, db: Session = Depends(get_db)):
    """Create a new Platinum task in Needs_Action."""
    if task.domain not in ("email", "social", "accounting", "monitoring"):
        raise HTTPException(status_code=400, detail="Invalid domain")

    task_id = f"PT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    db_task = PlatinumTask(
        task_id=task_id,
        domain=task.domain,
        title=task.title,
        body=task.body,
        status="NEEDS_ACTION",
        author="api",
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    _log_audit(db, "api", "task_created", task_id, f"Domain: {task.domain}, Title: {task.title}")

    # Also create file in Needs_Action/ directory
    needs_dir = VAULT_PATH / "Platinum" / "Needs_Action" / task.domain
    needs_dir.mkdir(parents=True, exist_ok=True)
    task_file = needs_dir / f"{task_id}.json"
    task_file.write_text(json.dumps({
        "task_id": task_id,
        "domain": task.domain,
        "title": task.title,
        "body": task.body,
        "status": "NEEDS_ACTION",
        "created_at": datetime.utcnow().isoformat(),
    }, indent=2), encoding="utf-8")

    return db_task


@router.get("/tasks/{task_id}", response_model=PlatinumTaskResponse)
async def get_platinum_task(task_id: str, db: Session = Depends(get_db)):
    """Get specific Platinum task details."""
    task = db.query(PlatinumTask).filter(PlatinumTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.get("/pending")
async def list_pending_approvals(db: Session = Depends(get_db)):
    """List all tasks pending approval."""
    pending = db.query(PlatinumTask).filter(
        PlatinumTask.status == "PENDING_APPROVAL"
    ).all()
    return [
        {
            "task_id": t.task_id,
            "domain": t.domain,
            "title": t.title,
            "author": t.author,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in pending
    ]


@router.post("/approve/{task_id}")
async def approve_task(task_id: str, db: Session = Depends(get_db)):
    """Approve a pending draft."""
    task = db.query(PlatinumTask).filter(PlatinumTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if task.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Task is not pending approval (status: {task.status})")

    task.status = "APPROVED"
    task.approver = "local"
    task.updated_at = datetime.utcnow()
    db.commit()

    _log_audit(db, "local", "approved", task_id, f"Approved: {task.title}")
    return {"status": "approved", "task_id": task_id}


@router.post("/reject/{task_id}")
async def reject_task(task_id: str, body: RejectRequest, db: Session = Depends(get_db)):
    """Reject a pending draft with reason."""
    task = db.query(PlatinumTask).filter(PlatinumTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if task.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Task is not pending approval (status: {task.status})")

    task.status = "REJECTED"
    task.approver = "local"
    task.reject_reason = body.reason
    task.updated_at = datetime.utcnow()
    db.commit()

    _log_audit(db, "local", "rejected", task_id, f"Rejected: {body.reason}")
    return {"status": "rejected", "task_id": task_id, "reason": body.reason}


@router.get("/agents")
async def get_agent_status(db: Session = Depends(get_db)):
    """Get agent heartbeat status."""
    agents = db.query(AgentStatus).all()

    # Also check file-based heartbeats
    updates_dir = VAULT_PATH / "Platinum" / "Updates"
    file_agents = []
    if updates_dir.exists():
        for f in updates_dir.glob("*_heartbeat.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                file_agents.append(data)
            except (json.JSONDecodeError, OSError):
                pass

    return {
        "database_agents": [
            {
                "name": a.agent_name,
                "status": a.status,
                "current_task": a.current_task,
                "last_heartbeat": a.last_heartbeat.isoformat() if a.last_heartbeat else None,
                "tasks_completed": a.tasks_completed,
            }
            for a in agents
        ],
        "file_agents": file_agents,
    }


@router.post("/demo", response_model=DemoResponse)
async def run_demo(db: Session = Depends(get_db)):
    """Run the Platinum demo workflow via API."""
    steps = []
    audit = []
    now = datetime.utcnow

    # Step 1: Create email task
    task_id = f"PT-DEMO-{now().strftime('%H%M%S')}"
    db_task = PlatinumTask(
        task_id=task_id, domain="email",
        title="Demo: Invoice Follow-up",
        body="Please review invoice #1234 and confirm payment.",
        status="NEEDS_ACTION", author="demo",
    )
    db.add(db_task)
    db.commit()
    steps.append({"step": 1, "action": "Task created in Needs_Action", "task_id": task_id})

    # Step 2: Cloud claims task
    db_task.status = "CLAIMED"
    db_task.owner = "cloud"
    db.commit()
    steps.append({"step": 2, "action": "Cloud Agent claimed task", "owner": "cloud"})

    # Step 3: Cloud drafts reply
    db_task.status = "DRAFTING"
    db.commit()
    steps.append({"step": 3, "action": "Cloud Agent drafting reply"})

    # Step 4: Cloud submits for approval
    db_task.status = "PENDING_APPROVAL"
    db.commit()
    steps.append({"step": 4, "action": "Draft submitted for Local approval"})

    # Step 5: Local approves
    db_task.status = "APPROVED"
    db_task.approver = "local"
    db.commit()
    steps.append({"step": 5, "action": "Local Agent approved draft"})

    # Step 6: Local executes send
    db_task.status = "DONE"
    db.commit()
    steps.append({"step": 6, "action": "Local Agent executed send (simulated)"})

    # Step 7: Audit log
    _log_audit(db, "demo", "demo_complete", task_id, f"Demo completed all 7 steps")
    steps.append({"step": 7, "action": "Audit trail recorded"})

    # Build audit trail
    audit_entries = db.query(PlatinumAuditLog).filter(
        PlatinumAuditLog.task_id == task_id
    ).all()
    for e in audit_entries:
        audit.append({
            "agent": e.agent, "action": e.action,
            "task_id": e.task_id, "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        })

    return DemoResponse(success=True, steps=steps, audit_trail=audit)


@router.get("/audit")
async def get_audit_log(limit: int = 50, db: Session = Depends(get_db)):
    """Get Platinum audit log entries."""
    entries = db.query(PlatinumAuditLog).order_by(
        PlatinumAuditLog.timestamp.desc()
    ).limit(limit).all()
    return [
        {
            "id": e.id,
            "agent": e.agent,
            "action": e.action,
            "task_id": e.task_id,
            "details": e.details,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in entries
    ]
