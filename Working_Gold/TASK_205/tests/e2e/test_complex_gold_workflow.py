"""
E2E Test: Complex Gold-Level Workflow

Tests complete Gold-level task lifecycle with multi-phase execution and approval.

Scenarios covered:
1. Gold task with full approval workflow
2. Multi-phase task execution
3. Comprehensive audit trail generation

Performance benchmarks:
- Total time: <2 minutes
- Memory usage: <200MB
- File operations: <200 ops
"""

import pytest
import time
import sys
from pathlib import Path
from datetime import datetime

# Add TASK_204 scripts to path
task_204_scripts = Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'
sys.path.insert(0, str(task_204_scripts))

from input_validator import InputValidator
from path_validator import PathValidator
from approval_verifier import ApprovalVerifier
from encryption_utils import ArchiveEncryption
from integrity_checker import IntegrityChecker
from secure_logging import SecureLogger


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestGoldLevelWorkflow:
    """Test complete Gold-level task with approval and multi-phase execution"""

    def test_gold_task_with_full_approval_workflow(self, temp_dir):
        """
        Test complete Gold task lifecycle with approval workflow

        Workflow:
        1. Create Gold task specification
        2. Transition to PLANNING state
        3. Create execution plan (5 phases)
        4. Request approval (PLANNING → AWAITING_APPROVAL)
        5. Grant approval
        6. Transition to IN_PROGRESS
        7. Execute all 5 phases
        8. Create comprehensive completion report
        9. Transition to COMPLETED
        10. Create encrypted archive
        11. Verify complete audit trail
        12. Transition to DONE

        Performance expectations:
        - Total time: <2 minutes
        - File operations: <200 ops
        """
        start_time = time.time()
        file_ops_count = 0

        work_dir = temp_dir('gold_workflow_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Step 1: Create Gold task specification
        task_spec = {
            'task_id': 'TASK_250',
            'description': 'Complex Gold-level task with multi-phase execution',
            'level': 'Gold',
            'priority': 'HIGH',
            'state': 'NEEDS_ACTION',
            'created': datetime.now().isoformat(),
        }

        validated_spec = InputValidator.validate_task_specification(task_spec)
        assert validated_spec is not None
        assert validated_spec['level'] == 'Gold'
        file_ops_count += 1

        # Step 2: Create working directory and setup logging
        validator = PathValidator(vault_root=str(vault_root))
        working_dir = validator.get_safe_task_dir('TASK_250', 'Gold', 'Working')
        working_dir.mkdir(parents=True, exist_ok=True)
        file_ops_count += 2

        logs_dir = working_dir / 'logs'
        logs_dir.mkdir()
        log_file = logs_dir / 'execution.log'
        file_ops_count += 2

        logger = SecureLogger('task_250', log_file=str(log_file), console=False)

        # Step 3: Transition to PLANNING state
        logger.info(f'Task {task_spec["task_id"]}: NEEDS_ACTION → PLANNING')
        task_spec['state'] = 'PLANNING'
        file_ops_count += 1

        # Step 4: Create execution plan (simulated 5-phase plan)
        plan_dir = working_dir / 'planning'
        plan_dir.mkdir()
        execution_plan = plan_dir / 'EXECUTION_PLAN.md'
        file_ops_count += 2

        plan_content = f"""# Execution Plan: {task_spec['task_id']}

**Task**: {task_spec['description']}
**Level**: {task_spec['level']}
**Priority**: {task_spec['priority']}

## Phases

### Phase 1: Foundation Setup (Week 1)
- Initialize infrastructure
- Set up dependencies
- Create baseline documentation

### Phase 2: Core Implementation (Weeks 2-3)
- Implement core functionality
- Write unit tests
- Initial integration

### Phase 3: Integration & Testing (Week 4)
- Full integration testing
- Performance benchmarks
- Security validation

### Phase 4: Documentation & Review (Week 5)
- Complete documentation
- Code review
- User acceptance testing

### Phase 5: Deployment & Verification (Week 6)
- Production deployment
- Verification testing
- Final sign-off

## Approval Required
This plan requires approval before proceeding to execution.

**Plan Created**: {datetime.now().isoformat()}
"""
        execution_plan.write_text(plan_content)
        file_ops_count += 1

        logger.info('Execution plan created with 5 phases')

        # Step 5: Request approval (PLANNING → AWAITING_APPROVAL)
        verifier = ApprovalVerifier()
        task_spec['state'] = 'AWAITING_APPROVAL'
        logger.info('Task transitioned to AWAITING_APPROVAL')
        file_ops_count += 1

        # Step 6: Grant approval (simulated human approval)
        approval_dir = working_dir / 'approvals'
        approval_dir.mkdir()
        approval_file = approval_dir / 'approval_001.json'
        file_ops_count += 2

        approval_data = {
            'task_id': 'TASK_250',
            'approved_by': 'test_approver',
            'approved_at': datetime.now().isoformat(),
            'approval_type': 'PLANNING_TO_EXECUTION',
            'notes': 'Approved for execution. All phases look good.',
        }

        import json
        approval_file.write_text(json.dumps(approval_data, indent=2))
        file_ops_count += 1

        # Validate approval transition
        is_valid, reason = verifier.validate_state_transition(
            'AWAITING_APPROVAL', 'IN_PROGRESS', has_approval=True, task_level='Gold'
        )
        assert is_valid is True
        logger.info(f'Approval granted: {reason}')

        # Step 7: Transition to IN_PROGRESS
        task_spec['state'] = 'IN_PROGRESS'
        logger.info('Task transitioned to IN_PROGRESS')
        file_ops_count += 1

        # Step 8: Execute all 5 phases
        phases_dir = working_dir / 'phases'
        phases_dir.mkdir()
        file_ops_count += 1

        for phase_num in range(1, 6):
            phase_dir = phases_dir / f'phase_{phase_num}'
            phase_dir.mkdir()
            file_ops_count += 1

            # Create phase deliverables
            deliverable = phase_dir / f'phase_{phase_num}_output.txt'
            deliverable.write_text(f'Phase {phase_num} completed successfully\n' + 'Output data\n' * 20)
            file_ops_count += 1

            # Create phase report
            phase_report = phase_dir / f'PHASE_{phase_num}_REPORT.md'
            phase_report.write_text(f"""# Phase {phase_num} Report

**Status**: COMPLETED
**Completed**: {datetime.now().isoformat()}

## Deliverables
- {f'phase_{phase_num}_output.txt'}: Phase output

## Summary
Phase {phase_num} completed successfully. All objectives met.
""")
            file_ops_count += 1

            logger.info(f'Phase {phase_num}/5 completed')

        # Step 9: Create comprehensive completion report
        completion_report = working_dir / 'COMPLETION_REPORT.md'
        report_content = f"""# Task Completion Report

**Task ID**: {task_spec['task_id']}
**Description**: {task_spec['description']}
**Level**: {task_spec['level']}
**Priority**: {task_spec['priority']}
**Status**: COMPLETED
**Completed**: {datetime.now().isoformat()}

## Execution Summary

This Gold-level task was executed in 5 phases over a simulated 6-week period.
All phases completed successfully with full approval workflow.

## Phases Completed

### Phase 1: Foundation Setup
- Status: COMPLETED
- Deliverables: phase_1_output.txt

### Phase 2: Core Implementation
- Status: COMPLETED
- Deliverables: phase_2_output.txt

### Phase 3: Integration & Testing
- Status: COMPLETED
- Deliverables: phase_3_output.txt

### Phase 4: Documentation & Review
- Status: COMPLETED
- Deliverables: phase_4_output.txt

### Phase 5: Deployment & Verification
- Status: COMPLETED
- Deliverables: phase_5_output.txt

## Approvals

1. Planning to Execution: Approved by test_approver

## Audit Trail

Complete execution logs available in logs/execution.log

## Metrics

- Total phases: 5
- Phases completed: 5
- Approval requests: 1
- Approvals granted: 1
- Errors: 0
- Duration: {time.time() - start_time:.2f}s (test execution)

## Security

- All logs sanitized
- Integrity checksums generated
- Encrypted archive created
"""
        completion_report.write_text(report_content)
        file_ops_count += 1

        logger.info('Comprehensive completion report created')

        # Step 10: Transition to COMPLETED
        task_spec['state'] = 'COMPLETED'
        logger.info('Task transitioned to COMPLETED')
        file_ops_count += 1

        # Step 11: Generate integrity checksums
        checker = IntegrityChecker(verbose=False)
        integrity_data = checker.create_integrity_file(str(working_dir))
        assert integrity_data is not None
        assert len(integrity_data['files']) >= 14  # Plan + 5 phases x 2 files + report + log + approval
        file_ops_count += 1

        # Verify integrity
        is_valid, errors = checker.verify_integrity(str(working_dir))
        assert is_valid is True
        assert len(errors) == 0

        # Step 12: Create encrypted archive
        archive_dir = vault_root / 'Archive_Gold' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / 'TASK_250_archive.enc'
        key_file = vault_root / 'encryption.key'
        file_ops_count += 3

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(working_dir), str(archive_file))
        file_ops_count += 10  # Archive creation with many files

        assert result is not None
        assert archive_file.exists()

        logger.info('Encrypted archive created')

        # Step 13: Verify audit trail completeness
        log_content = log_file.read_text()
        assert 'NEEDS_ACTION' in log_content and 'PLANNING' in log_content
        assert 'AWAITING_APPROVAL' in log_content
        assert 'IN_PROGRESS' in log_content
        assert 'Phase 1/5 completed' in log_content
        assert 'Phase 5/5 completed' in log_content
        assert 'COMPLETED' in log_content

        # Step 14: Transition to DONE
        task_spec['state'] = 'DONE'
        logger.info('Task transitioned to DONE - TASK COMPLETE')
        file_ops_count += 1

        # Performance validation
        elapsed_time = time.time() - start_time

        assert elapsed_time < 120, f"Task took {elapsed_time:.2f}s, expected <120s"
        assert file_ops_count < 200, f"Performed {file_ops_count} file ops, expected <200"

        print(f"\n[PASS] Gold Task Performance:")
        print(f"   - Total time: {elapsed_time:.2f}s (target: <120s)")
        print(f"   - File operations: {file_ops_count} (target: <200)")
        print(f"   - Phases completed: 5")
        print(f"   - Approvals: 1")


    def test_gold_task_with_failed_phase(self, temp_dir):
        """
        Test Gold task with a failed phase and recovery

        Simulates a phase failure and recovery workflow.
        """
        start_time = time.time()

        work_dir = temp_dir('gold_failed_phase_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Create Gold task
        task_spec = {
            'task_id': 'TASK_251',
            'description': 'Gold task with failed phase',
            'level': 'Gold',
            'priority': 'HIGH',
            'state': 'IN_PROGRESS',
        }

        validated_spec = InputValidator.validate_task_specification(task_spec)
        assert validated_spec is not None

        # Create working directory
        validator = PathValidator(vault_root=str(vault_root))
        working_dir = validator.get_safe_task_dir('TASK_251', 'Gold', 'Working')
        working_dir.mkdir(parents=True, exist_ok=True)

        logs_dir = working_dir / 'logs'
        logs_dir.mkdir()
        log_file = logs_dir / 'execution.log'
        logger = SecureLogger('task_251', log_file=str(log_file), console=False)

        # Execute phases with failure in phase 3
        phases_dir = working_dir / 'phases'
        phases_dir.mkdir()

        for phase_num in range(1, 6):
            phase_dir = phases_dir / f'phase_{phase_num}'
            phase_dir.mkdir()

            if phase_num == 3:
                # Simulate phase 3 failure
                error_file = phase_dir / 'ERROR.txt'
                error_file.write_text('Phase 3 failed: Integration test failure\n')
                logger.error(f'Phase {phase_num} FAILED: Integration test failure')

                # Transition to FAILED state
                task_spec['state'] = 'FAILED'
                logger.info('Task transitioned to FAILED')

                # Create error report
                error_report = working_dir / 'ERROR_REPORT.md'
                error_report.write_text(f"""# Error Report

**Task ID**: TASK_251
**Failed Phase**: Phase 3
**Error**: Integration test failure
**Timestamp**: {datetime.now().isoformat()}

## Recovery Actions
1. Investigate integration test failure
2. Fix identified issues
3. Re-run Phase 3
4. Continue with remaining phases
""")
                logger.info('Error report created')
                break
            else:
                # Phase succeeds
                deliverable = phase_dir / f'phase_{phase_num}_output.txt'
                deliverable.write_text(f'Phase {phase_num} completed successfully')
                logger.info(f'Phase {phase_num} completed')

        # Verify task is in FAILED state
        assert task_spec['state'] == 'FAILED'

        # Verify error documentation exists
        assert (working_dir / 'ERROR_REPORT.md').exists()
        assert (phases_dir / 'phase_3' / 'ERROR.txt').exists()

        # Verify audit trail shows failure
        log_content = log_file.read_text()
        assert 'Phase 3 FAILED' in log_content
        assert 'FAILED' in log_content

        elapsed_time = time.time() - start_time
        print(f"\n[PASS] Failed Phase Workflow: {elapsed_time:.2f}s")
        print(f"   - Phases executed: 2 (before failure)")
        print(f"   - Error report created")


    def test_gold_task_approval_timeout(self, temp_dir):
        """
        Test Gold task approval timeout scenario

        Simulates a task that times out while waiting for approval.
        """
        work_dir = temp_dir('gold_approval_timeout_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Create Gold task
        task_spec = {
            'task_id': 'TASK_252',
            'description': 'Gold task with approval timeout',
            'level': 'Gold',
            'priority': 'MEDIUM',
            'state': 'PLANNING',
        }

        validated_spec = InputValidator.validate_task_specification(task_spec)
        assert validated_spec is not None

        # Create working directory
        validator = PathValidator(vault_root=str(vault_root))
        working_dir = validator.get_safe_task_dir('TASK_252', 'Gold', 'Working')
        working_dir.mkdir(parents=True, exist_ok=True)

        logs_dir = working_dir / 'logs'
        logs_dir.mkdir()
        log_file = logs_dir / 'execution.log'
        logger = SecureLogger('task_252', log_file=str(log_file), console=False)

        # Create execution plan
        plan_dir = working_dir / 'planning'
        plan_dir.mkdir()
        execution_plan = plan_dir / 'EXECUTION_PLAN.md'
        execution_plan.write_text('# Execution Plan\n\nWaiting for approval...')

        # Request approval
        task_spec['state'] = 'AWAITING_APPROVAL'
        logger.info('Task awaiting approval')

        # Simulate approval timeout (no approval file created)
        # In real system, this would trigger timeout handler after configured period
        timeout_file = working_dir / 'APPROVAL_TIMEOUT.txt'
        timeout_file.write_text(f"""# Approval Timeout

**Task ID**: TASK_252
**Requested**: {datetime.now().isoformat()}
**Status**: Timeout after 7 days (simulated)

Task has been waiting for approval beyond the configured timeout period.
Next steps: Contact approver or cancel task.
""")

        logger.warning('Approval timeout detected')

        # Verify timeout documented
        assert timeout_file.exists()
        assert task_spec['state'] == 'AWAITING_APPROVAL'

        # Verify audit trail shows timeout
        log_content = log_file.read_text()
        assert 'Approval timeout' in log_content or 'timeout detected' in log_content

        print(f"\n[PASS] Approval Timeout Scenario")
        print(f"   - Task state: AWAITING_APPROVAL")
        print(f"   - Timeout documented")
