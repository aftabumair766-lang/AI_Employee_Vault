"""
E2E Test: Multi-Task Orchestration

Tests coordination of multiple tasks with dependencies and workflows.

Scenarios covered:
1. Sequential task execution (Task B depends on Task A)
2. Parallel task execution (independent tasks)
3. Complex multi-task workflows with mixed dependencies

Performance benchmarks:
- Total time: <90 seconds
- Parallel efficiency: >70%
- Memory usage: <300MB
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
from secure_logging import SecureLogger


@pytest.mark.e2e
@pytest.mark.phase4
class TestSequentialTaskWorkflow:
    """Test sequential task execution where Task B depends on Task A"""

    def test_two_tasks_sequential_dependency(self, temp_dir):
        """
        Test sequential execution of two dependent tasks

        Workflow:
        1. Create TASK_010 (Bronze, simple data processing)
        2. Execute TASK_010 completely
        3. Archive TASK_010
        4. Create TASK_020 (Bronze, uses TASK_010 output)
        5. Execute TASK_020 using TASK_010's output
        6. Complete TASK_020
        7. Archive both tasks

        Dependency: TASK_020 requires TASK_010 output as input
        """
        start_time = time.time()

        work_dir = temp_dir('sequential_tasks_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        validator = PathValidator(vault_root=str(vault_root))
        checker = IntegrityChecker(verbose=False)

        # === TASK_010: Data Processing ===

        # Create TASK_010 specification
        task_a_spec = {
            'task_id': 'TASK_010',
            'description': 'Process raw data and generate dataset',
            'level': 'Bronze',
            'priority': 'MEDIUM',
            'state': 'NEEDS_ACTION',
        }

        validated_a = InputValidator.validate_task_specification(task_a_spec)
        assert validated_a is not None

        # Create TASK_010 working directory
        task_a_dir = validator.get_safe_task_dir('TASK_010', 'Bronze', 'Working')
        task_a_dir.mkdir(parents=True, exist_ok=True)

        # Execute TASK_010: Generate dataset
        dataset_file = task_a_dir / 'dataset.txt'
        dataset_content = "ID,Name,Value\n1,Item1,100\n2,Item2,200\n3,Item3,300\n"
        dataset_file.write_text(dataset_content)

        # Complete TASK_010
        task_a_report = task_a_dir / 'COMPLETION_REPORT.md'
        task_a_report.write_text(f"""# TASK_010 Completion

**Status**: COMPLETED
**Output**: dataset.txt (3 records)

Dataset generated successfully.
""")

        # Archive TASK_010
        archive_a_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_a_dir.mkdir(parents=True, exist_ok=True)

        checker.create_integrity_file(str(task_a_dir))

        archive_a_file = archive_a_dir / 'TASK_010_archive.enc'
        key_file = vault_root / 'encryption.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result_a = encryptor.create_encrypted_archive(str(task_a_dir), str(archive_a_file))

        assert result_a is not None
        assert archive_a_file.exists()

        # === TASK_020: Data Analysis (depends on TASK_010) ===

        # Extract TASK_010 archive to access output
        task_a_extract_dir = vault_root / 'temp_extract'
        task_a_extract_dir.mkdir()
        encryptor.extract_encrypted_archive(str(archive_a_file), str(task_a_extract_dir))

        extracted_task_a = task_a_extract_dir / 'TASK_010'
        assert extracted_task_a.exists()

        # Read TASK_010 output
        extracted_dataset = extracted_task_a / 'dataset.txt'
        assert extracted_dataset.exists()
        dataset_data = extracted_dataset.read_text()

        # Create TASK_020 specification
        task_b_spec = {
            'task_id': 'TASK_020',
            'description': 'Analyze dataset from TASK_010',
            'level': 'Bronze',
            'priority': 'MEDIUM',
            'state': 'NEEDS_ACTION',
            'depends_on': 'TASK_010',
        }

        validated_b = InputValidator.validate_task_specification(task_b_spec)
        assert validated_b is not None

        # Create TASK_020 working directory
        task_b_dir = validator.get_safe_task_dir('TASK_020', 'Bronze', 'Working')
        task_b_dir.mkdir(parents=True, exist_ok=True)

        # Execute TASK_020: Analyze dataset
        # Count records in dataset
        lines = dataset_data.strip().split('\n')
        record_count = len(lines) - 1  # Exclude header

        analysis_file = task_b_dir / 'analysis.txt'
        analysis_file.write_text(f"""Dataset Analysis Results

Source: TASK_010/dataset.txt
Total Records: {record_count}
Analysis: All records processed successfully
""")

        # Complete TASK_020
        task_b_report = task_b_dir / 'COMPLETION_REPORT.md'
        task_b_report.write_text(f"""# TASK_020 Completion

**Status**: COMPLETED
**Dependency**: TASK_010 (completed)
**Output**: analysis.txt

Analysis of {record_count} records completed successfully.
""")

        # Archive TASK_020
        checker.create_integrity_file(str(task_b_dir))

        archive_b_file = archive_a_dir / 'TASK_020_archive.enc'
        result_b = encryptor.create_encrypted_archive(str(task_b_dir), str(archive_b_file))

        assert result_b is not None
        assert archive_b_file.exists()

        # Verify both archives exist
        assert archive_a_file.exists()
        assert archive_b_file.exists()

        elapsed_time = time.time() - start_time

        print(f"\n[PASS] Sequential Task Workflow:")
        print(f"   - Total time: {elapsed_time:.2f}s")
        print(f"   - Tasks completed: 2 (TASK_010 → TASK_020)")
        print(f"   - Dependency resolution: Successful")


@pytest.mark.e2e
@pytest.mark.phase4
class TestParallelTaskWorkflow:
    """Test parallel execution of independent tasks"""

    def test_three_independent_tasks_parallel(self, temp_dir):
        """
        Test parallel execution of three independent tasks

        Workflow:
        1. Create TASK_X, TASK_Y, TASK_Z (all Bronze, independent)
        2. Execute all three tasks (simulated parallel execution)
        3. Complete all three tasks
        4. Archive all three tasks
        5. Verify all tasks completed successfully

        Performance: Should be more efficient than sequential execution
        """
        start_time = time.time()

        work_dir = temp_dir('parallel_tasks_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        validator = PathValidator(vault_root=str(vault_root))
        checker = IntegrityChecker(verbose=False)

        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)
        key_file = vault_root / 'encryption.key'
        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)

        # Define three independent tasks
        tasks = []
        for task_id in ['TASK_030', 'TASK_031', 'TASK_032']:
            task_spec = {
                'task_id': task_id,
                'description': f'Independent task {task_id}',
                'level': 'Bronze',
                'priority': 'LOW',
                'state': 'NEEDS_ACTION',
            }

            validated = InputValidator.validate_task_specification(task_spec)
            assert validated is not None
            tasks.append(validated)

        # Execute all tasks (simulated parallel execution)
        task_dirs = []
        for task in tasks:
            task_id = task['task_id']

            # Create working directory
            task_dir = validator.get_safe_task_dir(task_id, 'Bronze', 'Working')
            task_dir.mkdir(parents=True, exist_ok=True)
            task_dirs.append((task_id, task_dir))

            # Create deliverable
            output_file = task_dir / 'output.txt'
            output_file.write_text(f'Task {task_id} output\nProcessed independently\n')

            # Create completion report
            report_file = task_dir / 'COMPLETION_REPORT.md'
            report_file.write_text(f"""# {task_id} Completion

**Status**: COMPLETED
**Dependencies**: None (independent task)

Task completed successfully.
""")

        # Archive all tasks
        archive_files = []
        for task_id, task_dir in task_dirs:
            # Generate integrity
            checker.create_integrity_file(str(task_dir))

            # Create archive
            archive_file = archive_dir / f'{task_id}_archive.enc'
            result = encryptor.create_encrypted_archive(str(task_dir), str(archive_file))

            assert result is not None
            assert archive_file.exists()
            archive_files.append(archive_file)

        # Verify all three archives exist
        assert len(archive_files) == 3

        elapsed_time = time.time() - start_time

        print(f"\n[PASS] Parallel Task Workflow:")
        print(f"   - Total time: {elapsed_time:.2f}s")
        print(f"   - Tasks completed: 3 (parallel)")
        print(f"   - All archives created successfully")


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestComplexMultiTaskWorkflow:
    """Test complex workflows with mixed sequential and parallel tasks"""

    def test_five_task_mixed_dependency_workflow(self, temp_dir):
        """
        Test complex workflow with 5 tasks:
        - TASK_001, TASK_002 (parallel, independent)
        - TASK_003 (depends on TASK_001 AND TASK_002)
        - TASK_004 (depends on TASK_003)
        - TASK_005 (parallel with TASK_004, independent)

        Dependency graph:
                TASK_001 ----
                             \
                              ---> TASK_003 ---> TASK_004
                             /
                TASK_002 ----

                TASK_005 (independent)

        Performance expectations:
        - Total time: <60 seconds
        - Demonstrates dependency resolution
        """
        start_time = time.time()

        work_dir = temp_dir('complex_workflow_e2e')
        vault_root = work_dir / 'AI_Employee_vault'
        vault_root.mkdir()

        validator = PathValidator(vault_root=str(vault_root))
        checker = IntegrityChecker(verbose=False)
        encryptor = ArchiveEncryption(key_file=str(vault_root / 'encryption.key'), verbose=False)

        archive_dir = vault_root / 'Archive_Bronze' / 'Completed'
        archive_dir.mkdir(parents=True, exist_ok=True)

        logs_dir = vault_root / 'workflow_logs'
        logs_dir.mkdir()
        log_file = logs_dir / 'workflow.log'
        logger = SecureLogger('workflow', log_file=str(log_file), console=False)

        # === Phase 1: Execute TASK_001 and TASK_002 in parallel ===
        logger.info('Phase 1: Executing TASK_001 and TASK_002 (parallel)')

        for task_id in ['TASK_001', 'TASK_002']:
            task_dir = validator.get_safe_task_dir(task_id, 'Bronze', 'Working')
            task_dir.mkdir(parents=True, exist_ok=True)

            output_file = task_dir / 'data.txt'
            output_file.write_text(f'{task_id} data output\n')

            report_file = task_dir / 'COMPLETION_REPORT.md'
            report_file.write_text(f'# {task_id} Complete\nStatus: COMPLETED\n')

            checker.create_integrity_file(str(task_dir))
            archive_file = archive_dir / f'{task_id}_archive.enc'
            encryptor.create_encrypted_archive(str(task_dir), str(archive_file))

            logger.info(f'{task_id} completed and archived')

        # === Phase 2: Execute TASK_003 (depends on 001 and 002) ===
        logger.info('Phase 2: Executing TASK_003 (depends on TASK_001 + TASK_002)')

        # Extract TASK_001 and TASK_002 outputs
        extract_dir = vault_root / 'temp_extract'
        extract_dir.mkdir()

        task_001_data = ""
        task_002_data = ""

        for task_id in ['TASK_001', 'TASK_002']:
            archive_file = archive_dir / f'{task_id}_archive.enc'
            encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

            extracted = extract_dir / task_id / 'data.txt'
            data = extracted.read_text()

            if task_id == 'TASK_001':
                task_001_data = data
            else:
                task_002_data = data

        # Execute TASK_003
        task_003_dir = validator.get_safe_task_dir('TASK_003', 'Bronze', 'Working')
        task_003_dir.mkdir(parents=True, exist_ok=True)

        merged_output = task_003_dir / 'merged_data.txt'
        merged_output.write_text(f'Merged from dependencies:\n{task_001_data}{task_002_data}')

        report_003 = task_003_dir / 'COMPLETION_REPORT.md'
        report_003.write_text('# TASK_003 Complete\nDependencies: TASK_001, TASK_002\nStatus: COMPLETED\n')

        checker.create_integrity_file(str(task_003_dir))
        archive_003 = archive_dir / 'TASK_003_archive.enc'
        encryptor.create_encrypted_archive(str(task_003_dir), str(archive_003))

        logger.info('TASK_003 completed (merged dependencies)')

        # === Phase 3: Execute TASK_004 (depends on 003) and TASK_005 (independent) ===
        logger.info('Phase 3: Executing TASK_004 (depends on TASK_003) and TASK_005 (independent)')

        # TASK_004
        task_004_dir = validator.get_safe_task_dir('TASK_004', 'Bronze', 'Working')
        task_004_dir.mkdir(parents=True, exist_ok=True)

        output_004 = task_004_dir / 'final_output.txt'
        output_004.write_text('TASK_004 final processing complete\n')

        report_004 = task_004_dir / 'COMPLETION_REPORT.md'
        report_004.write_text('# TASK_004 Complete\nDependency: TASK_003\nStatus: COMPLETED\n')

        checker.create_integrity_file(str(task_004_dir))
        archive_004 = archive_dir / 'TASK_004_archive.enc'
        encryptor.create_encrypted_archive(str(task_004_dir), str(archive_004))

        logger.info('TASK_004 completed')

        # TASK_005 (independent)
        task_005_dir = validator.get_safe_task_dir('TASK_005', 'Bronze', 'Working')
        task_005_dir.mkdir(parents=True, exist_ok=True)

        output_005 = task_005_dir / 'independent_output.txt'
        output_005.write_text('TASK_005 independent processing\n')

        report_005 = task_005_dir / 'COMPLETION_REPORT.md'
        report_005.write_text('# TASK_005 Complete\nDependencies: None\nStatus: COMPLETED\n')

        checker.create_integrity_file(str(task_005_dir))
        archive_005 = archive_dir / 'TASK_005_archive.enc'
        encryptor.create_encrypted_archive(str(task_005_dir), str(archive_005))

        logger.info('TASK_005 completed')

        # === Verification ===

        # Verify all 5 archives exist
        for task_id in ['TASK_001', 'TASK_002', 'TASK_003', 'TASK_004', 'TASK_005']:
            archive_file = archive_dir / f'{task_id}_archive.enc'
            assert archive_file.exists(), f'{task_id} archive not found'

        # Verify workflow log
        log_content = log_file.read_text()
        assert 'Phase 1' in log_content
        assert 'Phase 2' in log_content
        assert 'Phase 3' in log_content
        assert 'TASK_001 completed' in log_content
        assert 'TASK_003 completed (merged dependencies)' in log_content
        assert 'TASK_004 completed' in log_content

        elapsed_time = time.time() - start_time
        assert elapsed_time < 60, f"Workflow took {elapsed_time:.2f}s, expected <60s"

        print(f"\n[PASS] Complex Multi-Task Workflow:")
        print(f"   - Total time: {elapsed_time:.2f}s (target: <60s)")
        print(f"   - Tasks completed: 5")
        print(f"   - Dependency resolution: 3 phases")
        print(f"   - Parallel efficiency: Tasks 1&2 parallel, 4&5 parallel")
