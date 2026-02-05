"""
Sync Daemon - Periodic git sync between Cloud and Local.

Runs continuously, pulling and pushing vault changes at regular intervals.
Supports SSH key authentication for secure git operations.

Usage:
    python -m Platinum.src.sync_daemon
"""

import signal
import sys
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("platinum.sync_daemon")


class SyncDaemon:
    """Daemon process for periodic vault synchronization."""

    def __init__(self, settings=None):
        if settings is None:
            from Platinum.src.config import get_settings
            settings = get_settings()
        self.settings = settings
        self._running = False

        from Platinum.src.vault_sync import VaultSync
        self.vault_sync = VaultSync(
            vault_path=settings.VAULT_PATH,
            remote=settings.GIT_REMOTE,
            branch=settings.GIT_BRANCH,
            ssh_key=settings.GIT_SSH_KEY,
        )

    def start(self):
        """Start the sync loop."""
        self._running = True
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        logger.info(
            f"Sync Daemon started "
            f"(interval={self.settings.SYNC_INTERVAL}s, "
            f"remote={self.settings.GIT_REMOTE}/{self.settings.GIT_BRANCH})"
        )

        try:
            while self._running:
                self._run_cycle()
                # Sleep in small intervals for responsive shutdown
                for _ in range(self.settings.SYNC_INTERVAL):
                    if not self._running:
                        break
                    time.sleep(1)
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            logger.info("Sync Daemon stopped")

    def stop(self):
        """Stop the daemon gracefully."""
        self._running = False
        logger.info("Shutdown signal received")

    def _handle_signal(self, signum, frame):
        """Handle SIGINT/SIGTERM."""
        logger.info(f"Signal {signum} received, shutting down...")
        self.stop()

    def _run_cycle(self):
        """Run a single sync cycle."""
        try:
            start = time.time()

            # Pull first
            pull_result = self.vault_sync.pull()
            if pull_result.success:
                logger.info(f"Pull: {pull_result.message}")
            else:
                logger.warning(f"Pull failed: {pull_result.message}")

            # Push changes
            push_result = self.vault_sync.push(message="Cloud sync")
            if push_result.success:
                logger.info(f"Push: {push_result.message}")
            else:
                logger.warning(f"Push failed: {push_result.message}")

            elapsed = time.time() - start
            files_changed = len(pull_result.files_changed) + len(push_result.files_changed)

            logger.info(
                f"Sync cycle complete: {files_changed} files changed ({elapsed:.1f}s)"
            )

            # Write sync status
            self._write_sync_status(pull_result, push_result)

        except Exception as e:
            logger.error(f"Sync cycle failed: {e}")

    def _write_sync_status(self, pull_result, push_result):
        """Write sync status to Platinum/Updates/sync_status.json."""
        import json
        from pathlib import Path

        updates_dir = Path(self.settings.VAULT_PATH) / "Platinum" / "Updates"
        updates_dir.mkdir(parents=True, exist_ok=True)
        status_file = updates_dir / "sync_status.json"

        status = {
            "last_sync": datetime.utcnow().isoformat(),
            "pull": {
                "success": pull_result.success,
                "status": pull_result.status,
                "files_changed": len(pull_result.files_changed),
            },
            "push": {
                "success": push_result.success,
                "status": push_result.status,
                "files_changed": len(push_result.files_changed),
            },
            "remote": f"{self.settings.GIT_REMOTE}/{self.settings.GIT_BRANCH}",
        }
        status_file.write_text(json.dumps(status, indent=2), encoding="utf-8")

    def run_once(self):
        """Run a single cycle (for testing)."""
        self._run_cycle()

    def get_sync_log(self, limit: int = 10) -> list:
        """Get recent sync history from VaultSync."""
        return self.vault_sync.get_sync_log(limit)


def main():
    """Entry point."""
    daemon = SyncDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
