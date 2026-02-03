"""
VaultSync - Git-based vault synchronization between agents.

Reusable Platinum Skill: Synchronizes vault state between Cloud and Local
agents using git pull/push. Enforces file-type filtering to prevent
secret leakage during sync operations.

Usage:
    sync = VaultSync("/path/to/vault")
    result = sync.sync()
    print(result.status, result.message)
"""

import subprocess
import os
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


# File extensions allowed for sync (never sync secrets)
ALLOWED_EXTENSIONS = {".md", ".json", ".txt", ".yaml", ".yml", ".toml", ".cfg", ".log"}
BLOCKED_PATTERNS = [
    ".env", "*.key", "*.pem", "*.p12", "*.pfx", "*.jks",
    "*.secret", "*.token", "*.credentials",
    "whatsapp_session/*", "banking/*", "payment_tokens/*",
]


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    status: str  # "pulled", "pushed", "synced", "conflict", "error"
    message: str
    files_changed: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class VaultSync:
    """Git-based vault synchronization between agents."""

    def __init__(self, vault_path: str, remote: str = "origin", branch: str = "main"):
        self.vault_path = Path(vault_path)
        self.remote = remote
        self.branch = branch
        self._sync_log: List[dict] = []

    def _run_git(self, *args) -> tuple:
        """Run a git command and return (returncode, stdout, stderr)."""
        cmd = ["git", "-C", str(self.vault_path)] + list(args)
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return 1, "", "Git command timed out"
        except FileNotFoundError:
            return 1, "", "Git not found"

    def _is_allowed_file(self, filepath: str) -> bool:
        """Check if file is allowed for sync (not a secret)."""
        path = Path(filepath)
        ext = path.suffix.lower()
        name = path.name.lower()

        # Block known secret patterns
        for pattern in BLOCKED_PATTERNS:
            if "*" in pattern:
                # Glob-style pattern
                base = pattern.replace("*", "")
                if name.endswith(base.lstrip("*")) or filepath.startswith(pattern.rstrip("/*")):
                    return False
            elif name == pattern or name.startswith(pattern):
                return False

        # Only allow known safe extensions
        if ext and ext not in ALLOWED_EXTENSIONS:
            return False

        return True

    def pull(self) -> SyncResult:
        """Pull latest vault state from remote."""
        code, out, err = self._run_git("pull", self.remote, self.branch)
        if code == 0:
            files = self._parse_changed_files(out)
            result = SyncResult(
                success=True, status="pulled",
                message=f"Pull successful: {out or 'Already up to date'}",
                files_changed=files
            )
        else:
            result = SyncResult(
                success=False, status="error",
                message=f"Pull failed: {err}"
            )
        self._log_sync("pull", result)
        return result

    def push(self, message: str = "Vault sync") -> SyncResult:
        """Stage allowed files and push to remote."""
        # Get modified/untracked files
        status = self.get_status()
        allowed_files = [
            f for f in status.get("modified", []) + status.get("untracked", [])
            if self._is_allowed_file(f)
        ]

        if not allowed_files:
            return SyncResult(
                success=True, status="pushed",
                message="No allowed files to push"
            )

        # Stage only allowed files
        for f in allowed_files:
            self._run_git("add", f)

        # Commit
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"{message} [{timestamp}]"
        code, out, err = self._run_git("commit", "-m", commit_msg)
        if code != 0 and "nothing to commit" not in err + out:
            return SyncResult(
                success=False, status="error",
                message=f"Commit failed: {err}"
            )

        # Push
        code, out, err = self._run_git("push", self.remote, self.branch)
        if code == 0:
            result = SyncResult(
                success=True, status="pushed",
                message=f"Pushed {len(allowed_files)} files",
                files_changed=allowed_files
            )
        else:
            result = SyncResult(
                success=False, status="error",
                message=f"Push failed: {err}"
            )
        self._log_sync("push", result)
        return result

    def sync(self) -> SyncResult:
        """Full sync: pull then push."""
        pull_result = self.pull()
        if not pull_result.success and "conflict" not in pull_result.message.lower():
            return pull_result

        push_result = self.push()
        all_files = pull_result.files_changed + push_result.files_changed

        result = SyncResult(
            success=pull_result.success and push_result.success,
            status="synced" if push_result.success else "error",
            message=f"Sync: {pull_result.message} | {push_result.message}",
            files_changed=all_files
        )
        self._log_sync("sync", result)
        return result

    def get_status(self) -> dict:
        """Get modified and untracked files in the vault."""
        code, out, _ = self._run_git("status", "--porcelain")
        modified = []
        untracked = []
        if code == 0 and out:
            for line in out.splitlines():
                if len(line) >= 3:
                    status_code = line[:2].strip()
                    filepath = line[3:].strip()
                    if status_code == "??":
                        untracked.append(filepath)
                    else:
                        modified.append(filepath)
        return {"modified": modified, "untracked": untracked}

    def get_conflicts(self) -> list:
        """Detect merge conflicts."""
        code, out, _ = self._run_git("diff", "--name-only", "--diff-filter=U")
        if code == 0 and out:
            return out.splitlines()
        return []

    def resolve_conflict(self, file: str, strategy: str = "ours") -> bool:
        """Resolve a merge conflict using specified strategy."""
        if strategy not in ("ours", "theirs"):
            return False
        code, _, _ = self._run_git("checkout", f"--{strategy}", "--", file)
        if code == 0:
            self._run_git("add", file)
            return True
        return False

    def get_sync_log(self, limit: int = 10) -> list:
        """Get recent sync history."""
        return self._sync_log[-limit:]

    def _parse_changed_files(self, output: str) -> list:
        """Parse git output for changed file names."""
        files = []
        for line in output.splitlines():
            line = line.strip()
            if "|" in line:
                parts = line.split("|")
                if parts:
                    files.append(parts[0].strip())
        return files

    def _log_sync(self, operation: str, result: SyncResult) -> None:
        """Log a sync operation."""
        self._sync_log.append({
            "operation": operation,
            "success": result.success,
            "status": result.status,
            "message": result.message,
            "files_changed": len(result.files_changed),
            "timestamp": result.timestamp,
        })

    def validate_sync_files(self, files: List[str]) -> List[str]:
        """Filter a list of files to only those allowed for sync."""
        return [f for f in files if self._is_allowed_file(f)]
