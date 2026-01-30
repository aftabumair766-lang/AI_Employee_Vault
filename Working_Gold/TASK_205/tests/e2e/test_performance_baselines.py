"""
E2E Test: Performance Baseline Testing

Establishes performance baselines for critical operations.

Benchmarks covered:
1. Task creation performance (100 tasks)
2. State validation performance (1000 validations)
3. File operation performance (100 files)
4. Encryption/decryption performance (various sizes)

Performance baselines:
- Task creation: <100ms/task
- State validation: <50ms/validation
- File operations: <10ms/op
- Encryption: <500ms for 1MB file
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


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestTaskCreationPerformance:
    """Benchmark task creation performance"""

    def test_create_100_tasks_performance(self, temp_dir):
        """
        Benchmark: Create 100 task specifications

        Target: <100ms per task (10 seconds total for 100 tasks)
        """
        work_dir = temp_dir('task_creation_perf')

        task_specs = []
        start_time = time.time()

        for i in range(1, 101):  # Start at 1, not 0
            task_spec = {
                'task_id': f'TASK_{i:03d}',
                'description': f'Performance test task {i}',
                'level': 'Bronze',
                'priority': 'LOW',
                'state': 'NEEDS_ACTION',
                'created': datetime.now().isoformat(),
            }

            # Validate task specification (this is the expensive operation)
            validated_spec = InputValidator.validate_task_specification(task_spec)
            task_specs.append(validated_spec)

        elapsed_time = time.time() - start_time
        time_per_task = (elapsed_time / 100) * 1000  # Convert to ms

        # Verify all created
        assert len(task_specs) == 100

        # Performance assertion
        assert time_per_task < 100, f"Task creation took {time_per_task:.2f}ms per task, target: <100ms"

        print(f"\n[PASS] Task Creation Performance:")
        print(f"   - Total time: {elapsed_time:.2f}s")
        print(f"   - Time per task: {time_per_task:.2f}ms (target: <100ms)")
        print(f"   - Tasks created: 100")
        print(f"   - Throughput: {100/elapsed_time:.1f} tasks/sec")


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestStateValidationPerformance:
    """Benchmark state transition validation performance"""

    def test_1000_state_validations_performance(self):
        """
        Benchmark: Validate 1000 state transitions

        Target: <50ms per validation
        """
        verifier = ApprovalVerifier()

        # Test various transition combinations
        transitions = [
            ('NEEDS_ACTION', 'PLANNING', False, 'Bronze'),
            ('PLANNING', 'AWAITING_APPROVAL', False, 'Gold'),
            ('AWAITING_APPROVAL', 'IN_PROGRESS', True, 'Gold'),
            ('IN_PROGRESS', 'COMPLETED', False, 'Bronze'),
            ('COMPLETED', 'DONE', False, 'Bronze'),
            ('NEEDS_ACTION', 'IN_PROGRESS', False, 'Bronze'),
            ('IN_PROGRESS', 'FAILED', False, 'Bronze'),
            ('IN_PROGRESS', 'BLOCKED', False, 'Silver'),
        ]

        validation_count = 0
        start_time = time.time()

        # Run 1000 validations (cycle through transitions)
        for i in range(1000):
            from_state, to_state, has_approval, level = transitions[i % len(transitions)]

            is_valid, reason = verifier.validate_state_transition(
                from_state, to_state, has_approval=has_approval, task_level=level
            )

            # Verify we got a result
            assert isinstance(is_valid, bool)
            assert isinstance(reason, str)
            validation_count += 1

        elapsed_time = time.time() - start_time
        time_per_validation = (elapsed_time / 1000) * 1000  # Convert to ms

        assert validation_count == 1000

        # Performance assertion
        assert time_per_validation < 50, f"Validation took {time_per_validation:.2f}ms each, target: <50ms"

        print(f"\n[PASS] State Validation Performance:")
        print(f"   - Total time: {elapsed_time:.2f}s")
        print(f"   - Time per validation: {time_per_validation:.2f}ms (target: <50ms)")
        print(f"   - Validations: 1000")
        print(f"   - Throughput: {1000/elapsed_time:.1f} validations/sec")


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestFileOperationPerformance:
    """Benchmark file operation performance"""

    def test_100_file_operations_performance(self, temp_dir):
        """
        Benchmark: Read and write 100 files

        Target: <10ms per operation (read + write)
        """
        work_dir = temp_dir('file_ops_perf')
        files_dir = work_dir / 'files'
        files_dir.mkdir()

        # Test data
        test_content = "Test file content\n" * 10  # ~200 bytes

        operations = 0
        start_time = time.time()

        # Write 100 files
        for i in range(100):
            file_path = files_dir / f'file_{i:03d}.txt'
            file_path.write_text(test_content)
            operations += 1

        # Read 100 files
        for i in range(100):
            file_path = files_dir / f'file_{i:03d}.txt'
            content = file_path.read_text()
            assert content == test_content
            operations += 1

        elapsed_time = time.time() - start_time
        time_per_operation = (elapsed_time / operations) * 1000  # Convert to ms

        assert operations == 200  # 100 writes + 100 reads

        # Performance assertion
        assert time_per_operation < 10, f"File ops took {time_per_operation:.2f}ms each, target: <10ms"

        print(f"\n[PASS] File Operation Performance:")
        print(f"   - Total time: {elapsed_time:.2f}s")
        print(f"   - Time per operation: {time_per_operation:.2f}ms (target: <10ms)")
        print(f"   - Operations: {operations} (100 writes + 100 reads)")
        print(f"   - Throughput: {operations/elapsed_time:.1f} ops/sec")


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestEncryptionPerformance:
    """Benchmark encryption/decryption performance"""

    def test_encryption_various_file_sizes(self, temp_dir):
        """
        Benchmark: Encrypt and decrypt files of various sizes

        Targets:
        - 1KB file: <50ms
        - 100KB file: <200ms
        - 1MB file: <500ms
        """
        work_dir = temp_dir('encryption_perf')

        encryptor = ArchiveEncryption(key_file=None, verbose=False)  # Generate new key

        # Test various file sizes
        test_sizes = {
            '1KB': 1 * 1024,
            '100KB': 100 * 1024,
            '1MB': 1 * 1024 * 1024,
        }

        targets = {
            '1KB': 0.05,    # 50ms
            '100KB': 0.20,  # 200ms
            '1MB': 0.50,    # 500ms
        }

        results = {}

        for size_name, size_bytes in test_sizes.items():
            # Create test file
            test_file = work_dir / f'test_{size_name}.dat'
            test_data = 'X' * size_bytes
            test_file.write_text(test_data)

            # Benchmark encryption
            encrypted_file = work_dir / f'test_{size_name}.enc'

            encrypt_start = time.time()
            encryptor.encrypt_file(str(test_file), str(encrypted_file))
            encrypt_time = time.time() - encrypt_start

            assert encrypted_file.exists()

            # Benchmark decryption
            decrypted_file = work_dir / f'test_{size_name}_decrypted.dat'

            decrypt_start = time.time()
            encryptor.decrypt_file(str(encrypted_file), str(decrypted_file))
            decrypt_time = time.time() - decrypt_start

            assert decrypted_file.exists()

            # Verify decrypted content matches
            decrypted_data = decrypted_file.read_text()
            assert decrypted_data == test_data

            total_time = encrypt_time + decrypt_time
            results[size_name] = {
                'encrypt_time': encrypt_time,
                'decrypt_time': decrypt_time,
                'total_time': total_time,
            }

            # Performance assertion
            target_time = targets[size_name]
            assert total_time < target_time, f"{size_name} took {total_time:.3f}s, target: <{target_time}s"

        print(f"\n[PASS] Encryption/Decryption Performance:")
        for size_name, times in results.items():
            print(f"   - {size_name}: {times['total_time']*1000:.1f}ms " +
                  f"(encrypt: {times['encrypt_time']*1000:.1f}ms, " +
                  f"decrypt: {times['decrypt_time']*1000:.1f}ms)")


    def test_compression_efficiency(self, temp_dir):
        """
        Benchmark: Test ZSTD compression efficiency

        Measures compression ratio and speed
        """
        work_dir = temp_dir('compression_perf')

        encryptor = ArchiveEncryption(key_file=None, verbose=False)

        # Create highly compressible file (repeated text)
        test_file = work_dir / 'compressible.txt'
        test_data = "This is repeated text.\n" * 10000  # ~230KB
        test_file.write_text(test_data)

        original_size = test_file.stat().st_size

        # Compress
        compressed_file = work_dir / 'compressed.zst'

        compress_start = time.time()
        encryptor.compress_file(str(test_file), str(compressed_file), level=3)
        compress_time = time.time() - compress_start

        compressed_size = compressed_file.stat().st_size
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

        # Decompress
        decompressed_file = work_dir / 'decompressed.txt'

        decompress_start = time.time()
        encryptor.decompress_file(str(compressed_file), str(decompressed_file))
        decompress_time = time.time() - decompress_start

        # Verify
        decompressed_data = decompressed_file.read_text()
        assert decompressed_data == test_data

        # Performance expectations
        assert compression_ratio > 5, f"Compression ratio {compression_ratio:.1f}x, expected >5x for repetitive data"
        assert compress_time < 1.0, f"Compression took {compress_time:.2f}s, expected <1s"
        assert decompress_time < 0.5, f"Decompression took {decompress_time:.2f}s, expected <0.5s"

        print(f"\n[PASS] Compression Efficiency:")
        print(f"   - Original size: {original_size/1024:.1f}KB")
        print(f"   - Compressed size: {compressed_size/1024:.1f}KB")
        print(f"   - Compression ratio: {compression_ratio:.1f}x")
        print(f"   - Compression time: {compress_time*1000:.1f}ms")
        print(f"   - Decompression time: {decompress_time*1000:.1f}ms")


@pytest.mark.e2e
@pytest.mark.phase4
@pytest.mark.slow
class TestIntegrityCheckPerformance:
    """Benchmark integrity checking performance"""

    def test_integrity_check_100_files(self, temp_dir):
        """
        Benchmark: Generate and verify integrity checksums for 100 files

        Target: <2 seconds total
        """
        work_dir = temp_dir('integrity_perf')
        task_dir = work_dir / 'task'
        task_dir.mkdir()

        # Create 100 files
        for i in range(100):
            file_path = task_dir / f'file_{i:03d}.txt'
            file_path.write_text(f'File content {i}\n' * 50)

        checker = IntegrityChecker(verbose=False)

        # Benchmark checksum generation
        generate_start = time.time()
        integrity_data = checker.create_integrity_file(str(task_dir))
        generate_time = time.time() - generate_start

        assert integrity_data is not None
        assert len(integrity_data['files']) == 100

        # Benchmark verification
        verify_start = time.time()
        is_valid, errors = checker.verify_integrity(str(task_dir))
        verify_time = time.time() - verify_start

        assert is_valid is True
        assert len(errors) == 0

        total_time = generate_time + verify_time

        # Performance assertion
        assert total_time < 2.0, f"Integrity ops took {total_time:.2f}s, target: <2s"

        print(f"\n[PASS] Integrity Check Performance:")
        print(f"   - Files: 100")
        print(f"   - Generate time: {generate_time*1000:.1f}ms")
        print(f"   - Verify time: {verify_time*1000:.1f}ms")
        print(f"   - Total time: {total_time*1000:.1f}ms (target: <2000ms)")
        print(f"   - Throughput: {100/total_time:.1f} files/sec")
