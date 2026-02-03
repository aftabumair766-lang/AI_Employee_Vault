"""
Unit tests for all 5 Platinum reusable skills.

Tests:
- VaultSync: file filtering, status
- DraftManager: create, submit, approve, reject
- ClaimManager: claim, release, double-claim prevention
- AgentHeartbeat: beat, is_alive, timeout detection
- SecretGuard: cloud blocks secrets, local allows all
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Platinum.src.vault_sync import VaultSync, ALLOWED_EXTENSIONS
from Platinum.src.draft_manager import DraftManager, Draft
from Platinum.src.claim_manager import ClaimManager
from Platinum.src.agent_heartbeat import AgentHeartbeat
from Platinum.src.secret_guard import SecretGuard


# ========== FIXTURES ==========

@pytest.fixture
def vault_dir(tmp_path):
    """Create a temporary vault directory with Platinum structure."""
    platinum = tmp_path / "Platinum"
    for domain in ("email", "social", "accounting", "monitoring"):
        (platinum / "Needs_Action" / domain).mkdir(parents=True)
        (platinum / "Pending_Approval" / domain).mkdir(parents=True)
        (platinum / "Plans" / domain).mkdir(parents=True)
    for agent in ("cloud", "local"):
        (platinum / "In_Progress" / agent).mkdir(parents=True)
    (platinum / "Updates").mkdir(parents=True)
    (platinum / "Done").mkdir(parents=True)
    (platinum / "Logs").mkdir(parents=True)
    return tmp_path


# ========== VaultSync Tests ==========

class TestVaultSync:
    def test_allowed_file_md(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        assert sync._is_allowed_file("README.md")

    def test_allowed_file_json(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        assert sync._is_allowed_file("config.json")

    def test_blocked_file_env(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        assert not sync._is_allowed_file(".env")

    def test_blocked_file_key(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        assert not sync._is_allowed_file("vault.key")

    def test_blocked_file_pem(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        assert not sync._is_allowed_file("cert.pem")

    def test_validate_sync_files(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        files = ["README.md", ".env", "config.json", "secret.key", "notes.txt"]
        safe = sync.validate_sync_files(files)
        assert "README.md" in safe
        assert "config.json" in safe
        assert "notes.txt" in safe
        assert ".env" not in safe
        assert "secret.key" not in safe

    def test_get_status_empty(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        status = sync.get_status()
        assert "modified" in status
        assert "untracked" in status

    def test_sync_log_empty(self, vault_dir):
        sync = VaultSync(str(vault_dir))
        assert sync.get_sync_log() == []


# ========== DraftManager Tests ==========

class TestDraftManager:
    def test_create_draft(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        draft = dm.create_draft("email", "Test Subject", "Test body", "cloud")
        assert draft.draft_id.startswith("DRAFT-")
        assert draft.domain == "email"
        assert draft.title == "Test Subject"
        assert draft.status == "draft"
        assert draft.author == "cloud"

    def test_submit_for_approval(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        draft = dm.create_draft("email", "Test", "Body", "cloud")
        result = dm.submit_for_approval(draft.draft_id)
        assert result is True

        # Verify it moved to Pending_Approval
        pending = dm.list_pending("email")
        assert len(pending) == 1
        assert pending[0].draft_id == draft.draft_id
        assert pending[0].status == "pending_approval"

    def test_approve_draft(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        draft = dm.create_draft("email", "Test", "Body", "cloud")
        dm.submit_for_approval(draft.draft_id)
        approved = dm.approve(draft.draft_id, "local")
        assert approved is not None
        assert approved.status == "approved"
        assert approved.approver == "local"

    def test_reject_draft(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        draft = dm.create_draft("social", "Post", "Content", "cloud")
        dm.submit_for_approval(draft.draft_id)
        rejected = dm.reject(draft.draft_id, "local", "Not appropriate")
        assert rejected is not None
        assert rejected.status == "rejected"
        assert rejected.reject_reason == "Not appropriate"

    def test_get_draft(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        draft = dm.create_draft("email", "Find me", "Body", "cloud")
        found = dm.get_draft(draft.draft_id)
        assert found is not None
        assert found.title == "Find me"

    def test_get_draft_not_found(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        found = dm.get_draft("DRAFT-NONEXISTENT")
        assert found is None

    def test_audit_trail(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        draft = dm.create_draft("email", "Audit Test", "Body", "cloud")
        dm.submit_for_approval(draft.draft_id)
        dm.approve(draft.draft_id, "local")
        trail = dm.get_audit_trail(draft.draft_id)
        assert len(trail) == 3  # created, submitted, approved
        assert trail[0]["action"] == "created"
        assert trail[1]["action"] == "submitted_for_approval"
        assert trail[2]["action"] == "approved"

    def test_list_pending_all_domains(self, vault_dir):
        dm = DraftManager(str(vault_dir))
        dm.create_draft("email", "E1", "B", "cloud")
        dm.create_draft("social", "S1", "B", "cloud")
        # Submit both
        drafts = [dm.create_draft("email", "E2", "B", "cloud"),
                  dm.create_draft("social", "S2", "B", "cloud")]
        for d in drafts:
            dm.submit_for_approval(d.draft_id)
        pending = dm.list_pending()
        assert len(pending) == 2


# ========== ClaimManager Tests ==========

class TestClaimManager:
    def _create_task_file(self, vault_dir, domain, task_id):
        """Helper: create a task file in Needs_Action."""
        task_dir = vault_dir / "Platinum" / "Needs_Action" / domain
        task_dir.mkdir(parents=True, exist_ok=True)
        task_file = task_dir / f"{task_id}.json"
        task_file.write_text(json.dumps({
            "task_id": task_id, "domain": domain,
            "title": f"Test {task_id}", "status": "needs_action",
        }), encoding="utf-8")
        return f"Needs_Action/{domain}/{task_id}.json"

    def test_list_available(self, vault_dir):
        cm = ClaimManager(str(vault_dir))
        self._create_task_file(vault_dir, "email", "T001")
        self._create_task_file(vault_dir, "email", "T002")
        available = cm.list_available("email")
        assert len(available) == 2

    def test_claim_success(self, vault_dir):
        cm = ClaimManager(str(vault_dir))
        rel = self._create_task_file(vault_dir, "email", "T001")
        result = cm.claim(rel, "cloud")
        assert result is True
        assert cm.is_claimed("T001.json")
        assert cm.get_owner("T001.json") == "cloud"

    def test_claim_already_claimed(self, vault_dir):
        cm = ClaimManager(str(vault_dir))
        rel = self._create_task_file(vault_dir, "email", "T001")
        cm.claim(rel, "cloud")
        # File no longer in Needs_Action, can't claim again
        result = cm.claim(rel, "local")
        assert result is False

    def test_release(self, vault_dir):
        cm = ClaimManager(str(vault_dir))
        rel = self._create_task_file(vault_dir, "email", "T001")
        cm.claim(rel, "cloud")
        result = cm.release("T001.json", "cloud")
        assert result is True
        assert not cm.is_claimed("T001.json")

    def test_list_claimed_by(self, vault_dir):
        cm = ClaimManager(str(vault_dir))
        self._create_task_file(vault_dir, "email", "T001")
        self._create_task_file(vault_dir, "social", "T002")
        cm.claim("Needs_Action/email/T001.json", "cloud")
        cm.claim("Needs_Action/social/T002.json", "cloud")
        claimed = cm.list_claimed_by("cloud")
        assert len(claimed) == 2

    def test_claim_missing_file(self, vault_dir):
        cm = ClaimManager(str(vault_dir))
        result = cm.claim("Needs_Action/email/NONEXIST.json", "cloud")
        assert result is False

    def test_get_owner_unclaimed(self, vault_dir):
        cm = ClaimManager(str(vault_dir))
        assert cm.get_owner("NONEXIST.json") is None


# ========== AgentHeartbeat Tests ==========

class TestAgentHeartbeat:
    def test_beat_creates_file(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir))
        hb.beat()
        path = vault_dir / "Platinum" / "Updates" / "cloud_heartbeat.json"
        assert path.exists()

    def test_beat_with_task(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir))
        hb.beat(current_task="DRAFT-ABC")
        data = json.loads(
            (vault_dir / "Platinum" / "Updates" / "cloud_heartbeat.json").read_text()
        )
        assert data["current_task"] == "DRAFT-ABC"

    def test_is_alive_true(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir))
        hb.beat()
        assert hb.is_alive("cloud", timeout=60) is True

    def test_is_alive_false_no_file(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir))
        assert hb.is_alive("nonexistent", timeout=60) is False

    def test_is_alive_stale(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir))
        # Write a heartbeat with old timestamp
        path = vault_dir / "Platinum" / "Updates" / "cloud_heartbeat.json"
        old_time = (datetime.utcnow() - timedelta(seconds=120)).isoformat()
        path.write_text(json.dumps({
            "agent_name": "cloud", "status": "online",
            "timestamp": old_time, "current_task": None,
        }))
        assert hb.is_alive("cloud", timeout=60) is False

    def test_get_status_online(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir))
        hb.beat()
        status = hb.get_status("cloud")
        assert status["status"] == "online"
        assert status["agent_name"] == "cloud"

    def test_get_status_offline(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir))
        status = hb.get_status("nonexistent")
        assert status["status"] == "offline"

    def test_get_all_agents(self, vault_dir):
        hb_cloud = AgentHeartbeat("cloud", str(vault_dir))
        hb_local = AgentHeartbeat("local", str(vault_dir))
        hb_cloud.beat()
        hb_local.beat()
        agents = hb_cloud.get_all_agents()
        assert len(agents) == 2
        names = {a["agent_name"] for a in agents}
        assert "cloud" in names
        assert "local" in names

    def test_background_heartbeat(self, vault_dir):
        hb = AgentHeartbeat("cloud", str(vault_dir), interval=1)
        hb.start_background()
        time.sleep(1.5)
        hb.stop_background()
        assert hb.is_alive("cloud", timeout=5)


# ========== SecretGuard Tests ==========

class TestSecretGuard:
    def test_cloud_blocks_env(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access(".env") is False

    def test_cloud_blocks_key(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access("vault.key") is False

    def test_cloud_blocks_pem(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access("cert.pem") is False

    def test_cloud_blocks_banking(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access("banking/credentials") is False

    def test_cloud_blocks_payment_tokens(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access("payment_tokens/stripe") is False

    def test_cloud_blocks_whatsapp(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access("whatsapp_session/session.dat") is False

    def test_cloud_allows_email_draft(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access("email_draft") is True

    def test_cloud_allows_task_file(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.can_access("task_file") is True

    def test_local_allows_everything(self):
        guard = SecretGuard(agent_role="local")
        assert guard.can_access(".env") is True
        assert guard.can_access("vault.key") is True
        assert guard.can_access("banking/creds") is True
        assert guard.can_access("payment_tokens/stripe") is True

    def test_validate_sync_files(self):
        guard = SecretGuard(agent_role="cloud")
        files = ["readme.md", ".env", "config.json", "secret.key"]
        safe = guard.validate_sync_files(files)
        assert "readme.md" in safe
        assert "config.json" in safe
        assert ".env" not in safe
        assert "secret.key" not in safe

    def test_audit_log(self):
        guard = SecretGuard(agent_role="cloud")
        guard.can_access(".env")
        guard.can_access("email_draft")
        log = guard.get_audit_log()
        assert len(log) == 2
        assert log[0]["allowed"] is False
        assert log[1]["allowed"] is True

    def test_invalid_role(self):
        with pytest.raises(ValueError):
            SecretGuard(agent_role="invalid")

    def test_is_secret_file(self):
        guard = SecretGuard(agent_role="cloud")
        assert guard.is_secret_file(".env") is True
        assert guard.is_secret_file("readme.md") is False

    def test_get_blocked_patterns_cloud(self):
        guard = SecretGuard(agent_role="cloud")
        patterns = guard.get_blocked_patterns()
        assert len(patterns) > 0

    def test_get_blocked_patterns_local(self):
        guard = SecretGuard(agent_role="local")
        patterns = guard.get_blocked_patterns()
        assert len(patterns) == 0
