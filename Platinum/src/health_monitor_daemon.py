"""
Health Monitor Daemon - Standalone entry point with signal handling.

Runs health checks periodically and writes status/alerts.

Usage:
    python -m Platinum.src.health_monitor_daemon
    # or
    python Platinum/src/health_monitor_daemon.py
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
logger = logging.getLogger("platinum.health_daemon")


class HealthMonitorDaemon:
    """Daemon process for periodic health monitoring."""

    def __init__(self, settings=None):
        if settings is None:
            from Platinum.src.config import get_settings
            settings = get_settings()
        self.settings = settings
        self._running = False

        from Platinum.src.health_monitor import HealthMonitor
        self.monitor = HealthMonitor(settings)

    def start(self):
        """Start the health monitoring loop."""
        self._running = True
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        logger.info(
            f"Health Monitor Daemon started "
            f"(interval={self.settings.HEALTH_CHECK_INTERVAL}s)"
        )

        try:
            while self._running:
                self._run_cycle()
                # Sleep in small intervals for responsive shutdown
                for _ in range(self.settings.HEALTH_CHECK_INTERVAL):
                    if not self._running:
                        break
                    time.sleep(1)
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            logger.info("Health Monitor Daemon stopped")

    def stop(self):
        """Stop the daemon gracefully."""
        self._running = False
        logger.info("Shutdown signal received")

    def _handle_signal(self, signum, frame):
        """Handle SIGINT/SIGTERM."""
        logger.info(f"Signal {signum} received, shutting down...")
        self.stop()

    def _run_cycle(self):
        """Run a single health check cycle."""
        try:
            start = time.time()
            status = self.monitor.run_checks()
            self.monitor.write_status(status)
            elapsed = time.time() - start

            healthy_count = sum(1 for c in status.checks if c.healthy)
            total = len(status.checks)
            logger.info(
                f"Health check complete: {healthy_count}/{total} healthy, "
                f"{len(status.alerts)} alerts ({elapsed:.1f}s)"
            )
        except Exception as e:
            logger.error(f"Health check cycle failed: {e}")

    def run_once(self):
        """Run a single cycle (for testing)."""
        self._run_cycle()


def main():
    """Entry point."""
    daemon = HealthMonitorDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
