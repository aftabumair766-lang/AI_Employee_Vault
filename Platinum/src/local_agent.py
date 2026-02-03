"""
LocalAgent - Local Executive Agent for the Platinum Tier.

Uses skills: DraftManager, AgentHeartbeat, SecretGuard, VaultSync

The Local Agent has full executive authority. It reviews drafts submitted
by the Cloud Agent, approves or rejects them, and executes the final
actions (sending emails, posting to social, etc). Only the Local Agent
can access secrets and execute sends.

Usage:
    agent = LocalAgent("/path/to/vault")
    agent.run_once()  # Single iteration
    # or
    agent.start()     # Interactive CLI loop
"""

import json
import time
import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from Platinum.src.vault_sync import VaultSync
from Platinum.src.draft_manager import DraftManager, Draft
from Platinum.src.agent_heartbeat import AgentHeartbeat
from Platinum.src.secret_guard import SecretGuard

logger = logging.getLogger("platinum.local_agent")


class LocalAgent:
    """Local Executive Agent - reviews, approves, and executes actions."""

    AGENT_NAME = "local"

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.vault_sync = VaultSync(str(vault_path))
        self.draft_manager = DraftManager(str(vault_path))
        self.heartbeat = AgentHeartbeat(self.AGENT_NAME, str(vault_path), interval=30)
        self.secret_guard = SecretGuard(agent_role="local")  # Full access
        self._running = False
        self._log: list = []
        self._executed_actions: list = []

    def _log_action(self, action: str, details: str):
        entry = {
            "agent": self.AGENT_NAME,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._log.append(entry)
        logger.info(f"[LocalAgent] {action}: {details}")

    def start(self):
        """Interactive CLI loop for reviewing and approving drafts."""
        self._running = True
        self.heartbeat.start_background()
        self._log_action("start", "Local Agent started")

        try:
            while self._running:
                self.run_once()
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Graceful shutdown."""
        self._running = False
        self.heartbeat.stop_background()
        self._log_action("stop", "Local Agent stopped")

    def review_pending(self) -> List[Draft]:
        """List and display all pending approval drafts."""
        pending = self.draft_manager.list_pending()
        self._log_action("review", f"Found {len(pending)} pending drafts")
        return pending

    def approve_draft(self, draft_id: str) -> Optional[Draft]:
        """Approve a draft and execute the action."""
        draft = self.draft_manager.approve(draft_id, self.AGENT_NAME)
        if draft:
            self._log_action("approved", f"Approved draft {draft_id}")
            self.execute_action(draft)
            return draft
        self._log_action("approve_failed", f"Could not approve draft {draft_id}")
        return None

    def reject_draft(self, draft_id: str, reason: str) -> Optional[Draft]:
        """Reject a draft with a reason."""
        draft = self.draft_manager.reject(draft_id, self.AGENT_NAME, reason)
        if draft:
            self._log_action("rejected", f"Rejected draft {draft_id}: {reason}")
            return draft
        self._log_action("reject_failed", f"Could not reject draft {draft_id}")
        return None

    def execute_action(self, draft: Draft) -> bool:
        """Execute the approved action (send email, post, etc).

        This is where the Local Agent uses its executive authority and
        secret access to actually perform the action.
        """
        self.heartbeat.beat(current_task=draft.draft_id)

        action_record = {
            "draft_id": draft.draft_id,
            "domain": draft.domain,
            "title": draft.title,
            "action": f"execute_{draft.domain}",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "executed",
        }

        if draft.domain == "email":
            # Simulated email send (would use SMTP with secrets in production)
            action_record["details"] = f"Email sent: {draft.title}"
            self._log_action("executed", f"Sent email: {draft.title}")

        elif draft.domain == "social":
            # Simulated social post (would use API with tokens in production)
            action_record["details"] = f"Social post published: {draft.title}"
            self._log_action("executed", f"Published social post: {draft.title}")

        elif draft.domain == "accounting":
            # Simulated accounting entry
            action_record["details"] = f"Accounting entry recorded: {draft.title}"
            self._log_action("executed", f"Recorded accounting entry: {draft.title}")

        else:
            action_record["details"] = f"Action executed for domain: {draft.domain}"
            self._log_action("executed", f"Executed action for {draft.domain}: {draft.title}")

        self._executed_actions.append(action_record)

        # Write execution log
        self._write_execution_log(action_record)
        return True

    def _write_execution_log(self, action_record: dict):
        """Write execution record to Platinum/Logs/."""
        logs_dir = self.vault_path / "Platinum" / "Logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "execution_log.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(action_record) + "\n")

    def update_dashboard(self):
        """Update the Platinum dashboard with current status (single-writer)."""
        dashboard_path = self.vault_path / "Platinum" / "DASHBOARD_Platinum.md"

        pending = self.draft_manager.list_pending()
        agents = self.heartbeat.get_all_agents()

        content = f"""# PLATINUM LEVEL DASHBOARD

**Level**: Platinum (Dual-Agent Architecture)
**Last Updated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

---

## Agent Status

| Agent | Status | Current Task |
|-------|--------|--------------|
"""
        for agent in agents:
            content += f"| {agent.get('agent_name', 'unknown')} | {agent.get('status', 'unknown')} | {agent.get('current_task', '-')} |\n"

        content += f"""
---

## Pending Approvals: {len(pending)}

| Draft ID | Domain | Title | Author |
|----------|--------|-------|--------|
"""
        for draft in pending:
            content += f"| {draft.draft_id} | {draft.domain} | {draft.title} | {draft.author} |\n"

        content += f"""
---

## Executed Actions: {len(self._executed_actions)}

| Draft ID | Domain | Action | Timestamp |
|----------|--------|--------|-----------|
"""
        for action in self._executed_actions[-10:]:
            content += f"| {action['draft_id']} | {action['domain']} | {action['action']} | {action['timestamp']} |\n"

        content += "\n---\n"
        dashboard_path.write_text(content, encoding="utf-8")
        self._log_action("dashboard", "Dashboard updated")

    def run_once(self) -> List[Draft]:
        """Single iteration: review pending, auto-approve all (for demo)."""
        self.heartbeat.beat()
        approved = []

        pending = self.review_pending()
        for draft in pending:
            result = self.approve_draft(draft.draft_id)
            if result:
                approved.append(result)

        if approved:
            self.update_dashboard()

        return approved

    def get_log(self) -> list:
        return self._log.copy()

    def get_executed_actions(self) -> list:
        return self._executed_actions.copy()
