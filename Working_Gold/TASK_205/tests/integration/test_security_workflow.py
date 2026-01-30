"""
Integration tests for security workflows
TASK_205 Phase 3 - Testing Infrastructure Foundation
Tests complete security workflows: logging + sanitization + validation
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'TASK_204' / 'scripts'))

from input_validator import InputValidator
from secure_logging import SecureLogger
from path_validator import PathValidator, safe_file_operation, SecurityError


@pytest.mark.integration
@pytest.mark.phase3
@pytest.mark.security
class TestSecureLoggingWorkflow:
    """Test complete logging workflow with sanitization"""

    def test_task_execution_with_secure_logging(self, temp_dir):
        """Test task execution with automatic log sanitization"""
        work_dir = temp_dir('logging_workflow')
        log_file = work_dir / 'task_execution.log'

        # Create secure logger
        logger = SecureLogger('task_worker', log_file=str(log_file), console=False)

        # Simulate task execution with sensitive data
        logger.info('Starting task TASK_100')
        logger.info('User credentials: password=secret123')  # Should be sanitized
        logger.info('API request with api_key=AKIAIOSFODNN7EXAMPLE')  # Should be sanitized
        logger.info('User email: user@example.com')  # Should be sanitized
        logger.info('Task completed successfully')

        # Read log file
        log_content = log_file.read_text()

        # Verify sensitive data is sanitized
        assert 'secret123' not in log_content
        assert 'AKIAIOSFODNN7EXAMPLE' not in log_content
        assert 'user@example.com' not in log_content

        # Verify redaction markers present
        assert '***' in log_content

        # Verify normal messages preserved
        assert 'TASK_100' in log_content
        assert 'Task completed successfully' in log_content

    def test_multi_level_logging_with_sanitization(self, temp_dir):
        """Test different log levels with sanitization"""
        work_dir = temp_dir('log_levels')
        log_file = work_dir / 'multi_level.log'

        logger = SecureLogger('test', log_file=str(log_file), console=False)

        # Log at different levels with sensitive data
        logger.debug('Debug: password=debug123')
        logger.info('Info: token=info_token_123')
        logger.warning('Warning: secret=warn_secret')
        logger.error('Error: api_key=error_key_123')

        log_content = log_file.read_text()

        # All sensitive data should be redacted
        assert 'debug123' not in log_content
        assert 'info_token_123' not in log_content
        assert 'warn_secret' not in log_content
        assert 'error_key_123' not in log_content

        # Level markers should be present
        assert 'DEBUG' in log_content or 'INFO' in log_content  # DEBUG might be filtered
        assert 'WARNING' in log_content
        assert 'ERROR' in log_content


@pytest.mark.integration
@pytest.mark.phase3
@pytest.mark.security
class TestValidationSecurityWorkflow:
    """Test validation in security-critical workflows"""

    def test_complete_input_validation_workflow(self, temp_dir):
        """Test complete validation workflow for task creation"""
        # Step 1: Validate task ID
        task_id = 'TASK_125'
        validated_id, level = InputValidator.validate_task_id(task_id)
        assert validated_id == 'TASK_125'
        assert level == 'Silver'

        # Step 2: Validate all required fields
        spec = {
            'task_id': task_id,
            'description': 'Complete integration test for validation workflow',
            'level': level,
            'priority': 'HIGH',
            'state': 'NEEDS_ACTION',
            'started': '2026-01-29 13:00:00.000',
        }

        validated_spec = InputValidator.validate_task_specification(spec)

        # Step 3: Validate filename for output
        output_filename = 'task_125_output.json'
        validated_filename = InputValidator.validate_filename(output_filename)
        assert validated_filename == output_filename

        # Step 4: Validate state
        validated_state = InputValidator.validate_state('NEEDS_ACTION')
        assert validated_state == 'NEEDS_ACTION'

    def test_validation_blocks_malicious_input(self, temp_dir):
        """Test that validation blocks various attack vectors"""
        # Directory traversal in filename
        with pytest.raises(ValueError):
            InputValidator.validate_filename('../../../etc/passwd')

        # Invalid task ID format
        with pytest.raises(ValueError):
            InputValidator.validate_task_id('../../SECRET')

        # Reserved Windows filename
        with pytest.raises(ValueError):
            InputValidator.validate_filename('CON')

        # Hidden file (starts with dot)
        with pytest.raises(ValueError):
            InputValidator.validate_filename('.hidden_file')

    def test_log_sanitization_workflow(self, temp_dir):
        """Test log sanitization in workflow"""
        # Create message with multiple sensitive patterns
        message = "User login: user@example.com, password=secret123, API Key: AKIAIOSFODNN7EXAMPLE, SSN: 123-45-6789"

        # Sanitize
        sanitized = InputValidator.sanitize_log_message(message)

        # Verify all patterns redacted
        assert 'user@example.com' not in sanitized
        assert 'secret123' not in sanitized
        assert 'AKIAIOSFODNN7EXAMPLE' not in sanitized
        assert '123-45-6789' not in sanitized

        # Verify redaction markers
        assert '***@***.***' in sanitized  # Email
        assert '***' in sanitized  # Generic secrets
        assert 'AKIA****************' in sanitized  # AWS key


@pytest.mark.integration
@pytest.mark.phase3
@pytest.mark.security
class TestPathSecurityIntegration:
    """Test path security in integrated workflows"""

    def test_safe_file_workflow_with_validation(self, vault_root):
        """Test complete safe file workflow"""
        validator = PathValidator(vault_root=str(vault_root))

        # Step 1: Validate base directory
        working_bronze = vault_root / 'Working_Bronze'
        working_bronze.mkdir(parents=True, exist_ok=True)

        # Step 2: Create task directory safely
        task_dir = validator.safe_join('Working_Bronze', 'TASK_030')
        task_dir.mkdir(parents=True, exist_ok=True)

        # Step 3: Validate filename
        filename = 'output_data.json'
        validated_filename = InputValidator.validate_filename(filename)

        # Step 4: Create file with safe operations
        safe_path = validator.safe_join('Working_Bronze', 'TASK_030', validated_filename)
        safe_path.write_text('{"status": "success"}')

        # Verify file in safe location
        assert safe_path.exists()
        assert validator.is_safe_path(str(safe_path)) is True

    def test_multiple_security_layers(self, vault_root):
        """Test multiple security layers working together"""
        validator = PathValidator(vault_root=str(vault_root))

        # Layer 1: Path validation
        base_dir = 'Working_Gold'
        task_subdir = 'TASK_275'
        filename = 'secure_output.txt'

        # Layer 2: Filename validation
        validated_filename = InputValidator.validate_filename(filename)

        # Layer 3: Safe path construction
        safe_path = validator.safe_join(base_dir, task_subdir, validated_filename)
        safe_path.parent.mkdir(parents=True, exist_ok=True)

        # Layer 4: Safe file operation
        safe_path.write_text('Secured data')

        # Layer 5: Verify safety
        assert validator.is_safe_path(str(safe_path)) is True
        assert not validator.check_directory_traversal(str(safe_path))

    def test_security_error_handling_workflow(self, vault_root):
        """Test security error handling in workflow"""
        validator = PathValidator(vault_root=str(vault_root))

        # Create safe working directory
        working_dir = vault_root / 'Working_Gold'
        working_dir.mkdir(parents=True, exist_ok=True)

        safe_file = working_dir / 'test.txt'
        safe_file.write_text('test')

        # Try unsafe path
        unsafe_path = vault_root.parent / 'unsafe.txt'

        # Should raise SecurityError
        with pytest.raises(SecurityError, match="Unsafe path"):
            safe_file_operation(str(unsafe_path), operation='read', validator=validator)


@pytest.mark.integration
@pytest.mark.phase3
class TestEndToEndTaskWithSecurity:
    """Test complete end-to-end task with all security features"""

    def test_complete_secure_task_execution(self, vault_root, temp_dir):
        """Test complete task with all security features enabled"""
        work_dir = temp_dir('e2e_secure_task')
        log_file = work_dir / 'execution.log'

        # Step 1: Initialize security components
        logger = SecureLogger('secure_task', log_file=str(log_file), console=False)
        validator = PathValidator(vault_root=str(vault_root))

        # Step 2: Validate and create task
        task_spec = {
            'task_id': 'TASK_150',
            'description': 'End-to-end secure task execution test workflow',
            'level': 'Silver',
            'priority': 'HIGH',
            'state': 'IN_PROGRESS',
        }

        validated_spec = InputValidator.validate_task_specification(task_spec)
        logger.info(f"Task validated: {validated_spec['task_id']}")

        # Step 3: Create safe working directory
        task_dir = validator.get_safe_task_dir('TASK_150', 'Silver', 'Working')
        task_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Working directory created: {task_dir.name}")

        # Step 4: Process with sensitive data (will be sanitized in logs)
        logger.info('Processing user data: email=user@example.com, password=secret123')

        # Step 5: Validate and create output
        output_filename = 'task_150_results.json'
        validated_filename = InputValidator.validate_filename(output_filename)

        output_path = validator.safe_join('Working_Silver', 'TASK_150', validated_filename)
        output_path.write_text('{"status": "completed", "result": "success"}')
        logger.info(f'Output created: {validated_filename}')

        # Step 6: Verify security measures
        log_content = log_file.read_text()

        # Logs should be sanitized
        assert 'user@example.com' not in log_content
        assert 'secret123' not in log_content

        # Path should be safe
        assert validator.is_safe_path(str(output_path)) is True

        # File should exist
        assert output_path.exists()

        logger.info('Task completed successfully')


# Total: 11 integration test methods
