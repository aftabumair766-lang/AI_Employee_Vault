"""
Unit tests for input_validator.py
TASK_205 Phase 2 - Testing Infrastructure Foundation
Tests CRITICAL-4 Fix: Insufficient Input Validation (CVSS 7.0)
Tests CRITICAL-8 Fix: Sensitive Data in Logs (CVSS 6.0)
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'))

from input_validator import InputValidator, ValidationError


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestValidateTaskID:
    """Test task ID validation"""

    @pytest.mark.parametrize("task_id,expected_level", [
        ("TASK_001", "Bronze"),
        ("TASK_050", "Bronze"),
        ("TASK_100", "Bronze"),
        ("TASK_101", "Silver"),
        ("TASK_150", "Silver"),
        ("TASK_200", "Silver"),
        ("TASK_201", "Gold"),
        ("TASK_250", "Gold"),
        ("TASK_300", "Gold"),
    ])
    def test_valid_task_ids(self, task_id, expected_level):
        """Test valid task IDs with correct levels"""
        result_id, result_level = InputValidator.validate_task_id(task_id)
        assert result_id == task_id
        assert result_level == expected_level

    @pytest.mark.parametrize("task_id", [
        "TASK_000",  # Out of range
        "TASK_301",  # Out of range
        "TASK_999",  # Out of range
        "task_001",  # Lowercase
        "TASK001",   # No underscore
        "TASK_1",    # Wrong format
        "TASK_1234", # Too many digits
        "TEST_001",  # Wrong prefix
        "",          # Empty
        "TASK_ABC",  # Non-numeric
    ])
    def test_invalid_task_ids(self, task_id):
        """Test invalid task IDs raise ValueError"""
        with pytest.raises(ValueError):
            InputValidator.validate_task_id(task_id)


@pytest.mark.unit
@pytest.mark.phase2
class TestValidateTimestamp:
    """Test timestamp validation"""

    @pytest.mark.parametrize("timestamp", [
        "2026-01-29 12:30:00.000",
        "2025-12-31 23:59:59.999",
        "2000-01-01 00:00:00.000",
    ])
    def test_valid_timestamps(self, timestamp):
        """Test valid ISO 8601 timestamps"""
        result = InputValidator.validate_timestamp(timestamp)
        assert isinstance(result, datetime)

    @pytest.mark.parametrize("timestamp", [
        "2026-01-29 12:30:00",      # No milliseconds
        "2026-1-29 12:30:00.000",   # Single digit month
        "2026-01-29 12:30:00.00",   # Only 2 decimal places
        "2026-01-29T12:30:00.000",  # Wrong separator
        "invalid",                   # Invalid format
        "",                          # Empty
        "2026-13-01 12:30:00.000",  # Invalid month
    ])
    def test_invalid_timestamps(self, timestamp):
        """Test invalid timestamps raise ValueError"""
        with pytest.raises(ValueError):
            InputValidator.validate_timestamp(timestamp)


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestValidateFilename:
    """Test filename validation"""

    @pytest.mark.parametrize("filename", [
        "test_file.txt",
        "test-file-123.log",
        "file.tar.gz",
        "README.md",
        "a" * 255,  # Max length
    ])
    def test_valid_filenames(self, filename):
        """Test valid filenames"""
        result = InputValidator.validate_filename(filename)
        assert result == filename

    @pytest.mark.parametrize("filename", [
        "../etc/passwd",     # Directory traversal
        "test file.txt",     # Space
        ".hidden",           # Hidden file
        "CON",               # Reserved name
        "PRN",               # Reserved name
        "AUX",               # Reserved name
        "NUL",               # Reserved name
        "",                  # Empty
        "a" * 256,          # Too long
        "file@name.txt",    # Invalid character
        "file#name.txt",    # Invalid character
    ])
    def test_invalid_filenames(self, filename):
        """Test invalid filenames raise ValueError"""
        with pytest.raises(ValueError):
            InputValidator.validate_filename(filename)

    def test_filename_max_length_custom(self):
        """Test custom max length"""
        long_name = "a" * 50
        result = InputValidator.validate_filename(long_name, max_length=100)
        assert result == long_name

        with pytest.raises(ValueError, match="too long"):
            InputValidator.validate_filename(long_name, max_length=10)


@pytest.mark.unit
@pytest.mark.phase2
class TestValidateState:
    """Test state validation"""

    @pytest.mark.parametrize("state", [
        "NEEDS_ACTION",
        "PLANNING",
        "AWAITING_APPROVAL",
        "IN_PROGRESS",
        "COMPLETED",
        "DONE",
        "FAILED",
        "BLOCKED",
    ])
    def test_valid_states(self, state):
        """Test all valid states"""
        result = InputValidator.validate_state(state)
        assert result == state

    @pytest.mark.parametrize("state", [
        "INVALID",
        "PENDING",
        "RUNNING",
        "in_progress",  # Lowercase
        "",
    ])
    def test_invalid_states(self, state):
        """Test invalid states raise ValueError"""
        with pytest.raises(ValueError, match="Invalid state"):
            InputValidator.validate_state(state)


@pytest.mark.unit
@pytest.mark.phase2
class TestValidateLevel:
    """Test level validation"""

    @pytest.mark.parametrize("level", ["Bronze", "Silver", "Gold"])
    def test_valid_levels(self, level):
        """Test all valid levels"""
        result = InputValidator.validate_level(level)
        assert result == level

    @pytest.mark.parametrize("level", ["bronze", "GOLD", "Platinum", ""])
    def test_invalid_levels(self, level):
        """Test invalid levels raise ValueError"""
        with pytest.raises(ValueError, match="Invalid level"):
            InputValidator.validate_level(level)


@pytest.mark.unit
@pytest.mark.phase2
class TestValidatePriority:
    """Test priority validation"""

    @pytest.mark.parametrize("priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    def test_valid_priorities(self, priority):
        """Test all valid priorities"""
        result = InputValidator.validate_priority(priority)
        assert result == priority

    @pytest.mark.parametrize("priority", ["low", "Normal", "URGENT", ""])
    def test_invalid_priorities(self, priority):
        """Test invalid priorities raise ValueError"""
        with pytest.raises(ValueError, match="Invalid priority"):
            InputValidator.validate_priority(priority)


@pytest.mark.unit
@pytest.mark.phase2
class TestValidateDescription:
    """Test description validation"""

    def test_valid_description(self):
        """Test valid description"""
        desc = "This is a valid task description"
        result = InputValidator.validate_description(desc)
        assert result == desc

    def test_description_too_short(self):
        """Test description too short raises error"""
        with pytest.raises(ValueError, match="too short"):
            InputValidator.validate_description("Short")

    def test_description_too_long(self):
        """Test description too long raises error"""
        long_desc = "a" * 1001
        with pytest.raises(ValueError, match="too long"):
            InputValidator.validate_description(long_desc)

    def test_description_custom_length(self):
        """Test custom min/max length"""
        desc = "Short"
        result = InputValidator.validate_description(desc, min_length=3, max_length=10)
        assert result == desc

    def test_description_must_be_string(self):
        """Test non-string description raises error"""
        with pytest.raises(ValueError, match="must be a string"):
            InputValidator.validate_description(123)


@pytest.mark.unit
@pytest.mark.phase2
class TestValidateTaskSpecification:
    """Test complete task specification validation"""

    def test_valid_task_spec(self):
        """Test valid task specification"""
        spec = {
            'task_id': 'TASK_205',
            'description': 'Testing Infrastructure Foundation',
            'level': 'Gold',
            'priority': 'HIGH',
        }
        result = InputValidator.validate_task_specification(spec)
        assert result == spec

    def test_task_spec_with_optional_fields(self):
        """Test task spec with optional fields"""
        spec = {
            'task_id': 'TASK_205',
            'description': 'Testing Infrastructure Foundation',
            'level': 'Gold',
            'priority': 'HIGH',
            'state': 'IN_PROGRESS',
            'started': '2026-01-29 12:00:00.000',
            'completed': '2026-01-29 15:00:00.000',
        }
        result = InputValidator.validate_task_specification(spec)
        assert result == spec

    @pytest.mark.parametrize("missing_field", ['task_id', 'description', 'level', 'priority'])
    def test_task_spec_missing_required_field(self, missing_field):
        """Test missing required fields raise error"""
        spec = {
            'task_id': 'TASK_205',
            'description': 'Testing Infrastructure Foundation',
            'level': 'Gold',
            'priority': 'HIGH',
        }
        del spec[missing_field]

        with pytest.raises(ValueError, match=f"Missing required field: {missing_field}"):
            InputValidator.validate_task_specification(spec)

    def test_task_spec_invalid_task_id(self):
        """Test invalid task ID in spec"""
        spec = {
            'task_id': 'INVALID',
            'description': 'Testing Infrastructure Foundation',
            'level': 'Gold',
            'priority': 'HIGH',
        }
        with pytest.raises(ValueError):
            InputValidator.validate_task_specification(spec)

    def test_task_spec_invalid_state(self):
        """Test invalid state in spec"""
        spec = {
            'task_id': 'TASK_205',
            'description': 'Testing Infrastructure Foundation',
            'level': 'Gold',
            'priority': 'HIGH',
            'state': 'INVALID_STATE',
        }
        with pytest.raises(ValueError):
            InputValidator.validate_task_specification(spec)


@pytest.mark.unit
@pytest.mark.phase2
@pytest.mark.security
class TestSanitizeLogMessage:
    """Test log message sanitization (CRITICAL-8 Fix)"""

    @pytest.mark.parametrize("message,expected_pattern", [
        ("password=secret123", "password=***"),
        ("Password: mypass", "Password: ***"),
        ("api_key=abc123xyz", "api_key=***"),
        ("API-KEY: secret", "API-KEY: ***"),
        ("token=bearer123", "token=***"),
        ("SECRET: confidential", "SECRET: ***"),
    ])
    def test_sanitize_passwords_and_secrets(self, message, expected_pattern):
        """Test password and secret sanitization"""
        result = InputValidator.sanitize_log_message(message)
        assert expected_pattern in result
        assert "secret" not in result.lower() or "secret: ***" in result.lower()

    def test_sanitize_email_addresses(self):
        """Test email address sanitization"""
        message = "User email: user@example.com"
        result = InputValidator.sanitize_log_message(message)
        assert "***@***.***" in result
        assert "user@example.com" not in result

    def test_sanitize_credit_cards(self):
        """Test credit card sanitization"""
        message = "Card: 1234-5678-9012-3456"
        result = InputValidator.sanitize_log_message(message)
        assert "****-****-****-****" in result
        assert "1234-5678-9012-3456" not in result

    def test_sanitize_aws_keys(self):
        """Test AWS access key sanitization"""
        message = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        result = InputValidator.sanitize_log_message(message)
        assert "AKIA****************" in result
        assert "AKIAIOSFODNN7EXAMPLE" not in result

    def test_sanitize_github_tokens(self):
        """Test GitHub token sanitization"""
        # GitHub tokens are exactly 36 chars after ghp_
        message = "GH_Token: ghp_" + "a" * 36
        result = InputValidator.sanitize_log_message(message)
        # Token pattern catches this, so check that original is redacted
        assert "ghp_" + "a" * 36 not in result
        assert "***" in result

    def test_sanitize_openai_keys(self):
        """Test OpenAI API key sanitization"""
        message = "API Key: sk-" + "a" * 48
        result = InputValidator.sanitize_log_message(message)
        assert "sk-***" in result

    def test_sanitize_jwt_tokens(self):
        """Test JWT token sanitization"""
        message = "JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = InputValidator.sanitize_log_message(message)
        assert "eyJ***.eyJ***.***" in result

    def test_sanitize_ssn(self):
        """Test SSN sanitization"""
        message = "SSN: 123-45-6789"
        result = InputValidator.sanitize_log_message(message)
        assert "***-**-****" in result
        assert "123-45-6789" not in result

    def test_sanitize_phone_numbers(self):
        """Test phone number sanitization"""
        message = "Phone: 555-123-4567"
        result = InputValidator.sanitize_log_message(message)
        assert "***-***-****" in result

    def test_sanitize_multiple_patterns(self):
        """Test multiple sensitive patterns in one message"""
        message = "User: user@example.com, Password: secret123"
        result = InputValidator.sanitize_log_message(message)
        assert "***@***.***" in result
        assert "Password: ***" in result or "password: ***" in result.lower()
        assert "secret123" not in result
        assert "user@example.com" not in result

    def test_sanitize_preserves_normal_text(self):
        """Test normal text without sensitive data is preserved"""
        message = "Normal log message without secrets"
        result = InputValidator.sanitize_log_message(message)
        assert result == message


@pytest.mark.unit
@pytest.mark.phase2
class TestValidationError:
    """Test ValidationError exception"""

    def test_validation_error_can_be_raised(self):
        """Test ValidationError can be raised"""
        with pytest.raises(ValidationError):
            raise ValidationError("Test error")

    def test_validation_error_message(self):
        """Test ValidationError message"""
        with pytest.raises(ValidationError, match="Validation failed"):
            raise ValidationError("Validation failed")


# Total: 25 test methods across 10 test classes
