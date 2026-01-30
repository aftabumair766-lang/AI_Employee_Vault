"""
Unit tests for integrity_checker.py
TASK_205 Phase 2 - Testing Infrastructure Foundation
Tests CRITICAL-6 Fix: No Backup Integrity Verification (CVSS 6.5)
"""
import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'))

from integrity_checker import IntegrityChecker


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestGenerateChecksum:
    """Test checksum generation"""

    def test_generate_checksum_for_file(self, temp_dir):
        """Test generating SHA-256 checksum for file"""
        work_dir = temp_dir('integrity_test')
        test_file = work_dir / 'test.txt'
        test_file.write_text('Hello World')

        checker = IntegrityChecker(verbose=False)
        checksum = checker.generate_checksum(str(test_file))

        assert checksum is not None
        assert len(checksum) == 64  # SHA-256 is 64 hex chars
        # Known SHA-256 for "Hello World"
        assert checksum == 'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e'

    def test_generate_checksum_consistent(self, temp_dir):
        """Test checksum is consistent for same content"""
        work_dir = temp_dir('integrity_test')
        test_file = work_dir / 'test.txt'
        test_file.write_text('Test content')

        checker = IntegrityChecker(verbose=False)
        checksum1 = checker.generate_checksum(str(test_file))
        checksum2 = checker.generate_checksum(str(test_file))

        assert checksum1 == checksum2

    def test_generate_checksum_different_content(self, temp_dir):
        """Test different content produces different checksum"""
        work_dir = temp_dir('integrity_test')
        file1 = work_dir / 'test1.txt'
        file2 = work_dir / 'test2.txt'
        file1.write_text('Content A')
        file2.write_text('Content B')

        checker = IntegrityChecker(verbose=False)
        checksum1 = checker.generate_checksum(str(file1))
        checksum2 = checker.generate_checksum(str(file2))

        assert checksum1 != checksum2

    def test_generate_checksum_nonexistent_file(self, temp_dir):
        """Test checksum for nonexistent file returns None"""
        work_dir = temp_dir('integrity_test')
        nonexistent = work_dir / 'nonexistent.txt'

        checker = IntegrityChecker(verbose=False)
        checksum = checker.generate_checksum(str(nonexistent))

        assert checksum is None


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestCreateIntegrityFile:
    """Test integrity file creation"""

    def test_create_integrity_file(self, temp_dir):
        """Test creating integrity.json file"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()
        (archive_dir / 'file1.txt').write_text('Content 1')
        (archive_dir / 'file2.txt').write_text('Content 2')

        checker = IntegrityChecker(verbose=False)
        result = checker.create_integrity_file(str(archive_dir))

        assert result is not None
        assert 'version' in result
        assert 'files' in result
        assert len(result['files']) == 2

    def test_integrity_file_created_on_disk(self, temp_dir):
        """Test integrity.json file is created on disk"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()
        (archive_dir / 'test.txt').write_text('Test')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(archive_dir))

        integrity_file = archive_dir / 'integrity.json'
        assert integrity_file.exists()

    def test_integrity_file_contains_checksums(self, temp_dir):
        """Test integrity file contains checksums for all files"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()
        (archive_dir / 'file1.txt').write_text('Content 1')
        (archive_dir / 'file2.txt').write_text('Content 2')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(archive_dir))

        integrity_file = archive_dir / 'integrity.json'
        data = json.loads(integrity_file.read_text())

        assert 'file1.txt' in data['files']
        assert 'file2.txt' in data['files']
        assert 'sha256' in data['files']['file1.txt']
        assert 'size' in data['files']['file1.txt']

    def test_integrity_file_nested_structure(self, temp_dir):
        """Test integrity file with nested directory structure"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        (archive_dir / 'subdir').mkdir(parents=True)
        (archive_dir / 'file1.txt').write_text('Content 1')
        (archive_dir / 'subdir' / 'file2.txt').write_text('Content 2')

        checker = IntegrityChecker(verbose=False)
        result = checker.create_integrity_file(str(archive_dir))

        assert result is not None
        assert len(result['files']) == 2
        assert any('subdir' in path for path in result['files'].keys())

    def test_integrity_file_nonexistent_directory(self, temp_dir):
        """Test creating integrity file for nonexistent directory"""
        work_dir = temp_dir('integrity_test')
        nonexistent = work_dir / 'nonexistent'

        checker = IntegrityChecker(verbose=False)
        result = checker.create_integrity_file(str(nonexistent))

        assert result is None


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestVerifyIntegrity:
    """Test integrity verification"""

    def test_verify_integrity_valid(self, temp_dir):
        """Test verifying integrity of unmodified archive"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()
        (archive_dir / 'test.txt').write_text('Test content')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(archive_dir))

        is_valid, errors = checker.verify_integrity(str(archive_dir))

        assert is_valid is True
        assert len(errors) == 0

    def test_verify_integrity_modified_file(self, temp_dir):
        """Test verification fails when file is modified"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()
        test_file = archive_dir / 'test.txt'
        test_file.write_text('Original content')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(archive_dir))

        # Modify file
        test_file.write_text('Modified content')

        is_valid, errors = checker.verify_integrity(str(archive_dir))

        assert is_valid is False
        assert len(errors) > 0
        assert any('mismatch' in error.lower() for error in errors)

    def test_verify_integrity_missing_file(self, temp_dir):
        """Test verification fails when file is missing"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()
        test_file = archive_dir / 'test.txt'
        test_file.write_text('Content')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(archive_dir))

        # Delete file
        test_file.unlink()

        is_valid, errors = checker.verify_integrity(str(archive_dir))

        assert is_valid is False
        assert len(errors) > 0
        assert any('missing' in error.lower() for error in errors)

    def test_verify_integrity_no_integrity_file(self, temp_dir):
        """Test verification fails when integrity.json is missing"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()

        checker = IntegrityChecker(verbose=False)
        is_valid, errors = checker.verify_integrity(str(archive_dir))

        assert is_valid is False
        assert len(errors) > 0

    def test_verify_integrity_multiple_files(self, temp_dir):
        """Test verification with multiple files"""
        work_dir = temp_dir('integrity_test')
        archive_dir = work_dir / 'archive'
        archive_dir.mkdir()
        (archive_dir / 'file1.txt').write_text('Content 1')
        (archive_dir / 'file2.txt').write_text('Content 2')
        (archive_dir / 'file3.txt').write_text('Content 3')

        checker = IntegrityChecker(verbose=False)
        checker.create_integrity_file(str(archive_dir))

        is_valid, errors = checker.verify_integrity(str(archive_dir))

        assert is_valid is True
        assert len(errors) == 0


# Total: 15 test methods
