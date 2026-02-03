"""
Integration test for the Platinum demo workflow.
Verifies all 7 demo steps complete and audit trail is generated.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Platinum.src.demo import run_demo


@pytest.fixture
def demo_vault(tmp_path):
    """Create a temporary vault with Platinum structure for demo."""
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
    (platinum / "Signals").mkdir(parents=True)
    return tmp_path


class TestDemoWorkflow:
    def test_demo_completes_all_steps(self, demo_vault):
        result = run_demo(str(demo_vault))
        assert result["success"] is True
        assert len(result["steps"]) == 7

    def test_demo_creates_task_id(self, demo_vault):
        result = run_demo(str(demo_vault))
        assert result["task_id"] is not None
        assert result["task_id"].startswith("DEMO-")

    def test_demo_creates_draft(self, demo_vault):
        result = run_demo(str(demo_vault))
        assert result["draft_id"] is not None
        assert result["draft_id"].startswith("DRAFT-")

    def test_demo_audit_trail_exists(self, demo_vault):
        result = run_demo(str(demo_vault))
        assert len(result["audit_trail"]) > 0

    def test_demo_log_file_created(self, demo_vault):
        run_demo(str(demo_vault))
        log_file = demo_vault / "Platinum" / "Logs" / "demo_execution.log"
        assert log_file.exists()
        data = json.loads(log_file.read_text())
        assert data["steps_completed"] == 7
        assert data["secret_guard_verified"] is True

    def test_demo_done_directory_populated(self, demo_vault):
        run_demo(str(demo_vault))
        done_dir = demo_vault / "Platinum" / "Done"
        done_files = list(done_dir.glob("DRAFT-*.json"))
        assert len(done_files) >= 1

    def test_demo_step_descriptions(self, demo_vault):
        result = run_demo(str(demo_vault))
        step_descriptions = [s["description"] for s in result["steps"]]
        assert "Email task created in Needs_Action/email/" in step_descriptions
        assert "Cloud Agent scanned Needs_Action/" in step_descriptions
        assert "Audit trail recorded" in step_descriptions
