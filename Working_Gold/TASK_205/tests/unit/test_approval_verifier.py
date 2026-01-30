"""
Unit tests for approval_verifier.py
TASK_205 Phase 2 - Testing Infrastructure Foundation
Tests CRITICAL-5 Fix: Approval Bypass Risk (CVSS 7.5)
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'))

from approval_verifier import ApprovalVerifier


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestValidateStateTransition:
    """Test state transition validation"""

    def test_transition_requires_approval_with_approval(self):
        """Test transition that requires approval when approval exists"""
        verifier = ApprovalVerifier()
        is_valid, reason = verifier.validate_state_transition(
            'AWAITING_APPROVAL', 'IN_PROGRESS', has_approval=True, task_level='Gold'
        )
        assert is_valid is True
        assert "approved" in reason.lower()

    def test_transition_requires_approval_without_approval(self):
        """Test transition that requires approval when no approval"""
        verifier = ApprovalVerifier()
        is_valid, reason = verifier.validate_state_transition(
            'AWAITING_APPROVAL', 'IN_PROGRESS', has_approval=False, task_level='Gold'
        )
        assert is_valid is False
        assert "requires approval" in reason.lower()

    @pytest.mark.parametrize("from_state,to_state", [
        ('NEEDS_ACTION', 'PLANNING'),
        ('IN_PROGRESS', 'COMPLETED'),
        ('COMPLETED', 'DONE'),
        ('IN_PROGRESS', 'FAILED'),
        ('IN_PROGRESS', 'BLOCKED'),
        ('BLOCKED', 'IN_PROGRESS'),
    ])
    def test_transitions_without_approval(self, from_state, to_state):
        """Test transitions allowed without approval"""
        verifier = ApprovalVerifier()
        is_valid, reason = verifier.validate_state_transition(
            from_state, to_state, has_approval=False, task_level='Gold'
        )
        assert is_valid is True

    def test_bronze_skip_planning(self):
        """Test Bronze level can skip PLANNING"""
        verifier = ApprovalVerifier()
        is_valid, reason = verifier.validate_state_transition(
            'NEEDS_ACTION', 'IN_PROGRESS', has_approval=False, task_level='Bronze'
        )
        assert is_valid is True
        # Bronze can skip planning through normal allowed transitions
        assert "valid" in reason.lower()

    def test_invalid_transition_blocked(self):
        """Test invalid transitions are blocked"""
        verifier = ApprovalVerifier()
        is_valid, reason = verifier.validate_state_transition(
            'COMPLETED', 'IN_PROGRESS', has_approval=False, task_level='Gold'
        )
        assert is_valid is False


@pytest.mark.unit
@pytest.mark.phase2
class TestApprovalTimeout:
    """Test approval timeout checking"""

    def test_timeout_not_expired(self):
        """Test approval timeout not expired"""
        verifier = ApprovalVerifier()
        requested = datetime.now() - timedelta(hours=1)
        is_expired, deadline = verifier.check_approval_timeout(requested, 'Gold', 'MEDIUM')
        assert is_expired is False
        assert deadline > datetime.now()

    def test_timeout_expired(self):
        """Test approval timeout expired"""
        verifier = ApprovalVerifier()
        requested = datetime.now() - timedelta(hours=10)
        is_expired, deadline = verifier.check_approval_timeout(requested, 'Gold', 'MEDIUM')
        assert is_expired is True
        assert deadline < datetime.now()

    @pytest.mark.parametrize("level,hours,should_expire", [
        ('Gold', 3, False),
        ('Gold', 5, True),
        ('Silver', 7, False),
        ('Silver', 9, True),
        ('Bronze', 23, False),
        ('Bronze', 25, True),
    ])
    def test_timeout_by_level(self, level, hours, should_expire):
        """Test timeout varies by level"""
        verifier = ApprovalVerifier()
        requested = datetime.now() - timedelta(hours=hours)
        is_expired, _ = verifier.check_approval_timeout(requested, level, 'MEDIUM')
        assert is_expired == should_expire

    @pytest.mark.parametrize("priority,hours_delta", [
        ('CRITICAL', -2),
        ('HIGH', -1),
        ('MEDIUM', 0),
        ('LOW', 4),
    ])
    def test_priority_adjustments(self, priority, hours_delta):
        """Test priority affects timeout"""
        verifier = ApprovalVerifier()
        requested = datetime.now()
        _, deadline = verifier.check_approval_timeout(requested, 'Gold', priority)
        expected_deadline = requested + timedelta(hours=4 + hours_delta)
        # Allow 1 second tolerance
        assert abs((deadline - expected_deadline).total_seconds()) < 1


# Total: 12 test methods
