"""
Tests for HealthMonitor.
"""

import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from datetime import datetime

from Platinum.src.health_monitor import HealthMonitor, HealthCheck, HealthStatus
from Platinum.src.health_monitor_daemon import HealthMonitorDaemon


@pytest.fixture
def mock_settings(tmp_path):
    return SimpleNamespace(
        AGENT_ROLE="local",
        VAULT_PATH=str(tmp_path),
        HEALTH_CHECK_INTERVAL=60,
        HEALTH_ALERT_EMAIL="admin@example.com",
        HEALTH_CLOUD_URL="https://cloud.example.com",
        HEALTH_API_URL="http://localhost:8000",
        ODOO_URL="http://localhost:8069",
        HEARTBEAT_INTERVAL=30,
        is_local=True,
        is_cloud=False,
        has_smtp=False,
        IMAP_USER="", IMAP_PASSWORD="",
        SMTP_HOST="", SMTP_PORT=587, SMTP_USER="", SMTP_PASSWORD="",
    )


@pytest.fixture
def mock_settings_no_cloud(tmp_path):
    return SimpleNamespace(
        AGENT_ROLE="local",
        VAULT_PATH=str(tmp_path),
        HEALTH_CHECK_INTERVAL=60,
        HEALTH_ALERT_EMAIL="",
        HEALTH_CLOUD_URL="",
        HEALTH_API_URL="http://localhost:8000",
        ODOO_URL="",
        HEARTBEAT_INTERVAL=30,
        is_local=True,
        is_cloud=False,
        has_smtp=False,
        IMAP_USER="", IMAP_PASSWORD="",
        SMTP_HOST="", SMTP_PORT=587, SMTP_USER="", SMTP_PASSWORD="",
    )


@pytest.fixture
def monitor(mock_settings):
    return HealthMonitor(mock_settings)


@pytest.fixture
def monitor_minimal(mock_settings_no_cloud):
    return HealthMonitor(mock_settings_no_cloud)


class TestHealthCheck:

    def test_health_check_dataclass(self):
        check = HealthCheck(
            name="test",
            target="http://localhost",
            healthy=True,
            message="OK",
            response_time_ms=42.5,
        )
        assert check.name == "test"
        assert check.healthy is True
        assert check.response_time_ms == 42.5

    def test_health_status_dataclass(self):
        checks = [
            HealthCheck(name="a", target="x", healthy=True, message="ok"),
            HealthCheck(name="b", target="y", healthy=False, message="down"),
        ]
        status = HealthStatus(
            overall_healthy=False,
            checks=checks,
            alerts=["b is down"],
        )
        assert status.overall_healthy is False
        assert len(status.checks) == 2
        assert len(status.alerts) == 1


class TestHealthMonitor:

    @patch("urllib.request.urlopen")
    def test_check_api_health_success(self, mock_urlopen, monitor):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        check = monitor.check_api_health()
        assert check.name == "api_health"
        assert check.healthy is True

    @patch("urllib.request.urlopen")
    def test_check_api_health_failure(self, mock_urlopen, monitor):
        mock_urlopen.side_effect = Exception("Connection refused")
        check = monitor.check_api_health()
        assert check.healthy is False
        assert "unreachable" in check.message.lower()

    def test_check_cloud_vm_not_configured(self, monitor_minimal):
        check = monitor_minimal.check_cloud_vm()
        assert check.healthy is True
        assert "not configured" in check.message.lower()

    @patch("urllib.request.urlopen")
    def test_check_cloud_vm_success(self, mock_urlopen, monitor):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        check = monitor.check_cloud_vm()
        assert check.healthy is True

    @patch("urllib.request.urlopen")
    def test_check_cloud_vm_failure(self, mock_urlopen, monitor):
        mock_urlopen.side_effect = Exception("Timeout")
        check = monitor.check_cloud_vm()
        assert check.healthy is False

    def test_check_odoo_not_configured(self, monitor_minimal):
        check = monitor_minimal.check_odoo()
        assert check.healthy is True
        assert "not configured" in check.message.lower()

    def test_check_agent_heartbeats_none(self, monitor):
        check = monitor.check_agent_heartbeats()
        assert check.healthy is True
        assert "not be running" in check.message.lower() or "No agent" in check.message

    def test_check_agent_heartbeats_healthy(self, mock_settings, tmp_path):
        # Create a fresh heartbeat file
        updates_dir = tmp_path / "Platinum" / "Updates"
        updates_dir.mkdir(parents=True, exist_ok=True)
        hb_file = updates_dir / "cloud_heartbeat.json"
        hb_file.write_text(json.dumps({
            "agent_name": "cloud",
            "status": "online",
            "current_task": None,
            "timestamp": datetime.utcnow().isoformat(),
            "interval": 30,
        }), encoding="utf-8")

        monitor = HealthMonitor(mock_settings)
        check = monitor.check_agent_heartbeats()
        assert check.healthy is True

    def test_check_agent_heartbeats_stale(self, mock_settings, tmp_path):
        updates_dir = tmp_path / "Platinum" / "Updates"
        updates_dir.mkdir(parents=True, exist_ok=True)
        hb_file = updates_dir / "cloud_heartbeat.json"
        hb_file.write_text(json.dumps({
            "agent_name": "cloud",
            "status": "online",
            "current_task": None,
            "timestamp": "2020-01-01T00:00:00",
            "interval": 30,
        }), encoding="utf-8")

        monitor = HealthMonitor(mock_settings)
        check = monitor.check_agent_heartbeats()
        assert check.healthy is False
        assert "unhealthy" in check.message.lower()

    @patch.object(HealthMonitor, "check_api_health")
    @patch.object(HealthMonitor, "check_cloud_vm")
    @patch.object(HealthMonitor, "check_odoo")
    @patch.object(HealthMonitor, "check_agent_heartbeats")
    def test_run_checks_all_healthy(self, mock_hb, mock_odoo, mock_cloud, mock_api, monitor):
        for m in (mock_api, mock_cloud, mock_odoo, mock_hb):
            m.return_value = HealthCheck(name="test", target="x", healthy=True, message="ok")

        status = monitor.run_checks()
        assert status.overall_healthy is True
        assert len(status.checks) == 4
        assert len(status.alerts) == 0

    @patch.object(HealthMonitor, "check_api_health")
    @patch.object(HealthMonitor, "check_cloud_vm")
    @patch.object(HealthMonitor, "check_odoo")
    @patch.object(HealthMonitor, "check_agent_heartbeats")
    def test_run_checks_with_alert(self, mock_hb, mock_odoo, mock_cloud, mock_api, monitor):
        mock_api.return_value = HealthCheck(name="api", target="x", healthy=False, message="down")
        mock_cloud.return_value = HealthCheck(name="cloud", target="x", healthy=True, message="ok")
        mock_odoo.return_value = HealthCheck(name="odoo", target="x", healthy=True, message="ok")
        mock_hb.return_value = HealthCheck(name="hb", target="x", healthy=True, message="ok")

        status = monitor.run_checks()
        assert status.overall_healthy is False
        assert len(status.alerts) == 1
        assert "api" in status.alerts[0].lower()

    def test_write_status(self, monitor, tmp_path):
        status = HealthStatus(
            overall_healthy=True,
            checks=[HealthCheck(name="test", target="x", healthy=True, message="ok")],
        )
        path = monitor.write_status(status)
        assert Path(path).exists()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert data["overall_healthy"] is True

    def test_get_status_dict(self, monitor):
        status = HealthStatus(
            overall_healthy=False,
            checks=[HealthCheck(name="a", target="x", healthy=False, message="err")],
            alerts=["alert1"],
        )
        d = monitor.get_status_dict(status)
        assert d["overall_healthy"] is False
        assert len(d["checks"]) == 1
        assert d["alerts"] == ["alert1"]

    def test_handle_alerts_creates_task_file(self, monitor, tmp_path):
        monitor._handle_alerts(["Test alert"])
        monitoring_dir = tmp_path / "Platinum" / "Needs_Action" / "monitoring"
        files = list(monitoring_dir.glob("HEALTH-*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert data["domain"] == "monitoring"

    def test_alert_history(self, monitor, tmp_path):
        assert monitor.get_alert_history() == []
        monitor._handle_alerts(["Test"])
        assert len(monitor.get_alert_history()) == 1


class TestHealthMonitorDaemon:

    def test_daemon_init(self, mock_settings):
        daemon = HealthMonitorDaemon(settings=mock_settings)
        assert daemon.monitor is not None

    def test_daemon_run_once(self, mock_settings):
        daemon = HealthMonitorDaemon(settings=mock_settings)
        # Should not raise
        with patch.object(daemon.monitor, "run_checks") as mock_checks:
            mock_checks.return_value = HealthStatus(
                overall_healthy=True,
                checks=[],
            )
            with patch.object(daemon.monitor, "write_status"):
                daemon.run_once()

    def test_daemon_stop(self, mock_settings):
        daemon = HealthMonitorDaemon(settings=mock_settings)
        daemon._running = True
        daemon.stop()
        assert daemon._running is False
