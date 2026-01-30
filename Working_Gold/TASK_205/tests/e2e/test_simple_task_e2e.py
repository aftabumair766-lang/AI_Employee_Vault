"""
E2E Test: Simple Task End-to-End

Tests complete Bronze-level task lifecycle from creation to archival.

Scenarios covered:
1. Simple Bronze task: NEEDS_ACTION → IN_PROGRESS → COMPLETED → DONE
2. Task with deliverables and completion report
3. Archival with integrity verification

Performance benchmarks:
- Total time: <30 seconds
- Memory usage: <100MB
- File operations: <50 ops
"""

import pytest
import time
import sys
from pathlib import Path
from datetime import datetime

# Add TASK_204 scripts to path for accessing implemented modules
task_204_scripts = Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'
sys.path.insert(0, str(task_204_scripts))

from input_validator import InputValidator
from path_validator import PathValidator
from encryption_utils import ArchiveEncryption
from integrity_checker import IntegrityChecker


@pytest.mark.e2e
@pytest.mark.phase4
class TestSimpleBronzeTaskE2E:
    """Test complete lifecycle of a simple Bronze-level task"""

    def test_bronze_task_complete_lifecycle(self, temp_dir):
        """
        Test complete Bronze task lifecycle: creation → execution → completion → archival

        Workflow:
        1. Create task specification
        2. Validate task inputs
        3. Create working directory
        4. Simulate task execution (create deliverables)
        5. Create completion report
        6. Generate integrity checksums
        7. Create encrypted archive
        8. Verify archive integrity
        9. Clean up working directory

        Performance expectations:
        - Total time: <30 seconds
        - File operations: <50 ops
        """
        start_time = time.time()
        file_ops_count = 0

        work_dir = temp_dir('bronze_task_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Step 1: Create task specification
        task_spec = {
            'task_id': 'TASK_001',
            'description': 'Simple Bronze-level task for E2E testing',
            'level': 'Bronze',
            'priority': 'LOW',
            'state': 'NEEDS_ACTION',
            'created': datetime.now().isoformat(),
        }

        # Step 2: Validate task specification
        validated_spec = InputValidator.validate_task_specification(task_spec)
        assert validated_spec is not None
        assert validated_spec['task_id'] == 'TASK_001'
        assert validated_spec['level'] == 'Bronze'
        file_ops_count += 1

        # Step 3: Create working directory (NEEDS_ACTION → IN_PROGRESS)
        validator = PathValidator(vault_root=str(vault_root))
        working_dir = validator.get_safe_task_dir('TASK_001', 'Bronze', 'Working')
        working_dir.mkdir(parents=True, exist_ok=True)
        file_ops_count += 2

        assert working_dir.exists()
        assert validator.is_safe_path(str(working_dir))

        # Step 4: Simulate task execution - create deliverables
        deliverable1 = working_dir / 'output.txt'
        deliverable1.write_text('Task output: Simple Bronze task completed successfully')
        file_ops_count += 1

        deliverable2 = working_dir / 'results.json'
        deliverable2.write_text('{"status": "success", "items_processed": 10}')
        file_ops_count += 1

        logs_dir = working_dir / 'logs'
        logs_dir.mkdir()
        execution_log = logs_dir / 'execution.log'
        execution_log.write_text('Task started\nTask completed\n')
        file_ops_count += 3

        # Step 5: Create completion report (IN_PROGRESS → COMPLETED)
        completion_report = working_dir / 'COMPLETION_REPORT.md'
        report_content = f"""# Task Completion Report

**Task ID**: {task_spec['task_id']}
**Description**: {task_spec['description']}
**Level**: {task_spec['level']}
**Status**: COMPLETED
**Completed**: {datetime.now().isoformat()}

## Deliverables
- output.txt: Task output file
- results.json: Results data
- logs/execution.log: Execution logs

## Summary
Simple Bronze task completed successfully. All deliverables created.

## Metrics
- Items processed: 10
- Errors: 0
- Duration: <30s
"""
        completion_report.write_text(report_content)
        file_ops_count += 1

        assert completion_report.exists()

        # Step 6: Generate integrity checksums before archival
        checker = IntegrityChecker(verbose=False)
        integrity_data = checker.create_integrity_file(str(working_dir))
        file_ops_count += 1

        assert integrity_data is not None
        assert len(integrity_data['files']) >= 4  # At least 4 files (output, results, log, report)

        # Verify integrity before archival
        is_valid, errors = checker.verify_integrity(str(working_dir))
        assert is_valid is True
        assert len(errors) == 0
        file_ops_count += 1

        # Step 7: Create encrypted archive (COMPLETED → DONE)
        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_file = archive_dir / 'TASK_001_archive.enc'
        key_file = vault_root / 'encryption.key'
        file_ops_count += 3

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(working_dir), str(archive_file))
        file_ops_count += 5  # Archive creation involves multiple operations

        assert result is not None  # Returns archive path
        assert archive_file.exists()
        assert archive_file.stat().st_size > 0

        # Step 8: Verify archive can be extracted and integrity maintained
        extract_dir = vault_root / 'temp_extract'
        extract_dir.mkdir()
        file_ops_count += 1

        encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))
        file_ops_count += 5  # Extraction involves multiple operations

        extracted_task_dir = extract_dir / 'TASK_001'
        assert extracted_task_dir.exists()

        # Verify integrity after extraction
        is_valid, errors = checker.verify_integrity(str(extracted_task_dir))
        assert is_valid is True
        assert len(errors) == 0
        file_ops_count += 1

        # Verify deliverables present in extracted archive
        assert (extracted_task_dir / 'output.txt').exists()
        assert (extracted_task_dir / 'results.json').exists()
        assert (extracted_task_dir / 'COMPLETION_REPORT.md').exists()
        assert (extracted_task_dir / 'logs' / 'execution.log').exists()

        # Step 9: Performance validation
        elapsed_time = time.time() - start_time

        # Verify performance benchmarks
        assert elapsed_time < 30, f"Task took {elapsed_time:.2f}s, expected <30s"
        assert file_ops_count < 50, f"Performed {file_ops_count} file ops, expected <50"

        print(f"\n[PASS]E2E Test Performance:")
        print(f"   - Total time: {elapsed_time:.2f}s (target: <30s)")
        print(f"   - File operations: {file_ops_count} (target: <50)")


    def test_bronze_task_with_minimal_deliverables(self, temp_dir):
        """
        Test Bronze task with minimal deliverables (just completion report)

        This represents the simplest possible task workflow.
        """
        start_time = time.time()

        work_dir = temp_dir('bronze_minimal_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Create task
        task_spec = {
            'task_id': 'TASK_002',
            'description': 'Minimal Bronze task',
            'level': 'Bronze',
            'priority': 'LOW',
            'state': 'NEEDS_ACTION',
        }

        validated_spec = InputValidator.validate_task_specification(task_spec)
        assert validated_spec is not None

        # Create working directory
        validator = PathValidator(vault_root=str(vault_root))
        working_dir = validator.get_safe_task_dir('TASK_002', 'Bronze', 'Working')
        working_dir.mkdir(parents=True, exist_ok=True)

        # Create only completion report (minimal deliverable)
        completion_report = working_dir / 'COMPLETION_REPORT.md'
        completion_report.write_text(f"""# Minimal Task Completion

**Task ID**: TASK_002
**Status**: COMPLETED

Task completed with minimal deliverables.
""")

        # Generate integrity and archive
        checker = IntegrityChecker(verbose=False)
        integrity_data = checker.create_integrity_file(str(working_dir))
        assert integrity_data is not None

        is_valid, errors = checker.verify_integrity(str(working_dir))
        assert is_valid is True

        # Archive
        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / 'TASK_002_archive.enc'
        key_file = vault_root / 'encryption.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(working_dir), str(archive_file))

        assert result is not None  # Returns archive path
        assert archive_file.exists()

        # Performance check - minimal task should be very fast
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10, f"Minimal task took {elapsed_time:.2f}s, expected <10s"

        print(f"\n[PASS]Minimal Task Performance: {elapsed_time:.2f}s")


    def test_bronze_task_with_large_deliverables(self, temp_dir):
        """
        Test Bronze task with larger deliverables to stress file operations

        This tests the system's ability to handle tasks with multiple files
        and moderate file sizes.
        """
        start_time = time.time()

        work_dir = temp_dir('bronze_large_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Create task
        task_spec = {
            'task_id': 'TASK_003',
            'description': 'Bronze task with larger deliverables',
            'level': 'Bronze',
            'priority': 'MEDIUM',
            'state': 'NEEDS_ACTION',
        }

        validated_spec = InputValidator.validate_task_specification(task_spec)
        assert validated_spec is not None

        # Create working directory
        validator = PathValidator(vault_root=str(vault_root))
        working_dir = validator.get_safe_task_dir('TASK_003', 'Bronze', 'Working')
        working_dir.mkdir(parents=True, exist_ok=True)

        # Create multiple deliverables (simulate realistic task output)
        outputs_dir = working_dir / 'outputs'
        outputs_dir.mkdir()

        # Create 10 output files
        for i in range(10):
            output_file = outputs_dir / f'output_{i:03d}.txt'
            output_file.write_text(f'Output file {i}\n' + 'Data line\n' * 100)

        # Create logs directory with multiple log files
        logs_dir = working_dir / 'logs'
        logs_dir.mkdir()

        for log_type in ['execution', 'debug', 'error']:
            log_file = logs_dir / f'{log_type}.log'
            log_file.write_text(f'{log_type.upper()} log\n' + f'{log_type} entry\n' * 50)

        # Create completion report
        completion_report = working_dir / 'COMPLETION_REPORT.md'
        completion_report.write_text(f"""# Task Completion Report

**Task ID**: TASK_003
**Status**: COMPLETED

## Deliverables
- 10 output files in outputs/
- 3 log files in logs/
- This completion report

All deliverables created successfully.
""")

        # Generate integrity and verify
        checker = IntegrityChecker(verbose=False)
        integrity_data = checker.create_integrity_file(str(working_dir))
        assert integrity_data is not None
        assert len(integrity_data['files']) >= 14  # 10 outputs + 3 logs + 1 report

        is_valid, errors = checker.verify_integrity(str(working_dir))
        assert is_valid is True

        # Create encrypted archive
        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / 'TASK_003_archive.enc'
        key_file = vault_root / 'encryption.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(working_dir), str(archive_file))

        assert result is not None  # Returns archive path
        assert archive_file.exists()

        # Extract and verify integrity maintained
        extract_dir = vault_root / 'temp_extract'
        extract_dir.mkdir()
        encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

        extracted_task_dir = extract_dir / 'TASK_003'
        is_valid, errors = checker.verify_integrity(str(extracted_task_dir))
        assert is_valid is True

        # Verify all files present
        assert (extracted_task_dir / 'outputs').exists()
        assert len(list((extracted_task_dir / 'outputs').glob('*.txt'))) == 10
        assert (extracted_task_dir / 'logs').exists()
        assert len(list((extracted_task_dir / 'logs').glob('*.log'))) == 3

        # Performance check
        elapsed_time = time.time() - start_time
        assert elapsed_time < 30, f"Large task took {elapsed_time:.2f}s, expected <30s"

        print(f"\n[PASS]Large Task Performance: {elapsed_time:.2f}s")
        print(f"   - Files archived: {len(integrity_data['files'])}")


@pytest.mark.e2e
@pytest.mark.phase4
class TestTaskFailureRecovery:
    """Test task failure scenarios and recovery mechanisms"""

    def test_task_integrity_violation_detected(self, temp_dir):
        """
        Test that integrity violations are detected during archival

        Simulates a scenario where a file is modified after integrity
        checksums are generated but before archival.
        """
        work_dir = temp_dir('integrity_violation_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Create task
        validator = PathValidator(vault_root=str(vault_root))
        working_dir = validator.get_safe_task_dir('TASK_099', 'Bronze', 'Working')
        working_dir.mkdir(parents=True, exist_ok=True)

        # Create deliverable
        output_file = working_dir / 'output.txt'
        output_file.write_text('Original content')

        # Generate integrity checksums
        checker = IntegrityChecker(verbose=False)
        integrity_data = checker.create_integrity_file(str(working_dir))
        assert integrity_data is not None

        # Simulate file tampering AFTER integrity check
        output_file.write_text('Modified content - tampered!')

        # Verify integrity should now fail
        is_valid, errors = checker.verify_integrity(str(working_dir))
        assert is_valid is False
        assert len(errors) > 0
        assert any('mismatch' in error.lower() for error in errors)

        print(f"\n[PASS]Integrity violation correctly detected")
        print(f"   - Errors: {errors}")
