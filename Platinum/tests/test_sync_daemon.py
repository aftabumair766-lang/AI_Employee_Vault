"""
Tests for SyncDaemon.
"""

import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from Platinum.src.sync_daemon import SyncDaemon
from Platinum.src.vault_sync import SyncResult


@pytest.fixture
def mock_settings(tmp_path):
    return SimpleNamespace(
        VAULT_PATH=str(tmp_path),
        GIT_REMOTE="origin",
        GIT_BRANCH="main",
        GIT_SSH_KEY="",
        SYNC_INTERVAL=60,
    )


@pytest.fixture
def daemon(mock_settings):
    with patch.object(SyncDaemon, "__init__", lambda self, settings: None):
        d = SyncDaemon.__new__(SyncDaemon)
        d.settings = mock_settings
        d._running = False
        d.vault_sync = MagicMock()
        return d


class TestSyncDaemon:

    def test_init(self, mock_settings, tmp_path):
        # Create a minimal test that doesn't need VaultSync mocking
        from Platinum.src.vault_sync import VaultSync
        with patch.object(VaultSync, "__init__", lambda *a, **k: None):
            with patch.object(VaultSync, "pull", return_value=None):
                daemon = SyncDaemon(settings=mock_settings)
                assert daemon.settings.SYNC_INTERVAL == 60

    def test_stop(self, daemon):
        daemon._running = True
        daemon.stop()
        assert daemon._running is False

    def test_run_cycle_success(self, daemon, mock_settings, tmp_path):
        daemon.vault_sync.pull.return_value = SyncResult(
            success=True, status="pulled", message="OK", files_changed=["a.md"]
        )
        daemon.vault_sync.push.return_value = SyncResult(
            success=True, status="pushed", message="OK", files_changed=[]
        )

        daemon._run_cycle()

        daemon.vault_sync.pull.assert_called_once()
        daemon.vault_sync.push.assert_called_once()

        # Check status file was written
        status_file = tmp_path / "Platinum" / "Updates" / "sync_status.json"
        assert status_file.exists()
        data = json.loads(status_file.read_text(encoding="utf-8"))
        assert data["pull"]["success"] is True
        assert data["push"]["success"] is True

    def test_run_cycle_pull_failure(self, daemon):
        daemon.vault_sync.pull.return_value = SyncResult(
            success=False, status="error", message="Network error"
        )
        daemon.vault_sync.push.return_value = SyncResult(
            success=True, status="pushed", message="OK"
        )

        # Should not raise
        daemon._run_cycle()

    def test_run_cycle_push_failure(self, daemon):
        daemon.vault_sync.pull.return_value = SyncResult(
            success=True, status="pulled", message="OK"
        )
        daemon.vault_sync.push.return_value = SyncResult(
            success=False, status="error", message="Push rejected"
        )

        # Should not raise
        daemon._run_cycle()

    def test_run_once(self, daemon):
        daemon.vault_sync.pull.return_value = SyncResult(
            success=True, status="pulled", message="OK"
        )
        daemon.vault_sync.push.return_value = SyncResult(
            success=True, status="pushed", message="OK"
        )

        daemon.run_once()
        daemon.vault_sync.pull.assert_called_once()

    def test_get_sync_log(self, daemon):
        daemon.vault_sync.get_sync_log.return_value = [{"test": "log"}]
        log = daemon.get_sync_log()
        assert len(log) == 1

    def test_handle_signal(self, daemon):
        daemon._running = True
        daemon._handle_signal(2, None)  # SIGINT
        assert daemon._running is False

    def test_write_sync_status(self, daemon, mock_settings, tmp_path):
        pull_result = SyncResult(
            success=True, status="pulled", message="OK",
            files_changed=["file1.md", "file2.json"]
        )
        push_result = SyncResult(
            success=True, status="pushed", message="OK",
            files_changed=["file3.txt"]
        )

        daemon._write_sync_status(pull_result, push_result)

        status_file = tmp_path / "Platinum" / "Updates" / "sync_status.json"
        assert status_file.exists()
        data = json.loads(status_file.read_text(encoding="utf-8"))
        assert data["pull"]["files_changed"] == 2
        assert data["push"]["files_changed"] == 1
        assert data["remote"] == "origin/main"
