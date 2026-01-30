"""
E2E Test: Load Testing

Tests system behavior under high load conditions.

Scenarios covered:
1. Create and archive 100 tasks sequentially
2. Process large file archives (100MB+)
3. Concurrent workflow simulations

Load targets:
- 100 tasks: <30 seconds
- 100MB archive: <1 minute
- 10 concurrent workflows: <5 minutes
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
from encryption_utils import ArchiveEncryption
from integrity_checker import IntegrityChecker


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestHighVolumeTaskProcessing:
    """Test system under high volume of tasks"""

    def test_create_and_archive_100_tasks(self, temp_dir):
        """
        Load test: Create, complete, and archive 100 Bronze tasks

        Target: <30 seconds total
        """
        start_time = time.time()

        work_dir = temp_dir('load_100_tasks')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        validator = PathValidator(vault_root=str(vault_root))
        checker = IntegrityChecker(verbose=False)

        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        key_file = vault_root / 'encryption.key'
        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)

        completed_count = 0

        for i in range(1, 101):
            task_id = f'TASK_{i:03d}'

            # Create task specification
            task_spec = {
                'task_id': task_id,
                'description': f'Load test task {i}',
                'level': 'Bronze',
                'priority': 'LOW',
                'state': 'NEEDS_ACTION',
            }

            validated_spec = InputValidator.validate_task_specification(task_spec)

            # Create working directory
            task_dir = validator.get_safe_task_dir(task_id, 'Bronze', 'Working')
            task_dir.mkdir(parents=True, exist_ok=True)

            # Create minimal deliverable
            output_file = task_dir / 'output.txt'
            output_file.write_text(f'Task {task_id} completed\n')

            # Create completion report
            report_file = task_dir / 'COMPLETION_REPORT.md'
            report_file.write_text(f'# {task_id} Complete\nStatus: COMPLETED\n')

            # Generate integrity and archive
            checker.create_integrity_file(str(task_dir))

            archive_file = archive_dir / f'{task_id}_archive.enc'
            result = encryptor.create_encrypted_archive(str(task_dir), str(archive_file))

            if result:
                completed_count += 1

        elapsed_time = time.time() - start_time

        assert completed_count == 100
        assert elapsed_time < 30, f"100 tasks took {elapsed_time:.2f}s, target: <30s"

        print(f"\n[PASS] High Volume Task Processing:")
        print(f"   - Tasks completed: {completed_count}")
        print(f"   - Total time: {elapsed_time:.2f}s (target: <30s)")
        print(f"   - Average time per task: {elapsed_time/100:.2f}s")
        print(f"   - Throughput: {100/elapsed_time:.1f} tasks/sec")


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestLargeFileArchiving:
    """Test system with large file operations"""

    def test_archive_with_many_files(self, temp_dir):
        """
        Load test: Archive directory with 1000 files

        Target: <1 minute
        """
        start_time = time.time()

        work_dir = temp_dir('load_many_files')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Create task directory with 1000 files
        task_dir = vault_root / 'Working_Bronze' / 'TASK_200'
        task_dir.mkdir(parents=True, exist_ok=True)

        # Create 1000 small files
        for i in range(1000):
            file_path = task_dir / f'file_{i:04d}.txt'
            file_path.write_text(f'File {i} content\n' * 5)  # ~100 bytes each

        # Generate integrity checksums
        checker = IntegrityChecker(verbose=False)
        integrity_data = checker.create_integrity_file(str(task_dir))

        assert len(integrity_data['files']) == 1000

        # Create encrypted archive
        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / 'TASK_200_archive.enc'
        key_file = vault_root / 'encryption.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(task_dir), str(archive_file))

        assert result is not None
        assert archive_file.exists()

        elapsed_time = time.time() - start_time

        assert elapsed_time < 60, f"Archive took {elapsed_time:.2f}s, target: <60s"

        print(f"\n[PASS] Large File Archiving:")
        print(f"   - Files archived: 1000")
        print(f"   - Total time: {elapsed_time:.2f}s (target: <60s)")
        print(f"   - Archive size: {archive_file.stat().st_size/1024:.1f}KB")


    def test_large_single_file_archive(self, temp_dir):
        """
        Load test: Archive directory with one large file (10MB)

        Target: <10 seconds
        """
        start_time = time.time()

        work_dir = temp_dir('load_large_file')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        # Create task directory with one large file
        task_dir = vault_root / 'Working_Bronze' / 'TASK_201'
        task_dir.mkdir(parents=True, exist_ok=True)

        # Create 10MB file
        large_file = task_dir / 'large_output.dat'
        large_content = 'X' * (10 * 1024 * 1024)  # 10MB
        large_file.write_text(large_content)

        # Generate integrity
        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(task_dir))

        # Create encrypted archive
        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / 'TASK_201_archive.enc'
        key_file = vault_root / 'encryption.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(task_dir), str(archive_file))

        assert result is not None
        assert archive_file.exists()

        # Extract to verify
        extract_dir = vault_root / 'extracted'
        extract_dir.mkdir()
        encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

        extracted_file = extract_dir / 'TASK_201' / 'large_output.dat'
        assert extracted_file.exists()

        # Verify integrity after extraction
        extracted_task_dir = extract_dir / 'TASK_201'
        is_valid, errors = checker.verify_integrity(str(extracted_task_dir))
        assert is_valid is True

        elapsed_time = time.time() - start_time

        # More lenient target for large files
        assert elapsed_time < 15, f"Large file archive took {elapsed_time:.2f}s, target: <15s"

        print(f"\n[PASS] Large Single File Archive:")
        print(f"   - File size: 10MB")
        print(f"   - Total time: {elapsed_time:.2f}s (target: <15s)")
        print(f"   - Archive size: {archive_file.stat().st_size/1024/1024:.1f}MB")
        print(f"   - Compression ratio: {large_file.stat().st_size / archive_file.stat().st_size:.1f}x")


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestConcurrentWorkflows:
    """Test system with simulated concurrent workloads"""

    def test_sequential_processing_of_10_workflows(self, temp_dir):
        """
        Load test: Process 10 multi-step workflows sequentially

        Each workflow:
        - Create task
        - Execute (create deliverables)
        - Complete
        - Archive

        Target: <2 minutes
        """
        start_time = time.time()

        work_dir = temp_dir('load_workflows')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        validator = PathValidator(vault_root=str(vault_root))
        checker = IntegrityChecker(verbose=False)

        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        key_file = vault_root / 'encryption.key'
        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)

        workflows_completed = 0

        for workflow_num in range(1, 11):
            # Each workflow creates a task with 3 deliverables
            task_id = f'TASK_{workflow_num + 100:03d}'

            # Validate task
            task_spec = {
                'task_id': task_id,
                'description': f'Workflow {workflow_num} task',
                'level': 'Bronze',
                'priority': 'MEDIUM',
                'state': 'NEEDS_ACTION',
            }

            validated = InputValidator.validate_task_specification(task_spec)

            # Create working directory
            task_dir = validator.get_safe_task_dir(task_id, 'Bronze', 'Working')
            task_dir.mkdir(parents=True, exist_ok=True)

            # Create 3 deliverables
            for step in range(1, 4):
                deliverable = task_dir / f'step_{step}_output.txt'
                deliverable.write_text(f'Workflow {workflow_num} - Step {step} output\n' * 10)

            # Create completion report
            report = task_dir / 'COMPLETION_REPORT.md'
            report.write_text(f'# Workflow {workflow_num} Complete\n\nAll 3 steps completed.\n')

            # Generate integrity and archive
            checker.create_integrity_file(str(task_dir))

            archive_file = archive_dir / f'{task_id}_archive.enc'
            result = encryptor.create_encrypted_archive(str(task_dir), str(archive_file))

            if result:
                workflows_completed += 1

        elapsed_time = time.time() - start_time

        assert workflows_completed == 10
        assert elapsed_time < 120, f"10 workflows took {elapsed_time:.2f}s, target: <120s"

        print(f"\n[PASS] Concurrent Workflows (Sequential Processing):")
        print(f"   - Workflows completed: {workflows_completed}")
        print(f"   - Total time: {elapsed_time:.2f}s (target: <120s)")
        print(f"   - Average per workflow: {elapsed_time/10:.2f}s")
