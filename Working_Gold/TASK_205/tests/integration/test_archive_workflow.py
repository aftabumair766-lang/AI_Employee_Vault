"""
Integration tests for archive workflow with encryption and integrity
TASK_205 Phase 3 - Testing Infrastructure Foundation
Tests complete archival workflows: encryption + compression + integrity
"""
import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'))

from encryption_utils import ArchiveEncryption, CRYPTO_AVAILABLE, ZSTD_AVAILABLE
from integrity_checker import IntegrityChecker
from path_validator import PathValidator

# Skip if dependencies not available
pytestmark = pytest.mark.skipif(
    not (CRYPTO_AVAILABLE and ZSTD_AVAILABLE),
    reason="cryptography and zstandard required"
)


@pytest.mark.integration
@pytest.mark.phase3
@pytest.mark.security
class TestCompleteArchivalWorkflow:
    """Test complete workflow: create → encrypt → verify integrity → extract"""

    def test_full_archive_workflow_with_integrity(self, temp_dir):
        """Test complete archival workflow with integrity checking"""
        work_dir = temp_dir('archive_workflow')

        # Step 1: Create source files
        source_dir = work_dir / 'TASK_099'
        source_dir.mkdir()
        (source_dir / 'output.txt').write_text('Task output')
        (source_dir / 'report.md').write_text('# Task Report\n\nCompleted successfully')
        (source_dir / 'data.json').write_text(json.dumps({'result': 'success'}))

        # Step 2: Generate integrity checksums BEFORE encryption
        checker = IntegrityChecker(verbose=False)
        integrity_data = checker.create_integrity_file(str(source_dir))

        assert integrity_data is not None
        assert len(integrity_data['files']) == 3  # 3 files (integrity.json excluded from own checksums)
        assert (source_dir / 'integrity.json').exists()

        # Step 3: Verify integrity before archival
        is_valid, errors = checker.verify_integrity(str(source_dir))
        assert is_valid is True
        assert len(errors) == 0

        # Step 4: Create encrypted archive
        archive_file = work_dir / 'TASK_099_archive.enc'
        key_file = work_dir / 'encryption.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(source_dir), str(archive_file))

        assert archive_file.exists()
        assert result == Path(archive_file)

        # Verify metadata file
        metadata_file = archive_file.with_suffix('.json')
        assert metadata_file.exists()
        metadata = json.loads(metadata_file.read_text())
        assert metadata['encryption'] == 'AES-256-GCM'
        assert metadata['compression'] == 'ZSTD'

        # Step 5: Extract archive
        extract_dir = work_dir / 'extracted'
        encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

        # Step 6: Verify integrity AFTER extraction
        extracted_task_dir = extract_dir / 'TASK_099'
        is_valid, errors = checker.verify_integrity(str(extracted_task_dir))

        assert is_valid is True
        assert len(errors) == 0

        # Step 7: Verify all files extracted correctly
        assert (extracted_task_dir / 'output.txt').read_text() == 'Task output'
        assert (extracted_task_dir / 'data.json').exists()
        assert (extracted_task_dir / 'integrity.json').exists()

    def test_archive_with_tamper_detection(self, temp_dir):
        """Test that tampering is detected via integrity check"""
        work_dir = temp_dir('tamper_test')

        # Create source with integrity
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file.txt').write_text('Original content')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(source_dir))

        # Tamper with file
        (source_dir / 'file.txt').write_text('TAMPERED content')

        # Verify integrity - should fail
        is_valid, errors = checker.verify_integrity(str(source_dir))

        assert is_valid is False
        assert len(errors) > 0
        assert any('mismatch' in error.lower() for error in errors)

    def test_archive_workflow_with_path_validation(self, temp_dir):
        """Test archival workflow with safe path validation"""
        work_dir = temp_dir('archive_path_test')

        # Create source in safe location
        validator = PathValidator(vault_root=str(work_dir))

        # Validate archive path
        archive_base = 'Archive_Gold'
        archive_path = validator.safe_join(archive_base, 'Completed', 'TASK_250')
        archive_path.mkdir(parents=True, exist_ok=True)

        # Create files safely
        safe_file = validator.safe_join(archive_base, 'Completed', 'TASK_250', 'output.txt')
        safe_file.write_text('Archived output')

        assert safe_file.exists()
        assert safe_file.is_relative_to(work_dir)

        # Verify path is safe
        assert validator.is_safe_path(str(safe_file)) is True


@pytest.mark.integration
@pytest.mark.phase3
@pytest.mark.security
class TestEncryptionIntegrityWorkflow:
    """Test encryption and integrity together"""

    def test_encrypted_archive_integrity_preserved(self, temp_dir):
        """Test integrity is preserved through encryption/decryption"""
        work_dir = temp_dir('encrypt_integrity')

        # Create source
        source_dir = work_dir / 'task_data'
        source_dir.mkdir()
        (source_dir / 'sensitive.txt').write_text('Sensitive data')

        # Generate integrity checksums
        checker = IntegrityChecker(verbose=False)
        original_integrity = checker.create_integrity_file(str(source_dir))
        original_checksum = original_integrity['files']['sensitive.txt']['sha256']

        # Encrypt
        archive_file = work_dir / 'archive.enc'
        key_file = work_dir / 'key.bin'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        encryptor.create_encrypted_archive(str(source_dir), str(archive_file))

        # Extract
        extract_dir = work_dir / 'extracted'
        encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

        # Verify integrity after extraction
        extracted_task = extract_dir / 'task_data'
        is_valid, errors = checker.verify_integrity(str(extracted_task))

        assert is_valid is True

        # Verify checksum matches original
        integrity_data = json.loads((extracted_task / 'integrity.json').read_text())
        extracted_checksum = integrity_data['files']['sensitive.txt']['sha256']
        assert extracted_checksum == original_checksum

    def test_wrong_key_prevents_extraction(self, temp_dir):
        """Test that wrong decryption key prevents data access"""
        work_dir = temp_dir('wrong_key_test')

        # Create and encrypt with key 1
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'data.txt').write_text('Secret data')

        archive_file = work_dir / 'archive.enc'
        key_file1 = work_dir / 'key1.bin'

        encryptor1 = ArchiveEncryption(key_file=str(key_file1), verbose=False)
        encryptor1.create_encrypted_archive(str(source_dir), str(archive_file))

        # Try to extract with different key
        key_file2 = work_dir / 'key2.bin'
        encryptor2 = ArchiveEncryption(key_file=str(key_file2), verbose=False)

        extract_dir = work_dir / 'extracted'

        # Should fail with wrong key
        with pytest.raises(Exception):
            encryptor2.extract_encrypted_archive(str(archive_file), str(extract_dir))


@pytest.mark.integration
@pytest.mark.phase3
class TestMultiTaskArchivalWorkflow:
    """Test archiving multiple tasks"""

    def test_multiple_task_archival(self, temp_dir):
        """Test archiving multiple completed tasks"""
        work_dir = temp_dir('multi_archive')

        task_ids = ['TASK_001', 'TASK_002', 'TASK_003']
        checker = IntegrityChecker(verbose=False)

        for task_id in task_ids:
            # Create task output
            task_dir = work_dir / task_id
            task_dir.mkdir()
            (task_dir / 'output.txt').write_text(f'Output from {task_id}')

            # Generate integrity
            integrity = checker.create_integrity_file(str(task_dir))
            assert integrity is not None

            # Verify integrity
            is_valid, _ = checker.verify_integrity(str(task_dir))
            assert is_valid is True

        # Verify all tasks have integrity files
        for task_id in task_ids:
            integrity_file = work_dir / task_id / 'integrity.json'
            assert integrity_file.exists()

    def test_incremental_archival(self, temp_dir):
        """Test incremental archival of tasks"""
        work_dir = temp_dir('incremental')
        archive_dir = work_dir / 'Archive_Gold' / 'Completed'
        archive_dir.mkdir(parents=True)

        # Archive task 1
        task1_src = work_dir / 'TASK_201'
        task1_src.mkdir()
        (task1_src / 'result.txt').write_text('Result 1')

        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        archive1 = archive_dir / 'TASK_201.enc'
        encryptor.create_encrypted_archive(str(task1_src), str(archive1))

        assert archive1.exists()

        # Archive task 2
        task2_src = work_dir / 'TASK_202'
        task2_src.mkdir()
        (task2_src / 'result.txt').write_text('Result 2')

        archive2 = archive_dir / 'TASK_202.enc'
        encryptor.create_encrypted_archive(str(task2_src), str(archive2))

        assert archive2.exists()

        # Verify both archives exist
        archives = list(archive_dir.glob('*.enc'))
        assert len(archives) == 2


@pytest.mark.integration
@pytest.mark.phase3
class TestArchiveRecoveryWorkflow:
    """Test archive recovery and error scenarios"""

    def test_corrupted_file_detected(self, temp_dir):
        """Test that corrupted files are detected"""
        work_dir = temp_dir('corruption_test')

        # Create files with integrity
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('Content 1')
        (source_dir / 'file2.txt').write_text('Content 2')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(source_dir))

        # Corrupt one file
        (source_dir / 'file1.txt').write_text('CORRUPTED')

        # Verify - should detect corruption
        is_valid, errors = checker.verify_integrity(str(source_dir))

        assert is_valid is False
        assert any('file1.txt' in error for error in errors)

    def test_missing_file_detected(self, temp_dir):
        """Test that missing files are detected"""
        work_dir = temp_dir('missing_test')

        # Create files with integrity
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('Content 1')
        (source_dir / 'file2.txt').write_text('Content 2')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(source_dir))

        # Delete one file
        (source_dir / 'file2.txt').unlink()

        # Verify - should detect missing file
        is_valid, errors = checker.verify_integrity(str(source_dir))

        assert is_valid is False
        assert any('missing' in error.lower() for error in errors)


# Total: 13 integration test methods
