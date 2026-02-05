"""
SecretGuard - Secret boundary enforcement.

Reusable Platinum Skill: Enforces secret access boundaries between Cloud
and Local agents. Cloud agent is blocked from accessing secrets (env files,
keys, payment tokens, etc). Local agent has full executive authority.

Usage:
    guard = SecretGuard(agent_role="cloud")
    if guard.can_access("email_draft"):
        process_draft()
    if not guard.can_access(".env"):
        print("Blocked!")
"""

import os
import re
from datetime import datetime
from typing import List
from pathlib import Path


# Patterns blocked for Cloud agent (never allowed to access)
BLOCKED_PATTERNS = [
    r"\.env$",
    r"\.env\..+$",
    r".*\.key$",
    r".*\.pem$",
    r".*\.p12$",
    r".*\.pfx$",
    r".*\.jks$",
    r".*\.secret$",
    r".*\.token$",
    r".*\.credentials$",
    r"whatsapp_session(/.*)?$",
    r"banking(/.*)?$",
    r"payment_tokens(/.*)?$",
    r"secrets(/.*)?$",
    r"private(/.*)?$",
    r"odoo_admin(/.*)?$",
    r"imap_credentials(/.*)?$",
    r"smtp_credentials(/.*)?$",
]

# Resource types that are always safe for any agent
SAFE_RESOURCES = {
    "email_draft", "social_draft", "accounting_draft",
    "monitoring_report", "task_file", "plan_file",
    "heartbeat", "status_update", "audit_log",
    "markdown", "json_config",
}


class SecretGuard:
    """Enforces secret access boundaries between Cloud and Local agents."""

    def __init__(self, agent_role: str = "cloud"):
        if agent_role not in ("cloud", "local"):
            raise ValueError(f"Invalid agent_role: {agent_role}. Must be 'cloud' or 'local'.")
        self.agent_role = agent_role
        self._blocked_patterns = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]
        self._audit_log: List[dict] = []

    def can_access(self, resource_type: str) -> bool:
        """Check if current agent role is allowed to access a resource.

        Args:
            resource_type: Resource identifier (filename, path, or type name)

        Returns:
            True if access is allowed, False if blocked.
        """
        # Local agent has full access (executive authority)
        if self.agent_role == "local":
            self.audit_access_attempt(resource_type, True)
            return True

        # Check if resource is a known safe type
        if resource_type.lower() in SAFE_RESOURCES:
            self.audit_access_attempt(resource_type, True)
            return True

        # Cloud agent: check against blocked patterns
        for pattern in self._blocked_patterns:
            if pattern.search(resource_type):
                self.audit_access_attempt(resource_type, False)
                return False

        # Not explicitly blocked - allow
        self.audit_access_attempt(resource_type, True)
        return True

    def validate_sync_files(self, files: List[str]) -> List[str]:
        """Filter out secret files from a list of files to sync.

        Args:
            files: List of file paths to validate

        Returns:
            List of files that are safe to sync (secrets removed).
        """
        safe_files = []
        for f in files:
            if self.can_access(f):
                safe_files.append(f)
        return safe_files

    def get_blocked_patterns(self) -> List[str]:
        """Return the list of blocked patterns for the current role."""
        if self.agent_role == "local":
            return []  # Local has no restrictions
        return BLOCKED_PATTERNS.copy()

    def audit_access_attempt(self, resource: str, allowed: bool) -> None:
        """Log an access attempt for auditing."""
        self._audit_log.append({
            "agent_role": self.agent_role,
            "resource": resource,
            "allowed": allowed,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_audit_log(self) -> List[dict]:
        """Return the access attempt audit log."""
        return self._audit_log.copy()

    def is_secret_file(self, filepath: str) -> bool:
        """Check if a file path matches any secret pattern."""
        for pattern in self._blocked_patterns:
            if pattern.search(filepath):
                return True
        return False
