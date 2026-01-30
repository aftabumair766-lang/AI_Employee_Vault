"""
Custom assertion helpers for tests
TASK_205 - Testing Infrastructure Foundation
"""
from pathlib import Path
from datetime import datetime


def assert_task_valid(task):
    """
    Assert task has valid structure

    Args:
        task: Task dictionary to validate

    Raises:
        AssertionError: If task structure is invalid
    """
    required_fields = ['task_id', 'description', 'level', 'priority', 'state']
    for field in required_fields:
        assert field in task, f"Task missing required field: {field}"

    # Validate task_id format
    assert task['task_id'].startswith('TASK_'), "Task ID must start with 'TASK_'"

    # Validate level
    assert task['level'] in ['Bronze', 'Silver', 'Gold'], f"Invalid level: {task['level']}"

    # Validate priority
    assert task['priority'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], \
        f"Invalid priority: {task['priority']}"

    # Validate state
    valid_states = ['NEEDS_ACTION', 'PLANNING', 'AWAITING_APPROVAL',
                   'IN_PROGRESS', 'COMPLETED', 'DONE', 'FAILED', 'BLOCKED']
    assert task['state'] in valid_states, f"Invalid state: {task['state']}"


def assert_file_exists(file_path):
    """
    Assert file exists

    Args:
        file_path: Path to file (str or Path)

    Raises:
        AssertionError: If file doesn't exist
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    assert path.exists(), f"File not found: {file_path}"
    assert path.is_file(), f"Path exists but is not a file: {file_path}"


def assert_dir_exists(dir_path):
    """
    Assert directory exists

    Args:
        dir_path: Path to directory (str or Path)

    Raises:
        AssertionError: If directory doesn't exist
    """
    path = Path(dir_path) if isinstance(dir_path, str) else dir_path
    assert path.exists(), f"Directory not found: {dir_path}"
    assert path.is_dir(), f"Path exists but is not a directory: {dir_path}"


def assert_file_contains(file_path, content):
    """
    Assert file contains specific content

    Args:
        file_path: Path to file
        content: Content to search for

    Raises:
        AssertionError: If content not found in file
    """
    assert_file_exists(file_path)
    path = Path(file_path) if isinstance(file_path, str) else file_path
    file_content = path.read_text()
    assert content in file_content, \
        f"Content '{content}' not found in file {file_path}"


def assert_timestamps_ordered(timestamp1, timestamp2):
    """
    Assert timestamp1 occurs before timestamp2

    Args:
        timestamp1: First timestamp (ISO 8601 format)
        timestamp2: Second timestamp (ISO 8601 format)

    Raises:
        AssertionError: If timestamp1 >= timestamp2
    """
    # Parse ISO 8601 timestamps
    dt1 = datetime.fromisoformat(timestamp1.replace(' ', 'T').replace('.', '.', 1))
    dt2 = datetime.fromisoformat(timestamp2.replace(' ', 'T').replace('.', '.', 1))

    assert dt1 < dt2, \
        f"Timestamp order incorrect: {timestamp1} should be before {timestamp2}"


def assert_state_transition_valid(from_state, to_state, level='Gold'):
    """
    Assert state transition is valid

    Args:
        from_state: Current state
        to_state: Target state
        level: Task level (Bronze, Silver, Gold)

    Raises:
        AssertionError: If transition is invalid
    """
    # Valid transitions (simplified - full logic would be more complex)
    valid_transitions = {
        'NEEDS_ACTION': ['PLANNING', 'IN_PROGRESS'],  # Bronze can skip PLANNING
        'PLANNING': ['AWAITING_APPROVAL'],
        'AWAITING_APPROVAL': ['IN_PROGRESS'],
        'IN_PROGRESS': ['COMPLETED', 'FAILED', 'BLOCKED'],
        'COMPLETED': ['DONE'],
        'BLOCKED': ['IN_PROGRESS'],
    }

    assert from_state in valid_transitions, f"Unknown from_state: {from_state}"
    assert to_state in valid_transitions.get(from_state, []), \
        f"Invalid transition: {from_state} -> {to_state}"


def assert_list_contains_all(list1, items):
    """
    Assert list contains all specified items

    Args:
        list1: List to check
        items: Items that should be in list

    Raises:
        AssertionError: If any item is missing
    """
    missing = [item for item in items if item not in list1]
    assert not missing, f"List missing items: {missing}"


def assert_dict_subset(dict1, subset):
    """
    Assert dict1 contains all key-value pairs from subset

    Args:
        dict1: Dictionary to check
        subset: Subset of expected key-value pairs

    Raises:
        AssertionError: If any key-value pair doesn't match
    """
    for key, value in subset.items():
        assert key in dict1, f"Dictionary missing key: {key}"
        assert dict1[key] == value, \
            f"Value mismatch for key '{key}': expected {value}, got {dict1[key]}"


def assert_no_errors_in_log(log_file):
    """
    Assert log file contains no ERROR entries

    Args:
        log_file: Path to log file

    Raises:
        AssertionError: If ERROR entries found
    """
    assert_file_exists(log_file)
    path = Path(log_file) if isinstance(log_file, str) else log_file
    content = path.read_text()

    error_lines = [line for line in content.split('\n') if '[ERROR]' in line]
    assert not error_lines, \
        f"Log contains {len(error_lines)} ERROR entries:\n" + '\n'.join(error_lines[:5])
