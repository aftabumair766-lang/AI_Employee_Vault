"""
Example unit tests demonstrating testing patterns
TASK_205 - Testing Infrastructure Foundation
"""
import pytest


@pytest.mark.unit
@pytest.mark.phase1
class TestBasicAssertions:
    """Demonstrate basic test assertions"""

    def test_basic_equality(self):
        """Test basic Python equality assertion"""
        assert 1 + 1 == 2

    def test_string_operations(self):
        """Test string operations"""
        text = "AI Employee Vault"
        assert "Employee" in text
        assert text.startswith("AI")
        assert text.endswith("Vault")
        assert len(text) == 17

    def test_list_operations(self):
        """Test list operations"""
        items = [1, 2, 3, 4, 5]
        assert len(items) == 5
        assert 3 in items
        assert items[0] == 1
        assert items[-1] == 5


@pytest.mark.unit
@pytest.mark.phase1
class TestFixtureUsage:
    """Demonstrate fixture usage"""

    def test_with_sample_task(self, sample_task_spec):
        """Test using shared fixture"""
        assert sample_task_spec['task_id'] == 'TASK_999'
        assert sample_task_spec['level'] == 'Gold'
        assert sample_task_spec['priority'] == 'MEDIUM'
        assert sample_task_spec['state'] == 'NEEDS_ACTION'

    def test_with_vault_root(self, vault_root):
        """Test using temporary vault root"""
        assert vault_root.exists()
        assert vault_root.is_dir()
        assert vault_root.name == "AI_Employee_vault"

    def test_with_valid_states(self, valid_states):
        """Test using valid states fixture"""
        assert 'NEEDS_ACTION' in valid_states
        assert 'IN_PROGRESS' in valid_states
        assert 'COMPLETED' in valid_states
        assert 'DONE' in valid_states
        assert len(valid_states) == 8


@pytest.mark.unit
@pytest.mark.phase1
class TestParameterizedTests:
    """Demonstrate parameterized testing"""

    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
        (10, 20),
    ])
    def test_multiplication(self, input, expected):
        """Test with multiple parameter sets"""
        assert input * 2 == expected

    @pytest.mark.parametrize("level", ['Bronze', 'Silver', 'Gold'])
    def test_valid_levels(self, level):
        """Test each valid level"""
        assert level in ['Bronze', 'Silver', 'Gold']

    @pytest.mark.parametrize("state,is_terminal", [
        ('NEEDS_ACTION', False),
        ('PLANNING', False),
        ('IN_PROGRESS', False),
        ('COMPLETED', False),
        ('DONE', True),
        ('FAILED', True),
    ])
    def test_terminal_states(self, state, is_terminal):
        """Test which states are terminal"""
        terminal_states = ['DONE', 'FAILED']
        assert (state in terminal_states) == is_terminal


@pytest.mark.unit
@pytest.mark.phase1
class TestExceptionHandling:
    """Demonstrate exception testing"""

    def test_exception_raised(self):
        """Test that exception is raised"""
        with pytest.raises(ValueError):
            raise ValueError("Test error")

    def test_exception_message(self):
        """Test exception message"""
        with pytest.raises(ValueError, match="Invalid value"):
            raise ValueError("Invalid value provided")

    def test_no_exception(self):
        """Test that no exception is raised"""
        try:
            result = 1 + 1
            assert result == 2
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")


@pytest.mark.unit
@pytest.mark.phase1
class TestTaskIDValidation:
    """Example tests for task ID validation logic"""

    def test_valid_task_id_format(self):
        """Test valid task ID format"""
        task_id = "TASK_205"
        assert task_id.startswith("TASK_")
        assert task_id.split("_")[1].isdigit()
        assert len(task_id.split("_")[1]) == 3

    @pytest.mark.parametrize("task_id,is_valid", [
        ("TASK_001", True),
        ("TASK_100", True),
        ("TASK_205", True),
        ("TASK_300", True),
        ("TASK_999", False),  # Out of range
        ("TASK_1", False),    # Wrong format
        ("task_001", False),  # Lowercase
        ("TASK001", False),   # No underscore
    ])
    def test_task_id_validation(self, task_id, is_valid):
        """Test task ID validation with various inputs"""
        # Simple validation logic (would be replaced with actual validator)
        try:
            parts = task_id.split("_")
            if len(parts) != 2:
                result = False
            elif parts[0] != "TASK":
                result = False
            elif not parts[1].isdigit():
                result = False
            elif len(parts[1]) != 3:
                result = False
            elif not (1 <= int(parts[1]) <= 300):
                result = False
            else:
                result = True
        except:
            result = False

        assert result == is_valid


@pytest.mark.unit
@pytest.mark.phase1
class TestFileOperations:
    """Example tests for file operations"""

    def test_create_temp_file(self, temp_file):
        """Test creating temporary file"""
        file_path = temp_file("test.txt", "Hello World")
        assert file_path.exists()
        assert file_path.read_text() == "Hello World"

    def test_create_temp_directory(self, temp_dir):
        """Test creating temporary directory"""
        dir_path = temp_dir("test_dir")
        assert dir_path.exists()
        assert dir_path.is_dir()


@pytest.mark.unit
@pytest.mark.phase1
class TestTimestamps:
    """Example tests for timestamp handling"""

    def test_iso_timestamp_format(self, iso_timestamp):
        """Test ISO 8601 timestamp format"""
        # Format: YYYY-MM-DD HH:MM:SS.mmm
        import re
        pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$'
        assert re.match(pattern, iso_timestamp)

    def test_timestamp_parsing(self, iso_timestamp):
        """Test timestamp can be parsed back to datetime"""
        from datetime import datetime
        dt = datetime.strptime(iso_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        assert isinstance(dt, datetime)


# Summary of example tests
"""
This module demonstrates:
- Basic assertions (equality, strings, lists)
- Fixture usage (sample_task_spec, vault_root, etc.)
- Parameterized tests (multiple inputs)
- Exception testing (pytest.raises)
- Task ID validation logic
- File operations with temp files/dirs
- Timestamp handling

Total example tests: 20+
All tests should pass (they test working functionality)
"""
