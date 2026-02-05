"""
HealthMonitor - Monitors system health and generates alerts.

Checks: Cloud VM HTTP ping, API /health, Odoo URL, agent heartbeat staleness.
Alerts via email (using EmailSender) or task files in Needs_Action/monitoring/.
Writes status to Platinum/Updates/health_status.json.

Usage:
    from Platinum.src.config import get_settings
    monitor = HealthMonitor(get_settings())
    status = monitor.run_checks()
    monitor.write_status(status)
"""

import json
import logging
import time
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger("platinum.health_monitor")


@dataclass
class HealthCheck:
    """Result of a single health check."""
    name: str
    target: str
    healthy: bool
    message: str
    response_time_ms: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class HealthStatus:
    """Aggregate health status."""
    overall_healthy: bool
    checks: List[HealthCheck]
    alerts: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class HealthMonitor:
    """Monitors system components and generates health reports."""

    def __init__(self, settings):
        self.settings = settings
        self.vault_path = Path(settings.VAULT_PATH)
        self._alert_history: List[dict] = []

    def check_api_health(self) -> HealthCheck:
        """Check if the FastAPI server is responding."""
        url = f"{self.settings.HEALTH_API_URL}/health"
        try:
            import urllib.request
            start = time.time()
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                elapsed = (time.time() - start) * 1000
                return HealthCheck(
                    name="api_health",
                    target=url,
                    healthy=resp.status == 200,
                    message=f"API responded with {resp.status}",
                    response_time_ms=round(elapsed, 1),
                )
        except Exception as e:
            return HealthCheck(
                name="api_health",
                target=url,
                healthy=False,
                message=f"API unreachable: {e}",
            )

    def check_cloud_vm(self) -> HealthCheck:
        """HTTP ping the Cloud VM."""
        url = self.settings.HEALTH_CLOUD_URL
        if not url:
            return HealthCheck(
                name="cloud_vm",
                target="(not configured)",
                healthy=True,
                message="Cloud VM URL not configured, skipping",
            )
        try:
            import urllib.request
            start = time.time()
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                elapsed = (time.time() - start) * 1000
                return HealthCheck(
                    name="cloud_vm",
                    target=url,
                    healthy=resp.status in (200, 301, 302),
                    message=f"Cloud VM responded with {resp.status}",
                    response_time_ms=round(elapsed, 1),
                )
        except Exception as e:
            return HealthCheck(
                name="cloud_vm",
                target=url,
                healthy=False,
                message=f"Cloud VM unreachable: {e}",
            )

    def check_odoo(self) -> HealthCheck:
        """Check if Odoo is responding."""
        url = self.settings.ODOO_URL
        if not url:
            return HealthCheck(
                name="odoo",
                target="(not configured)",
                healthy=True,
                message="Odoo URL not configured, skipping",
            )
        try:
            import urllib.request
            start = time.time()
            web_url = f"{url}/web/login"
            req = urllib.request.Request(web_url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                elapsed = (time.time() - start) * 1000
                return HealthCheck(
                    name="odoo",
                    target=url,
                    healthy=resp.status == 200,
                    message=f"Odoo responded with {resp.status}",
                    response_time_ms=round(elapsed, 1),
                )
        except Exception as e:
            return HealthCheck(
                name="odoo",
                target=url,
                healthy=False,
                message=f"Odoo unreachable: {e}",
            )

    def check_agent_heartbeats(self) -> HealthCheck:
        """Check if agent heartbeats are fresh."""
        from Platinum.src.agent_heartbeat import AgentHeartbeat
        summary = AgentHeartbeat.get_health_summary(
            str(self.vault_path),
            interval=self.settings.HEARTBEAT_INTERVAL,
        )
        if not summary:
            return HealthCheck(
                name="agent_heartbeats",
                target="Platinum/Updates/",
                healthy=True,
                message="No agent heartbeats found (agents may not be running)",
            )

        unhealthy = [name for name, info in summary.items() if not info.get("healthy")]
        if unhealthy:
            return HealthCheck(
                name="agent_heartbeats",
                target="Platinum/Updates/",
                healthy=False,
                message=f"Unhealthy agents: {', '.join(unhealthy)}",
            )
        return HealthCheck(
            name="agent_heartbeats",
            target="Platinum/Updates/",
            healthy=True,
            message=f"All {len(summary)} agents healthy",
        )

    def run_checks(self) -> HealthStatus:
        """Run all health checks and return aggregate status."""
        checks = [
            self.check_api_health(),
            self.check_cloud_vm(),
            self.check_odoo(),
            self.check_agent_heartbeats(),
        ]

        alerts = []
        for check in checks:
            if not check.healthy:
                alert_msg = f"[ALERT] {check.name}: {check.message}"
                alerts.append(alert_msg)
                logger.warning(alert_msg)

        overall = all(c.healthy for c in checks)
        status = HealthStatus(
            overall_healthy=overall,
            checks=checks,
            alerts=alerts,
        )

        if alerts:
            self._handle_alerts(alerts)

        return status

    def _handle_alerts(self, alerts: List[str]):
        """Handle health alerts - create monitoring task files."""
        monitoring_dir = self.vault_path / "Platinum" / "Needs_Action" / "monitoring"
        monitoring_dir.mkdir(parents=True, exist_ok=True)

        alert_data = {
            "task_id": f"HEALTH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "domain": "monitoring",
            "title": "Health Alert",
            "body": "\n".join(alerts),
            "status": "NEEDS_ACTION",
            "created_at": datetime.utcnow().isoformat(),
        }
        alert_file = monitoring_dir / f"{alert_data['task_id']}.json"
        alert_file.write_text(json.dumps(alert_data, indent=2), encoding="utf-8")
        self._alert_history.append(alert_data)
        logger.info(f"Health alert created: {alert_data['task_id']}")

        # Send email alert if configured
        if self.settings.HEALTH_ALERT_EMAIL and self.settings.is_local:
            try:
                self._send_email_alert(alerts)
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")

    def _send_email_alert(self, alerts: List[str]):
        """Send health alert via email (Local agent only)."""
        if not self.settings.has_smtp:
            return
        from Platinum.src.email_client import EmailSender
        sender = EmailSender(self.settings)
        sender.send(
            to=self.settings.HEALTH_ALERT_EMAIL,
            subject=f"[AI Employee] Health Alert - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            body=f"Health Monitor detected issues:\n\n" + "\n".join(alerts),
        )

    def write_status(self, status: HealthStatus) -> str:
        """Write health status to Platinum/Updates/health_status.json."""
        updates_dir = self.vault_path / "Platinum" / "Updates"
        updates_dir.mkdir(parents=True, exist_ok=True)
        status_file = updates_dir / "health_status.json"

        data = {
            "overall_healthy": status.overall_healthy,
            "checks": [
                {
                    "name": c.name,
                    "target": c.target,
                    "healthy": c.healthy,
                    "message": c.message,
                    "response_time_ms": c.response_time_ms,
                    "timestamp": c.timestamp,
                }
                for c in status.checks
            ],
            "alerts": status.alerts,
            "timestamp": status.timestamp,
        }
        status_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"Health status written: overall_healthy={status.overall_healthy}")
        return str(status_file)

    def get_status_dict(self, status: HealthStatus) -> dict:
        """Convert HealthStatus to a JSON-serializable dict (for API endpoint)."""
        return {
            "overall_healthy": status.overall_healthy,
            "checks": [
                {
                    "name": c.name,
                    "target": c.target,
                    "healthy": c.healthy,
                    "message": c.message,
                    "response_time_ms": c.response_time_ms,
                }
                for c in status.checks
            ],
            "alerts": status.alerts,
            "timestamp": status.timestamp,
        }

    def get_alert_history(self) -> List[dict]:
        """Return recent alert history."""
        return self._alert_history.copy()
