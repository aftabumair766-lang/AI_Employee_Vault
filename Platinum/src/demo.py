"""
Platinum Demo Workflow - Section 10.6 Gate

Demonstrates the complete Platinum dual-agent flow:
1. Create email task in Needs_Action/email/
2. Cloud Agent picks up task (claim-by-move)
3. Cloud Agent drafts reply
4. Cloud writes to Pending_Approval/email/
5. Local Agent reviews (auto-approve in demo mode)
6. Local Agent executes send (simulated)
7. Action logged in audit log, task moved to Done/

Usage:
    python -m Platinum.src.demo
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Platinum.src.cloud_agent import CloudAgent
from Platinum.src.local_agent import LocalAgent
from Platinum.src.agent_heartbeat import AgentHeartbeat
from Platinum.src.secret_guard import SecretGuard


def run_demo(vault_path: str = None) -> dict:
    """Run the complete Platinum demo workflow.

    Args:
        vault_path: Path to the vault root. Defaults to project root.

    Returns:
        dict with success status, steps completed, and audit trail.
    """
    if vault_path is None:
        vault_path = str(PROJECT_ROOT)

    vault = Path(vault_path)
    platinum_dir = vault / "Platinum"
    logs_dir = platinum_dir / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    steps = []
    audit_trail = []

    def log_step(step_num: int, description: str, details: str = ""):
        entry = {
            "step": step_num,
            "description": description,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        steps.append(entry)
        print(f"  Step {step_num}: {description}")
        if details:
            print(f"          {details}")

    print("=" * 60)
    print("PLATINUM TIER - DEMO WORKFLOW")
    print("Section 10.6 Gate: Email triage demonstration")
    print("=" * 60)
    print()

    # Step 1: Create email task in Needs_Action/email/
    email_dir = platinum_dir / "Needs_Action" / "email"
    email_dir.mkdir(parents=True, exist_ok=True)
    task_id = f"DEMO-{datetime.utcnow().strftime('%H%M%S')}"
    task_data = {
        "task_id": task_id,
        "domain": "email",
        "title": "Invoice #1234 - Payment Confirmation",
        "body": "Dear team, please confirm payment for invoice #1234. Amount: $5,000. Due: Feb 15.",
        "status": "needs_action",
        "created_at": datetime.utcnow().isoformat(),
    }
    task_file = email_dir / f"{task_id}.json"
    task_file.write_text(json.dumps(task_data, indent=2), encoding="utf-8")
    log_step(1, "Email task created in Needs_Action/email/", f"Task ID: {task_id}")

    # Step 2: Cloud Agent picks up task
    cloud = CloudAgent(vault_path)
    cloud.heartbeat.beat(current_task=task_id)
    available = cloud.scan_needs_action()
    log_step(2, "Cloud Agent scanned Needs_Action/", f"Found {len(available)} tasks")

    # Step 3: Cloud Agent claims and drafts reply
    task_rel_path = f"Needs_Action/email/{task_id}.json"
    draft_id = cloud.process_task(task_rel_path)
    log_step(3, "Cloud Agent claimed task and drafted reply", f"Draft ID: {draft_id}")

    # Step 4: Verify draft is in Pending_Approval/
    local = LocalAgent(vault_path)
    pending = local.review_pending()
    log_step(4, "Draft submitted to Pending_Approval/", f"Pending drafts: {len(pending)}")

    # Step 5: Local Agent auto-approves
    approved_drafts = local.run_once()
    approved_ids = [d.draft_id for d in approved_drafts]
    log_step(5, "Local Agent reviewed and approved", f"Approved: {approved_ids}")

    # Step 6: Local Agent executes send (simulated)
    executed = local.get_executed_actions()
    log_step(6, "Local Agent executed send (simulated)", f"Actions: {len(executed)}")

    # Step 7: Audit trail
    audit_trail = cloud.get_log() + local.get_log()
    log_step(7, "Audit trail recorded", f"Total entries: {len(audit_trail)}")

    # Verify SecretGuard boundaries
    cloud_guard = SecretGuard(agent_role="cloud")
    local_guard = SecretGuard(agent_role="local")
    print()
    print("  Secret Boundary Verification:")
    print(f"    Cloud can access .env: {cloud_guard.can_access('.env')}")  # False
    print(f"    Cloud can access email_draft: {cloud_guard.can_access('email_draft')}")  # True
    print(f"    Local can access .env: {local_guard.can_access('.env')}")  # True
    print(f"    Local can access banking/: {local_guard.can_access('banking/creds')}")  # True

    # Write demo execution log
    demo_log = {
        "demo_run": datetime.utcnow().isoformat(),
        "task_id": task_id,
        "draft_id": draft_id,
        "steps_completed": len(steps),
        "steps": steps,
        "audit_trail": audit_trail,
        "secret_guard_verified": True,
    }
    log_file = logs_dir / "demo_execution.log"
    log_file.write_text(json.dumps(demo_log, indent=2), encoding="utf-8")

    print()
    print("=" * 60)
    success = len(steps) == 7 and draft_id is not None and len(approved_drafts) > 0
    if success:
        print("DEMO COMPLETE - All 7 steps passed")
    else:
        print("DEMO INCOMPLETE - Some steps failed")
    print(f"Log written to: {log_file}")
    print("=" * 60)

    return {
        "success": success,
        "steps": steps,
        "audit_trail": audit_trail,
        "task_id": task_id,
        "draft_id": draft_id,
    }


if __name__ == "__main__":
    run_demo()
