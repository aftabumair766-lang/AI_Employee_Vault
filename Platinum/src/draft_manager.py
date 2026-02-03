"""
DraftManager - Draft creation and approval workflow manager.

Reusable Platinum Skill: Manages the lifecycle of drafts from creation
through approval or rejection. Drafts are stored as JSON files in the
vault's delegation directories.

Usage:
    dm = DraftManager("/path/to/vault")
    draft = dm.create_draft("email", "Re: Invoice", "Dear...", "cloud_agent")
    dm.submit_for_approval(draft.draft_id)
    dm.approve(draft.draft_id, "local_agent")
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from pathlib import Path


@dataclass
class Draft:
    """Represents a draft document in the approval workflow."""
    draft_id: str
    domain: str
    title: str
    body: str
    status: str  # "draft", "pending_approval", "approved", "rejected"
    author: str
    approver: Optional[str] = None
    reject_reason: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    audit_trail: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Draft":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class DraftManager:
    """Manages draft creation and approval workflows via file-based delegation."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.platinum_dir = self.vault_path / "Platinum"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure required directories exist."""
        for domain in ("email", "social", "accounting", "monitoring"):
            (self.platinum_dir / "Needs_Action" / domain).mkdir(parents=True, exist_ok=True)
            (self.platinum_dir / "Pending_Approval" / domain).mkdir(parents=True, exist_ok=True)
            (self.platinum_dir / "Plans" / domain).mkdir(parents=True, exist_ok=True)
        (self.platinum_dir / "Done").mkdir(parents=True, exist_ok=True)
        (self.platinum_dir / "Logs").mkdir(parents=True, exist_ok=True)

    def _draft_filename(self, draft_id: str) -> str:
        return f"{draft_id}.json"

    def _find_draft_file(self, draft_id: str) -> Optional[Path]:
        """Search for a draft file across all directories."""
        filename = self._draft_filename(draft_id)
        search_dirs = [
            self.platinum_dir / "Needs_Action",
            self.platinum_dir / "Pending_Approval",
            self.platinum_dir / "In_Progress",
            self.platinum_dir / "Done",
            self.platinum_dir / "Plans",
        ]
        for base_dir in search_dirs:
            if base_dir.exists():
                for root, _, files in os.walk(str(base_dir)):
                    if filename in files:
                        return Path(root) / filename
        return None

    def create_draft(self, domain: str, title: str, body: str, author: str) -> Draft:
        """Create a new draft in the Plans directory."""
        draft_id = f"DRAFT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.utcnow().isoformat()

        draft = Draft(
            draft_id=draft_id,
            domain=domain,
            title=title,
            body=body,
            status="draft",
            author=author,
            created_at=now,
            updated_at=now,
            audit_trail=[{
                "action": "created",
                "agent": author,
                "timestamp": now,
            }],
        )

        # Write to Plans/<domain>/
        plans_dir = self.platinum_dir / "Plans" / domain
        plans_dir.mkdir(parents=True, exist_ok=True)
        draft_file = plans_dir / self._draft_filename(draft_id)
        draft_file.write_text(draft.to_json(), encoding="utf-8")

        return draft

    def submit_for_approval(self, draft_id: str) -> bool:
        """Move draft from Plans/ to Pending_Approval/."""
        draft_file = self._find_draft_file(draft_id)
        if not draft_file or not draft_file.exists():
            return False

        draft = Draft.from_dict(json.loads(draft_file.read_text(encoding="utf-8")))
        now = datetime.utcnow().isoformat()

        draft.status = "pending_approval"
        draft.updated_at = now
        draft.audit_trail.append({
            "action": "submitted_for_approval",
            "agent": draft.author,
            "timestamp": now,
        })

        # Move to Pending_Approval/<domain>/
        dest_dir = self.platinum_dir / "Pending_Approval" / draft.domain
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / self._draft_filename(draft_id)

        dest_file.write_text(draft.to_json(), encoding="utf-8")
        if draft_file != dest_file:
            draft_file.unlink()

        return True

    def list_pending(self, domain: Optional[str] = None) -> List[Draft]:
        """List all pending approval drafts, optionally filtered by domain."""
        pending = []
        pending_dir = self.platinum_dir / "Pending_Approval"

        if domain:
            domains = [domain]
        else:
            domains = [d.name for d in pending_dir.iterdir() if d.is_dir()] if pending_dir.exists() else []

        for d in domains:
            domain_dir = pending_dir / d
            if domain_dir.exists():
                for f in domain_dir.glob("DRAFT-*.json"):
                    try:
                        data = json.loads(f.read_text(encoding="utf-8"))
                        pending.append(Draft.from_dict(data))
                    except (json.JSONDecodeError, TypeError):
                        continue
        return pending

    def approve(self, draft_id: str, approver: str) -> Optional[Draft]:
        """Approve a draft and move to Done/."""
        draft_file = self._find_draft_file(draft_id)
        if not draft_file or not draft_file.exists():
            return None

        draft = Draft.from_dict(json.loads(draft_file.read_text(encoding="utf-8")))
        now = datetime.utcnow().isoformat()

        draft.status = "approved"
        draft.approver = approver
        draft.updated_at = now
        draft.audit_trail.append({
            "action": "approved",
            "agent": approver,
            "timestamp": now,
        })

        # Move to Done/
        done_dir = self.platinum_dir / "Done"
        done_dir.mkdir(parents=True, exist_ok=True)
        dest_file = done_dir / self._draft_filename(draft_id)
        dest_file.write_text(draft.to_json(), encoding="utf-8")
        if draft_file != dest_file:
            draft_file.unlink()

        return draft

    def reject(self, draft_id: str, approver: str, reason: str) -> Optional[Draft]:
        """Reject a draft with a reason."""
        draft_file = self._find_draft_file(draft_id)
        if not draft_file or not draft_file.exists():
            return None

        draft = Draft.from_dict(json.loads(draft_file.read_text(encoding="utf-8")))
        now = datetime.utcnow().isoformat()

        draft.status = "rejected"
        draft.approver = approver
        draft.reject_reason = reason
        draft.updated_at = now
        draft.audit_trail.append({
            "action": "rejected",
            "agent": approver,
            "reason": reason,
            "timestamp": now,
        })

        # Write back in place (stays in Pending_Approval for review)
        draft_file.write_text(draft.to_json(), encoding="utf-8")
        return draft

    def get_draft(self, draft_id: str) -> Optional[Draft]:
        """Retrieve a draft by ID."""
        draft_file = self._find_draft_file(draft_id)
        if not draft_file or not draft_file.exists():
            return None
        data = json.loads(draft_file.read_text(encoding="utf-8"))
        return Draft.from_dict(data)

    def get_audit_trail(self, draft_id: str) -> List[dict]:
        """Get the full audit trail for a draft."""
        draft = self.get_draft(draft_id)
        if draft:
            return draft.audit_trail
        return []
