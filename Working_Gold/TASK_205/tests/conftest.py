"""
Pytest configuration and shared fixtures
TASK_205 - Testing Infrastructure Foundation
"""
import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def vault_root(tmp_path):
    """
    Provide temporary vault root directory for tests

    Creates a clean temporary directory that mimics the
    AI Employee Vault structure for isolated testing.

    Yields:
        Path: Temporary vault root directory
    """
    vault_dir = tmp_path / "AI_Employee_vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    yield vault_dir
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def sample_task_spec():
    """
    Provide sample task specification for testing

    Returns:
        dict: Valid task specification
    """
    return {
        'task_id': 'TASK_999',
        'description': 'Test task for unit tests',
        'level': 'Gold',
        'priority': 'MEDIUM',
        'state': 'NEEDS_ACTION'
    }


@pytest.fixture
def bronze_task_spec():
    """Bronze-level task specification"""
    return {
        'task_id': 'TASK_050',
        'description': 'Bronze test task',
        'level': 'Bronze',
        'priority': 'LOW',
        'state': 'NEEDS_ACTION'
    }


@pytest.fixture
def silver_task_spec():
    """Silver-level task specification"""
    return {
        'task_id': 'TASK_150',
        'description': 'Silver test task',
        'level': 'Silver',
        'priority': 'MEDIUM',
        'state': 'NEEDS_ACTION'
    }


@pytest.fixture
def gold_task_spec():
    """Gold-level task specification"""
    return {
        'task_id': 'TASK_250',
        'description': 'Gold test task',
        'level': 'Gold',
        'priority': 'HIGH',
        'state': 'NEEDS_ACTION'
    }


@pytest.fixture
def valid_states():
    """List of valid task states"""
    return [
        'NEEDS_ACTION',
        'PLANNING',
        'AWAITING_APPROVAL',
        'IN_PROGRESS',
        'COMPLETED',
        'DONE',
        'FAILED',
        'BLOCKED'
    ]


@pytest.fixture
def valid_levels():
    """List of valid levels"""
    return ['Bronze', 'Silver', 'Gold']


@pytest.fixture
def valid_priorities():
    """List of valid priorities"""
    return ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']


@pytest.fixture
def iso_timestamp():
    """
    Generate ISO 8601 timestamp with milliseconds

    Returns:
        str: Timestamp in format YYYY-MM-DD HH:MM:SS.mmm
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


@pytest.fixture
def temp_file(tmp_path):
    """
    Create temporary file for testing

    Usage:
        def test_something(temp_file):
            file_path = temp_file("test.txt", "content")
            assert file_path.exists()

    Returns:
        callable: Function to create temp files
    """
    def _create_file(filename, content=""):
        file_path = tmp_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path

    return _create_file


@pytest.fixture
def temp_dir(tmp_path):
    """
    Create temporary directory for testing

    Returns:
        callable: Function to create temp directories
    """
    def _create_dir(dirname):
        dir_path = tmp_path / dirname
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    return _create_dir


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Reset environment before each test

    This fixture runs automatically before every test
    to ensure a clean testing environment.
    """
    # Setup: runs before test
    yield
    # Teardown: runs after test
    pass


# Pytest hooks for custom behavior

def pytest_configure(config):
    """
    Configure pytest with custom settings
    """
    config.addinivalue_line(
        "markers",
        "phase1: Phase 1 foundation tests"
    )
    config.addinivalue_line(
        "markers",
        "phase2: Phase 2 unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection

    Can be used to skip tests, add markers, etc.
    """
    pass
