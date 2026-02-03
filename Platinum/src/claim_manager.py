"""
ClaimManager - Claim-by-move task ownership.

Reusable Platinum Skill: Prevents double-work between agents by using
atomic file moves. The first agent to move a task file from Needs_Action/
to In_Progress/<agent>/ owns the task.

Usage:
    cm = ClaimManager("/path/to/vault")
    available = cm.list_available("email")
    if cm.claim("DRAFT-ABC123.json", "cloud_agent"):
        print("Task claimed!")
"""

import os
import shutil
import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path


class ClaimManager:
    """Claim-by-move task ownership for preventing double-work between agents."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.platinum_dir = self.vault_path / "Platinum"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure required directories exist."""
        for domain in ("email", "social", "accounting", "monitoring"):
            (self.platinum_dir / "Needs_Action" / domain).mkdir(parents=True, exist_ok=True)
        for agent in ("cloud", "local"):
            (self.platinum_dir / "In_Progress" / agent).mkdir(parents=True, exist_ok=True)

    def list_available(self, domain: Optional[str] = None) -> List[str]:
        """List task files available in Needs_Action/."""
        available = []
        needs_action = self.platinum_dir / "Needs_Action"

        if domain:
            domains = [domain]
        else:
            domains = [
                d.name for d in needs_action.iterdir() if d.is_dir()
            ] if needs_action.exists() else []

        for d in domains:
            domain_dir = needs_action / d
            if domain_dir.exists():
                for f in domain_dir.iterdir():
                    if f.is_file() and f.suffix == ".json":
                        available.append(str(f.relative_to(self.platinum_dir)))

        return available

    def claim(self, task_file: str, agent_name: str) -> bool:
        """Claim a task by moving it from Needs_Action/ to In_Progress/<agent>/.

        Uses atomic file move to prevent race conditions. The first agent
        to successfully move the file owns the task.

        Args:
            task_file: Relative path from Platinum/ (e.g. "Needs_Action/email/task.json")
            agent_name: Name of the claiming agent ("cloud" or "local")

        Returns:
            True if claim was successful, False if file was already claimed or missing.
        """
        source = self.platinum_dir / task_file
        if not source.exists():
            return False

        dest_dir = self.platinum_dir / "In_Progress" / agent_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / source.name

        # If already claimed by someone, fail
        if dest.exists():
            return False

        try:
            # Update task metadata before moving
            if source.suffix == ".json":
                try:
                    data = json.loads(source.read_text(encoding="utf-8"))
                    data["owner"] = agent_name
                    data["claimed_at"] = datetime.utcnow().isoformat()
                    data["status"] = "claimed"
                    source.write_text(json.dumps(data, indent=2), encoding="utf-8")
                except (json.JSONDecodeError, TypeError):
                    pass

            # Atomic move (claim-by-move rule)
            shutil.move(str(source), str(dest))
            return True
        except (OSError, shutil.Error):
            return False

    def is_claimed(self, task_file: str) -> bool:
        """Check if a task file has been claimed (exists in In_Progress/)."""
        filename = Path(task_file).name
        for agent_dir in (self.platinum_dir / "In_Progress").iterdir():
            if agent_dir.is_dir() and (agent_dir / filename).exists():
                return True
        return False

    def release(self, task_file: str, agent_name: str) -> bool:
        """Release a claimed task back to Needs_Action/.

        Args:
            task_file: Filename of the task (e.g. "task.json")
            agent_name: Name of the agent releasing the task

        Returns:
            True if release was successful.
        """
        filename = Path(task_file).name
        source = self.platinum_dir / "In_Progress" / agent_name / filename
        if not source.exists():
            return False

        # Determine original domain from task data
        domain = "email"  # default
        if source.suffix == ".json":
            try:
                data = json.loads(source.read_text(encoding="utf-8"))
                domain = data.get("domain", "email")
                data["owner"] = None
                data["claimed_at"] = None
                data["status"] = "needs_action"
                source.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except (json.JSONDecodeError, TypeError):
                pass

        dest_dir = self.platinum_dir / "Needs_Action" / domain
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename

        try:
            shutil.move(str(source), str(dest))
            return True
        except (OSError, shutil.Error):
            return False

    def get_owner(self, task_file: str) -> Optional[str]:
        """Get the agent that owns a task file."""
        filename = Path(task_file).name
        in_progress = self.platinum_dir / "In_Progress"
        if in_progress.exists():
            for agent_dir in in_progress.iterdir():
                if agent_dir.is_dir() and (agent_dir / filename).exists():
                    return agent_dir.name
        return None

    def list_claimed_by(self, agent_name: str) -> List[str]:
        """List all tasks claimed by a specific agent."""
        agent_dir = self.platinum_dir / "In_Progress" / agent_name
        if not agent_dir.exists():
            return []
        return [f.name for f in agent_dir.iterdir() if f.is_file()]
