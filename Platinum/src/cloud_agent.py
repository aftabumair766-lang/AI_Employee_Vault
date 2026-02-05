"""
CloudAgent - Always-on Cloud Agent for the Platinum Tier.

Uses skills: ClaimManager, DraftManager, AgentHeartbeat, SecretGuard, VaultSync

The Cloud Agent runs 24/7, scanning for new tasks in Needs_Action/,
claiming them via claim-by-move, drafting responses, and submitting
them for Local Agent approval. It NEVER has access to secrets.

Usage:
    agent = CloudAgent("/path/to/vault")
    agent.run_once()  # Single iteration
    # or
    agent.start()     # Continuous loop
"""

import json
import time
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from Platinum.src.vault_sync import VaultSync
from Platinum.src.draft_manager import DraftManager
from Platinum.src.claim_manager import ClaimManager
from Platinum.src.agent_heartbeat import AgentHeartbeat
from Platinum.src.secret_guard import SecretGuard
from Platinum.src.config import get_settings

logger = logging.getLogger("platinum.cloud_agent")


class CloudAgent:
    """Always-on Cloud Agent - drafts responses, never executes sends."""

    AGENT_NAME = "cloud"

    def __init__(self, vault_path: str = None, settings=None):
        self.settings = settings or get_settings(AGENT_ROLE="cloud")
        self.vault_path = Path(vault_path) if vault_path else self.settings.vault
        self.vault_sync = VaultSync(
            str(self.vault_path),
            remote=self.settings.GIT_REMOTE,
            branch=self.settings.GIT_BRANCH,
        )
        self.draft_manager = DraftManager(str(self.vault_path))
        self.claim_manager = ClaimManager(str(self.vault_path))
        self.heartbeat = AgentHeartbeat(
            self.AGENT_NAME, str(self.vault_path),
            interval=self.settings.HEARTBEAT_INTERVAL,
        )
        self.secret_guard = SecretGuard(agent_role="cloud")
        self._running = False
        self._log: list = []
        self._email_reader = None

    def _log_action(self, action: str, details: str):
        entry = {
            "agent": self.AGENT_NAME,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._log.append(entry)
        logger.info(f"[CloudAgent] {action}: {details}")

    def start(self):
        """Main loop: sync, scan, claim, draft, submit."""
        self._running = True
        self.heartbeat.start_background()
        self._log_action("start", "Cloud Agent started")

        try:
            while self._running:
                self.run_once()
                time.sleep(10)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Graceful shutdown."""
        self._running = False
        self.heartbeat.stop_background()
        self._log_action("stop", "Cloud Agent stopped")

    def scan_needs_action(self) -> list:
        """Check all Needs_Action/ domains for available tasks."""
        available = []
        for domain in ("email", "social", "accounting", "monitoring"):
            tasks = self.claim_manager.list_available(domain)
            available.extend(tasks)
        return available

    def process_task(self, task_file: str) -> Optional[str]:
        """Claim a task, create a draft, and submit for approval.

        Args:
            task_file: Relative path from Platinum/ to the task file.

        Returns:
            Draft ID if successful, None otherwise.
        """
        # Security check
        if not self.secret_guard.can_access(task_file):
            self._log_action("blocked", f"Secret guard blocked access to {task_file}")
            return None

        # Claim the task
        if not self.claim_manager.claim(task_file, self.AGENT_NAME):
            self._log_action("claim_failed", f"Could not claim {task_file}")
            return None

        self._log_action("claimed", f"Claimed {task_file}")
        self.heartbeat.beat(current_task=task_file)

        # Read task data
        filename = Path(task_file).name
        claimed_path = self.vault_path / "Platinum" / "In_Progress" / self.AGENT_NAME / filename
        try:
            task_data = json.loads(claimed_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            task_data = {"domain": "email", "title": filename, "body": ""}

        domain = task_data.get("domain", "email")

        # Generate draft based on domain
        if domain == "email":
            draft = self.draft_email_reply(task_data)
        elif domain == "social":
            draft = self.draft_social_post(task_data)
        elif domain == "accounting":
            draft = self.draft_accounting_entry(task_data)
        else:
            draft = self.draft_manager.create_draft(
                domain=domain,
                title=task_data.get("title", "Monitoring Report"),
                body=f"Auto-generated report for: {task_data.get('title', 'unknown')}",
                author=self.AGENT_NAME,
            )

        self._log_action("drafted", f"Created draft {draft.draft_id} for {domain}")

        # Submit for approval
        if self.draft_manager.submit_for_approval(draft.draft_id):
            self._log_action("submitted", f"Draft {draft.draft_id} submitted for approval")
            return draft.draft_id

        return None

    def draft_email_reply(self, task_data: dict):
        """Create an email reply draft."""
        title = task_data.get("title", "Re: Untitled")
        body = task_data.get("body", "")
        return self.draft_manager.create_draft(
            domain="email",
            title=f"Re: {title}",
            body=f"Thank you for your message regarding '{title}'.\n\n"
                 f"We have reviewed your request and will respond shortly.\n\n"
                 f"Original: {body[:200]}",
            author=self.AGENT_NAME,
        )

    def draft_social_post(self, task_data: dict):
        """Create a social media post draft using SocialDrafter."""
        from Platinum.src.social_client import SocialDrafter
        title = task_data.get("title", "Update")
        drafter = SocialDrafter()
        social_draft = drafter.create_draft(
            content=task_data.get("body", title),
            platform=task_data.get("platform", "twitter"),
            hashtags=task_data.get("hashtags", []),
        )
        return self.draft_manager.create_draft(
            domain="social",
            title=title,
            body=drafter.draft_to_json(social_draft),
            author=self.AGENT_NAME,
        )

    def draft_accounting_entry(self, task_data: dict):
        """Create an accounting entry draft (optionally via Odoo)."""
        title = task_data.get("title", "Entry")

        # Try to create draft invoice in Odoo if configured
        odoo_draft = None
        if self.settings.has_odoo and task_data.get("partner_id"):
            try:
                from Platinum.src.odoo_client import OdooClient, OdooInvoiceLine
                client = OdooClient(self.settings)
                if client.connect():
                    lines = []
                    for line in task_data.get("lines", []):
                        lines.append(OdooInvoiceLine(
                            product_id=line.get("product_id", 1),
                            name=line.get("name", title),
                            quantity=line.get("quantity", 1),
                            price_unit=line.get("price_unit", task_data.get("amount", 0)),
                        ))
                    if not lines:
                        lines = [OdooInvoiceLine(
                            product_id=1, name=title,
                            quantity=1, price_unit=task_data.get("amount", 0),
                        )]
                    odoo_draft = client.create_draft_invoice(
                        partner_id=task_data["partner_id"],
                        lines=lines,
                        ref=task_data.get("body", title),
                    )
                    self._log_action("odoo_draft", f"Created Odoo draft invoice: {odoo_draft['id']}")
            except Exception as e:
                self._log_action("odoo_error", f"Odoo draft failed: {e}")

        body_data = {
            "type": "draft_entry",
            "description": task_data.get("body", title),
            "amount": task_data.get("amount", 0),
            "category": task_data.get("category", "general"),
        }
        if odoo_draft:
            body_data["odoo_invoice_id"] = odoo_draft["id"]

        return self.draft_manager.create_draft(
            domain="accounting",
            title=title,
            body=json.dumps(body_data, indent=2),
            author=self.AGENT_NAME,
        )

    def triage_inbox(self) -> list:
        """Triage email inbox via IMAP - creates task files for unread messages.

        Returns:
            List of created task file paths.
        """
        if not self.settings.has_imap:
            self._log_action("triage_skip", "IMAP credentials not configured")
            return []

        if self._email_reader is None:
            from Platinum.src.email_client import EmailReader
            self._email_reader = EmailReader(self.settings)

        try:
            created = self._email_reader.triage_inbox()
            self._log_action("triage", f"Created {len(created)} email tasks from inbox")
            return created
        except Exception as e:
            self._log_action("triage_error", f"Inbox triage failed: {e}")
            return []

    def run_once(self) -> list:
        """Single iteration: triage inbox, scan, claim, draft, submit. Returns list of draft IDs."""
        self.heartbeat.beat()
        draft_ids = []

        # Triage email inbox first
        self.triage_inbox()

        available = self.scan_needs_action()
        self._log_action("scan", f"Found {len(available)} available tasks")

        for task_file in available:
            draft_id = self.process_task(task_file)
            if draft_id:
                draft_ids.append(draft_id)

        return draft_ids

    def get_log(self) -> list:
        """Return the agent's action log."""
        return self._log.copy()
