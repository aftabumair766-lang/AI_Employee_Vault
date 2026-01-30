"""
Unit tests for secure_logging.py
TASK_205 Phase 2 - Testing Infrastructure Foundation
Tests CRITICAL-8 Fix: Sensitive Data in Logs (CVSS 6.0)
"""
import pytest
import sys
import logging
from pathlib import Path
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'))

from secure_logging import SecureLogger, SanitizingFormatter


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestSanitizingFormatter:
    """Test SanitizingFormatter"""

    def test_formatter_sanitizes_passwords(self):
        """Test formatter sanitizes password in log message"""
        formatter = SanitizingFormatter('[%(levelname)s] %(message)s')
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='User login password=secret123', args=(), exc_info=None
        )
        result = formatter.format(record)
        assert 'secret123' not in result
        assert '***' in result

    def test_formatter_sanitizes_api_keys(self):
        """Test formatter sanitizes API keys"""
        formatter = SanitizingFormatter('[%(levelname)s] %(message)s')
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='API request api_key=abc123xyz', args=(), exc_info=None
        )
        result = formatter.format(record)
        assert 'abc123xyz' not in result


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestSecureLogger:
    """Test SecureLogger"""

    def test_logger_initialization(self, temp_dir):
        """Test logger initialization"""
        work_dir = temp_dir('logging_test')
        log_file = work_dir / 'test.log'

        logger = SecureLogger('test_logger', log_file=str(log_file), console=False)

        assert logger.logger.name == 'test_logger'
        assert len(logger.logger.handlers) > 0

    def test_logger_creates_log_file(self, temp_dir):
        """Test logger creates log file"""
        work_dir = temp_dir('logging_test')
        log_file = work_dir / 'test.log'

        logger = SecureLogger('test_logger', log_file=str(log_file), console=False)
        logger.info('Test message')

        assert log_file.exists()

    def test_logger_sanitizes_sensitive_data(self, temp_dir):
        """Test logger sanitizes sensitive data in logs"""
        work_dir = temp_dir('logging_test')
        log_file = work_dir / 'test.log'

        logger = SecureLogger('test_logger', log_file=str(log_file), console=False)
        logger.info('User password=secret123')

        content = log_file.read_text()
        assert 'secret123' not in content
        assert '***' in content

    def test_logger_info_level(self, temp_dir):
        """Test info level logging"""
        work_dir = temp_dir('logging_test')
        log_file = work_dir / 'test.log'

        logger = SecureLogger('test_logger', log_file=str(log_file), console=False)
        logger.info('Info message')

        content = log_file.read_text()
        assert 'INFO' in content
        assert 'Info message' in content

    def test_logger_error_level(self, temp_dir):
        """Test error level logging"""
        work_dir = temp_dir('logging_test')
        log_file = work_dir / 'test.log'

        logger = SecureLogger('test_logger', log_file=str(log_file), console=False)
        logger.error('Error message')

        content = log_file.read_text()
        assert 'ERROR' in content
        assert 'Error message' in content

    def test_logger_without_file(self, capsys):
        """Test logger without file (console only)"""
        logger = SecureLogger('test_logger', log_file=None, console=True)
        logger.info('Console message')

        captured = capsys.readouterr()
        assert 'Console message' in captured.out


# Total: 8 test methods
