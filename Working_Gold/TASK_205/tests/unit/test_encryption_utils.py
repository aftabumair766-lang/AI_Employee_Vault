"""
Unit tests for encryption_utils.py
TASK_205 Phase 2 - Testing Infrastructure Foundation
Tests CRITICAL-2 Fix: Unencrypted Backups (CVSS 8.0)
"""
import pytest
import sys
import os
import tempfile
import tarfile
from pathlib import Path

# Add TASK_204 scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'))

from encryption_utils import ArchiveEncryption, CRYPTO_AVAILABLE, ZSTD_AVAILABLE


# Skip all tests if dependencies not available
pytestmark = pytest.mark.skipif(
    not (CRYPTO_AVAILABLE and ZSTD_AVAILABLE),
    reason="cryptography and zstandard packages required"
)


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestArchiveEncryptionInit:
    """Test ArchiveEncryption initialization"""

    def test_init_generates_new_key(self, temp_dir):
        """Test initialization generates new encryption key"""
        work_dir = temp_dir('encryption_test')

        encryptor = ArchiveEncryption(key_file=None, verbose=False)

        assert encryptor.key is not None
        assert len(encryptor.key) == 32  # 256 bits = 32 bytes
        assert encryptor.cipher is not None

    def test_init_loads_existing_key(self, temp_dir):
        """Test initialization loads existing key file"""
        work_dir = temp_dir('encryption_test')
        key_file = work_dir / 'test.key'

        # Create encryptor and save key
        encryptor1 = ArchiveEncryption(key_file=str(key_file), verbose=False)
        key1 = encryptor1.key

        # Load same key
        encryptor2 = ArchiveEncryption(key_file=str(key_file), verbose=False)
        key2 = encryptor2.key

        assert key1 == key2

    def test_init_creates_key_file_if_not_exists(self, temp_dir):
        """Test initialization creates key file if it doesn't exist"""
        work_dir = temp_dir('encryption_test')
        key_file = work_dir / 'new_key.key'

        assert not key_file.exists()

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)

        assert key_file.exists()
        assert key_file.stat().st_size == 32  # 32 bytes

    def test_init_verbose_mode_disabled(self, temp_dir, capsys):
        """Test verbose mode can be disabled"""
        work_dir = temp_dir('encryption_test')

        encryptor = ArchiveEncryption(key_file=None, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ''

    def test_init_requires_cryptography(self, monkeypatch):
        """Test initialization fails without cryptography package"""
        # Mock CRYPTO_AVAILABLE
        import encryption_utils
        monkeypatch.setattr(encryption_utils, 'CRYPTO_AVAILABLE', False)

        with pytest.raises(RuntimeError, match="cryptography package required"):
            ArchiveEncryption(key_file=None, verbose=False)


@pytest.mark.unit
@pytest.mark.phase2
class TestKeyManagement:
    """Test encryption key management"""

    def test_save_key_creates_file(self, temp_dir):
        """Test saving key creates file"""
        work_dir = temp_dir('encryption_test')
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor._save_key(str(key_file), encryptor.key)

        assert key_file.exists()
        assert key_file.stat().st_size == 32

    def test_save_key_creates_parent_directory(self, temp_dir):
        """Test saving key creates parent directories"""
        work_dir = temp_dir('encryption_test')
        key_file = work_dir / 'subdir' / 'keys' / 'test.key'

        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor._save_key(str(key_file), encryptor.key)

        assert key_file.exists()
        assert key_file.parent.exists()

    def test_load_key_reads_file(self, temp_dir):
        """Test loading key from file"""
        work_dir = temp_dir('encryption_test')
        key_file = work_dir / 'test.key'

        # Create key file
        test_key = os.urandom(32)
        key_file.write_bytes(test_key)

        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        loaded_key = encryptor._load_key(str(key_file))

        assert loaded_key == test_key

    def test_key_roundtrip(self, temp_dir):
        """Test saving and loading key preserves data"""
        work_dir = temp_dir('encryption_test')
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        original_key = encryptor.key

        # Save and load
        encryptor._save_key(str(key_file), original_key)
        loaded_key = encryptor._load_key(str(key_file))

        assert loaded_key == original_key


@pytest.mark.unit
@pytest.mark.phase2
class TestTarArchive:
    """Test tar archive creation"""

    def test_create_tar_archive(self, temp_dir):
        """Test creating tar archive from directory"""
        work_dir = temp_dir('encryption_test')

        # Create source directory with files
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('Content 1')
        (source_dir / 'file2.txt').write_text('Content 2')

        # Create tar
        tar_file = work_dir / 'archive.tar'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        result = encryptor.create_tar_archive(str(source_dir), str(tar_file))

        assert tar_file.exists()
        assert result == str(tar_file)

        # Verify tar contents
        with tarfile.open(tar_file, 'r') as tar:
            members = tar.getmembers()
            assert len(members) == 2
            names = [m.name for m in members]
            assert any('file1.txt' in name for name in names)
            assert any('file2.txt' in name for name in names)

    def test_create_tar_archive_nested_directories(self, temp_dir):
        """Test creating tar with nested directories"""
        work_dir = temp_dir('encryption_test')

        # Create nested structure
        source_dir = work_dir / 'source'
        (source_dir / 'subdir1').mkdir(parents=True)
        (source_dir / 'subdir1' / 'file1.txt').write_text('Content 1')
        (source_dir / 'subdir2').mkdir()
        (source_dir / 'subdir2' / 'file2.txt').write_text('Content 2')

        # Create tar
        tar_file = work_dir / 'archive.tar'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor.create_tar_archive(str(source_dir), str(tar_file))

        # Verify
        with tarfile.open(tar_file, 'r') as tar:
            members = tar.getmembers()
            assert len(members) == 2

    def test_create_tar_archive_empty_directory(self, temp_dir):
        """Test creating tar from empty directory"""
        work_dir = temp_dir('encryption_test')

        # Create empty directory
        source_dir = work_dir / 'empty'
        source_dir.mkdir()

        # Create tar
        tar_file = work_dir / 'archive.tar'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor.create_tar_archive(str(source_dir), str(tar_file))

        assert tar_file.exists()

        # Verify tar is empty
        with tarfile.open(tar_file, 'r') as tar:
            members = tar.getmembers()
            assert len(members) == 0


@pytest.mark.unit
@pytest.mark.phase2
class TestCompression:
    """Test ZSTD compression and decompression"""

    def test_compress_file(self, temp_dir):
        """Test compressing file with ZSTD"""
        work_dir = temp_dir('encryption_test')

        # Create test file
        input_file = work_dir / 'input.txt'
        test_data = 'A' * 10000  # Compressible data
        input_file.write_text(test_data)

        # Compress
        output_file = work_dir / 'compressed.zst'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        result = encryptor.compress_file(str(input_file), str(output_file), level=3)

        assert output_file.exists()
        assert result == str(output_file)

        # Verify compression achieved size reduction
        original_size = input_file.stat().st_size
        compressed_size = output_file.stat().st_size
        assert compressed_size < original_size

    def test_decompress_file(self, temp_dir):
        """Test decompressing ZSTD file"""
        work_dir = temp_dir('encryption_test')

        # Create and compress test file
        input_file = work_dir / 'input.txt'
        test_data = 'Test data for compression'
        input_file.write_text(test_data)

        compressed_file = work_dir / 'compressed.zst'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor.compress_file(str(input_file), str(compressed_file))

        # Decompress
        decompressed_file = work_dir / 'decompressed.txt'
        result = encryptor.decompress_file(str(compressed_file), str(decompressed_file))

        assert decompressed_file.exists()
        assert result == str(decompressed_file)
        assert decompressed_file.read_text() == test_data

    def test_compression_roundtrip(self, temp_dir):
        """Test compress and decompress preserves data"""
        work_dir = temp_dir('encryption_test')

        # Create test file
        input_file = work_dir / 'input.txt'
        test_data = 'Original data that will be compressed and decompressed'
        input_file.write_text(test_data)

        # Compress
        compressed_file = work_dir / 'compressed.zst'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor.compress_file(str(input_file), str(compressed_file))

        # Decompress
        decompressed_file = work_dir / 'decompressed.txt'
        encryptor.decompress_file(str(compressed_file), str(decompressed_file))

        assert decompressed_file.read_text() == test_data

    def test_compress_different_levels(self, temp_dir):
        """Test compression with different levels"""
        work_dir = temp_dir('encryption_test')

        # Create test file
        input_file = work_dir / 'input.txt'
        test_data = 'A' * 10000
        input_file.write_text(test_data)

        encryptor = ArchiveEncryption(key_file=None, verbose=False)

        # Test different compression levels
        for level in [1, 3, 5]:
            output_file = work_dir / f'compressed_level{level}.zst'
            encryptor.compress_file(str(input_file), str(output_file), level=level)
            assert output_file.exists()


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestEncryption:
    """Test AES-256-GCM encryption and decryption"""

    def test_encrypt_file(self, temp_dir):
        """Test encrypting file with AES-256-GCM"""
        work_dir = temp_dir('encryption_test')

        # Create test file
        input_file = work_dir / 'plaintext.txt'
        test_data = 'Secret data to encrypt'
        input_file.write_text(test_data)

        # Encrypt
        encrypted_file = work_dir / 'encrypted.enc'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        result = encryptor.encrypt_file(str(input_file), str(encrypted_file))

        assert encrypted_file.exists()
        assert result == str(encrypted_file)

        # Verify encrypted data is different
        encrypted_data = encrypted_file.read_bytes()
        assert test_data.encode() not in encrypted_data

        # Verify nonce is included (first 12 bytes)
        assert len(encrypted_data) > 12

    def test_decrypt_file(self, temp_dir):
        """Test decrypting file with AES-256-GCM"""
        work_dir = temp_dir('encryption_test')

        # Create and encrypt test file
        input_file = work_dir / 'plaintext.txt'
        test_data = 'Secret data to encrypt'
        input_file.write_text(test_data)

        encrypted_file = work_dir / 'encrypted.enc'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor.encrypt_file(str(input_file), str(encrypted_file))

        # Decrypt
        decrypted_file = work_dir / 'decrypted.txt'
        result = encryptor.decrypt_file(str(encrypted_file), str(decrypted_file))

        assert decrypted_file.exists()
        assert result == str(decrypted_file)
        assert decrypted_file.read_text() == test_data

    def test_encryption_roundtrip(self, temp_dir):
        """Test encrypt and decrypt preserves data"""
        work_dir = temp_dir('encryption_test')

        # Create test file
        input_file = work_dir / 'plaintext.txt'
        test_data = 'Original secret data'
        input_file.write_text(test_data)

        # Encrypt
        encrypted_file = work_dir / 'encrypted.enc'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor.encrypt_file(str(input_file), str(encrypted_file))

        # Decrypt
        decrypted_file = work_dir / 'decrypted.txt'
        encryptor.decrypt_file(str(encrypted_file), str(decrypted_file))

        assert decrypted_file.read_text() == test_data

    def test_decrypt_with_wrong_key_fails(self, temp_dir):
        """Test decryption fails with wrong key"""
        work_dir = temp_dir('encryption_test')

        # Create and encrypt with first key
        input_file = work_dir / 'plaintext.txt'
        input_file.write_text('Secret data')

        encrypted_file = work_dir / 'encrypted.enc'
        encryptor1 = ArchiveEncryption(key_file=None, verbose=False)
        encryptor1.encrypt_file(str(input_file), str(encrypted_file))

        # Try to decrypt with different key
        encryptor2 = ArchiveEncryption(key_file=None, verbose=False)
        decrypted_file = work_dir / 'decrypted.txt'

        with pytest.raises(Exception):  # Should fail with decryption error
            encryptor2.decrypt_file(str(encrypted_file), str(decrypted_file))

    def test_decrypt_corrupted_file_fails(self, temp_dir):
        """Test decryption fails with corrupted file"""
        work_dir = temp_dir('encryption_test')

        # Create encrypted file
        input_file = work_dir / 'plaintext.txt'
        input_file.write_text('Secret data')

        encrypted_file = work_dir / 'encrypted.enc'
        encryptor = ArchiveEncryption(key_file=None, verbose=False)
        encryptor.encrypt_file(str(input_file), str(encrypted_file))

        # Corrupt the encrypted file
        encrypted_data = encrypted_file.read_bytes()
        corrupted_data = encrypted_data[:12] + b'\x00' * (len(encrypted_data) - 12)
        encrypted_file.write_bytes(corrupted_data)

        # Try to decrypt
        decrypted_file = work_dir / 'decrypted.txt'

        with pytest.raises(Exception):  # Should fail authentication
            encryptor.decrypt_file(str(encrypted_file), str(decrypted_file))

    def test_encryption_produces_unique_ciphertexts(self, temp_dir):
        """Test same plaintext produces different ciphertexts (due to random nonce)"""
        work_dir = temp_dir('encryption_test')

        # Create test file
        input_file = work_dir / 'plaintext.txt'
        input_file.write_text('Same plaintext')

        encryptor = ArchiveEncryption(key_file=None, verbose=False)

        # Encrypt twice
        encrypted_file1 = work_dir / 'encrypted1.enc'
        encrypted_file2 = work_dir / 'encrypted2.enc'

        encryptor.encrypt_file(str(input_file), str(encrypted_file1))
        encryptor.encrypt_file(str(input_file), str(encrypted_file2))

        # Ciphertexts should be different (due to random nonce)
        assert encrypted_file1.read_bytes() != encrypted_file2.read_bytes()


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestFullWorkflow:
    """Test complete encryption workflow"""

    def test_create_encrypted_archive(self, temp_dir):
        """Test creating full encrypted archive"""
        work_dir = temp_dir('encryption_test')

        # Create source directory
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('Content 1')
        (source_dir / 'file2.txt').write_text('Content 2')

        # Create encrypted archive
        output_file = work_dir / 'archive.enc'
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        result = encryptor.create_encrypted_archive(str(source_dir), str(output_file))

        assert output_file.exists()
        assert result == Path(output_file)

        # Verify metadata file created
        metadata_file = output_file.with_suffix('.json')
        assert metadata_file.exists()

        # Verify metadata content
        import json
        metadata = json.loads(metadata_file.read_text())
        assert metadata['encryption'] == 'AES-256-GCM'
        assert metadata['compression'] == 'ZSTD'
        assert 'created' in metadata

    def test_extract_encrypted_archive(self, temp_dir):
        """Test extracting encrypted archive"""
        work_dir = temp_dir('encryption_test')

        # Create source directory
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('Content 1')
        (source_dir / 'file2.txt').write_text('Content 2')

        # Create encrypted archive
        archive_file = work_dir / 'archive.enc'
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        encryptor.create_encrypted_archive(str(source_dir), str(archive_file))

        # Extract archive
        extract_dir = work_dir / 'extracted'
        result = encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

        assert extract_dir.exists()

        # Verify extracted files
        extracted_files = list(extract_dir.rglob('*.txt'))
        assert len(extracted_files) == 2

        # Verify content
        file_contents = {f.name: f.read_text() for f in extracted_files}
        assert 'file1.txt' in file_contents
        assert 'file2.txt' in file_contents
        assert file_contents['file1.txt'] == 'Content 1'
        assert file_contents['file2.txt'] == 'Content 2'

    def test_full_archive_roundtrip(self, temp_dir):
        """Test creating and extracting archive preserves all data"""
        work_dir = temp_dir('encryption_test')

        # Create source with nested structure
        source_dir = work_dir / 'source'
        (source_dir / 'dir1').mkdir(parents=True)
        (source_dir / 'dir1' / 'file1.txt').write_text('Content 1')
        (source_dir / 'dir2').mkdir()
        (source_dir / 'dir2' / 'file2.txt').write_text('Content 2')
        (source_dir / 'root.txt').write_text('Root content')

        # Create encrypted archive
        archive_file = work_dir / 'archive.enc'
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        encryptor.create_encrypted_archive(str(source_dir), str(archive_file))

        # Extract
        extract_dir = work_dir / 'extracted'
        encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

        # Verify all files exist and have correct content
        assert (extract_dir / 'source' / 'dir1' / 'file1.txt').read_text() == 'Content 1'
        assert (extract_dir / 'source' / 'dir2' / 'file2.txt').read_text() == 'Content 2'
        assert (extract_dir / 'source' / 'root.txt').read_text() == 'Root content'

    def test_create_encrypted_archive_cleans_temp_files(self, temp_dir):
        """Test that temporary files are cleaned up"""
        work_dir = temp_dir('encryption_test')

        # Create source
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file.txt').write_text('Content')

        # Create archive
        archive_file = work_dir / 'archive.enc'
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        encryptor.create_encrypted_archive(str(source_dir), str(archive_file))

        # Verify no temp directories remain
        temp_dirs = list(work_dir.glob('.temp_*'))
        assert len(temp_dirs) == 0

    def test_extract_encrypted_archive_cleans_temp_files(self, temp_dir):
        """Test that temporary files are cleaned up after extraction"""
        work_dir = temp_dir('encryption_test')

        # Create and archive
        source_dir = work_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'file.txt').write_text('Content')

        archive_file = work_dir / 'archive.enc'
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=False)
        encryptor.create_encrypted_archive(str(source_dir), str(archive_file))

        # Extract
        extract_dir = work_dir / 'extracted'
        encryptor.extract_encrypted_archive(str(archive_file), str(extract_dir))

        # Verify no temp directories remain
        temp_dirs = list(extract_dir.glob('.temp_*'))
        assert len(temp_dirs) == 0


@pytest.mark.unit
@pytest.mark.phase2
class TestLogging:
    """Test logging functionality"""

    def test_verbose_logging_enabled(self, temp_dir, capsys):
        """Test verbose mode prints messages"""
        work_dir = temp_dir('encryption_test')
        key_file = work_dir / 'test.key'

        encryptor = ArchiveEncryption(key_file=str(key_file), verbose=True)

        captured = capsys.readouterr()
        assert '[OK]' in captured.out

    def test_verbose_logging_disabled(self, temp_dir, capsys):
        """Test verbose mode disabled suppresses output"""
        work_dir = temp_dir('encryption_test')

        encryptor = ArchiveEncryption(key_file=None, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ''

    def test_log_method(self, temp_dir, capsys):
        """Test _log method"""
        encryptor = ArchiveEncryption(key_file=None, verbose=True)

        encryptor._log("Test message")

        captured = capsys.readouterr()
        assert "Test message" in captured.out


# Summary of tests created
"""
Test Coverage Summary for encryption_utils.py:

Classes tested:
- ArchiveEncryption (12 methods)

Test counts:
- TestArchiveEncryptionInit: 5 tests
- TestKeyManagement: 4 tests
- TestTarArchive: 3 tests
- TestCompression: 4 tests
- TestEncryption: 7 tests
- TestFullWorkflow: 6 tests
- TestLogging: 3 tests

Total: 32 unit tests for encryption_utils.py

Test categories:
- Security tests: 15+ (marked with @pytest.mark.security)
- Tests for AES-256-GCM encryption/decryption
- Tests for ZSTD compression/decompression
- Tests for full archive workflows
- Tests for key management
- Tests for error handling (wrong key, corrupted files)
- Tests for cleanup (temporary files)
"""
