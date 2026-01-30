# Testing Guide
## AI Employee Vault - Testing Infrastructure

**TASK_205 - Testing Infrastructure Foundation**
**Created**: 2026-01-29
**Status**: Phase 1 Complete

---

## Overview

This guide explains how to write, run, and maintain tests for the AI Employee Vault project. Our testing infrastructure uses pytest with comprehensive coverage reporting and multiple test types.

**Current Test Statistics** (Phase 1):
- Example tests: 35 passing
- Test execution time: <1 second
- Infrastructure: Fully operational

**Target** (Phase 2-5):
- Total tests: 200+
- Coverage: 80%+
- Execution time: <5 minutes

---

## Quick Start

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest Working_Gold/TASK_205/tests/unit/test_example.py

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run tests with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel (faster)
pytest -n auto
```

### Test Organization

```
tests/
├── unit/              # Unit tests (individual functions)
├── integration/       # Integration tests (workflows)
├── e2e/              # End-to-end tests (complete scenarios)
├── fixtures/         # Shared test fixtures
├── helpers/          # Test utilities
│   ├── assertions.py  # Custom assertions
│   └── factories.py   # Test data factories
└── conftest.py       # Pytest configuration
```

---

## Writing Tests

### Basic Test Structure

```python
import pytest

@pytest.mark.unit  # Mark test type
@pytest.mark.phase2  # Mark phase
class TestTaskManagement:
    """Test task management functions"""

    def test_create_task_with_valid_spec(self, sample_task_spec):
        """Test task creation with valid specification"""
        # Arrange
        spec = sample_task_spec

        # Act
        task = create_task(spec)

        # Assert
        assert task['task_id'] == 'TASK_999'
        assert task['state'] == 'NEEDS_ACTION'
```

### Testing Patterns

#### 1. **Arrange-Act-Assert (AAA) Pattern**

```python
def test_state_transition():
    # Arrange - Set up test data
    task = create_test_task('TASK_001', state='NEEDS_ACTION')

    # Act - Execute the function being tested
    result = transition_task_state(task, 'PLANNING')

    # Assert - Verify expected outcome
    assert result['state'] == 'PLANNING'
```

#### 2. **Parameterized Tests**

```python
@pytest.mark.parametrize("task_id,is_valid", [
    ("TASK_001", True),
    ("TASK_999", False),  # Out of range
    ("task_001", False),  # Lowercase
])
def test_task_id_validation(task_id, is_valid):
    """Test task ID validation with multiple inputs"""
    result = validate_task_id(task_id)
    assert result == is_valid
```

#### 3. **Exception Testing**

```python
def test_invalid_state_transition():
    """Test that invalid transition raises error"""
    with pytest.raises(ValueError, match="Invalid transition"):
        transition_task_state('DONE', 'IN_PROGRESS')
```

#### 4. **Fixture Usage**

```python
def test_with_vault_root(vault_root):
    """Test using temporary vault directory"""
    # vault_root is automatically created and cleaned up
    assert vault_root.exists()

    # Create test files
    test_file = vault_root / "test.txt"
    test_file.write_text("content")

    assert test_file.exists()
    # Cleanup happens automatically
```

---

## Available Fixtures

### Standard Fixtures (conftest.py)

**vault_root**: Temporary vault directory
```python
def test_example(vault_root):
    assert vault_root.exists()
```

**sample_task_spec**: Sample task specification
```python
def test_example(sample_task_spec):
    assert sample_task_spec['task_id'] == 'TASK_999'
```

**bronze_task_spec, silver_task_spec, gold_task_spec**: Level-specific tasks
```python
def test_example(gold_task_spec):
    assert gold_task_spec['level'] == 'Gold'
```

**valid_states, valid_levels, valid_priorities**: Valid values
```python
def test_example(valid_states):
    assert 'IN_PROGRESS' in valid_states
```

**iso_timestamp**: ISO 8601 timestamp
```python
def test_example(iso_timestamp):
    assert re.match(r'\d{4}-\d{2}-\d{2}', iso_timestamp)
```

**temp_file, temp_dir**: Create temporary files/directories
```python
def test_example(temp_file):
    file_path = temp_file("test.txt", "content")
    assert file_path.exists()
```

---

## Custom Assertions

Use custom assertions from `helpers/assertions.py` for clearer tests:

```python
from helpers.assertions import (
    assert_task_valid,
    assert_file_exists,
    assert_timestamps_ordered,
    assert_state_transition_valid
)

def test_example():
    task = create_task(spec)

    # Instead of manual assertions
    assert_task_valid(task)
    assert_file_exists('path/to/file.txt')
    assert_timestamps_ordered(ts1, ts2)
```

**Available assertions**:
- `assert_task_valid(task)` - Validate task structure
- `assert_file_exists(path)` - Check file exists
- `assert_dir_exists(path)` - Check directory exists
- `assert_file_contains(path, content)` - Check file content
- `assert_timestamps_ordered(ts1, ts2)` - Check timestamp order
- `assert_state_transition_valid(from, to)` - Check valid transition
- `assert_list_contains_all(list, items)` - Check list contains items
- `assert_dict_subset(dict, subset)` - Check dict contains subset
- `assert_no_errors_in_log(logfile)` - Check no errors in log

---

## Test Data Factories

Use factory functions from `helpers/factories.py` to create test data:

```python
from helpers.factories import (
    create_test_task,
    create_test_file,
    create_sample_vault_structure
)

def test_example(vault_root):
    # Create test task
    task = create_test_task(
        task_id='TASK_001',
        level='Gold',
        priority='HIGH'
    )

    # Create test file
    file_path = create_test_file(vault_root, 'test.txt', 'content')

    # Create full vault structure
    vault = create_sample_vault_structure(vault_root, level='Gold')
    assert vault['tasks_file'].exists()
```

**Available factories**:
- `create_test_task(**kwargs)` - Create task spec
- `create_test_file(dir, filename, content)` - Create file
- `create_test_directory(base, dirname)` - Create directory
- `create_task_directory_structure(vault, task_id)` - Create task dirs
- `generate_iso_timestamp()` - Generate timestamp
- `create_execution_log_entry(...)` - Create log entry
- `create_tasks_md_content(tasks)` - Create TASKS.md content
- `create_status_md_content(state, activity)` - Create STATUS.md content
- `create_sample_vault_structure(vault, level)` - Create full structure

---

## Test Markers

Mark tests to categorize and run selectively:

```python
@pytest.mark.unit       # Unit test
@pytest.mark.integration  # Integration test
@pytest.mark.e2e        # End-to-end test
@pytest.mark.slow       # Slow test (>1 second)
@pytest.mark.security   # Security-related test
@pytest.mark.phase2     # Phase 2 test
```

**Run tests by marker**:
```bash
pytest -m unit           # Only unit tests
pytest -m "not slow"     # Skip slow tests
pytest -m "unit and phase2"  # Unit tests from phase 2
```

---

## Coverage Reporting

### Generate Coverage Reports

```bash
# Terminal report
pytest --cov=. --cov-report=term-missing

# HTML report (open htmlcov/index.html)
pytest --cov=. --cov-report=html

# XML report (for CI/CD)
pytest --cov=. --cov-report=xml

# Fail if coverage below 80%
pytest --cov=. --cov-fail-under=80
```

### Understanding Coverage

**Line coverage**: Percentage of code lines executed
**Branch coverage**: Percentage of code branches (if/else) tested
**Function coverage**: Percentage of functions called

**Target**: ≥80% line coverage

### Excluding Code from Coverage

```python
def debug_function():  # pragma: no cover
    """This function won't be counted in coverage"""
    print("Debug info")
```

---

## Best Practices

### DO

✅ **Write tests first (TDD)** - Write test before implementation
✅ **Test one thing per test** - Clear, focused tests
✅ **Use descriptive names** - `test_create_task_with_invalid_id_raises_error`
✅ **Use fixtures** - Reuse common test data
✅ **Test edge cases** - Empty strings, None, boundary values
✅ **Test error conditions** - What happens when things go wrong?
✅ **Keep tests isolated** - Tests should not depend on each other
✅ **Use parameterized tests** - Test multiple inputs efficiently
✅ **Clean up after tests** - Use fixtures with teardown

### DON'T

❌ **Don't test external libraries** - Trust pytest, pathlib, etc.
❌ **Don't test implementation details** - Test behavior, not internals
❌ **Don't share state between tests** - Each test should be independent
❌ **Don't use sleep()** - Use mocking or proper synchronization
❌ **Don't ignore failing tests** - Fix or remove them
❌ **Don't write flaky tests** - Tests should be deterministic
❌ **Don't skip tests without reason** - Document why tests are skipped

---

## Common Testing Scenarios

### Testing File Operations

```python
def test_create_task_file(vault_root):
    """Test creating task file"""
    tasks_file = vault_root / 'TASKS_Gold.md'

    # Create file
    create_tasks_file(vault_root, 'Gold')

    # Verify
    assert_file_exists(tasks_file)
    assert_file_contains(tasks_file, 'TASK TRACKING LEDGER')
```

### Testing State Transitions

```python
def test_valid_state_transition():
    """Test valid state transition"""
    task = create_test_task(state='NEEDS_ACTION')

    result = transition_task_state(task, 'PLANNING')

    assert result['state'] == 'PLANNING'
    assert_state_transition_valid('NEEDS_ACTION', 'PLANNING')
```

### Testing with Mocks

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mocks"""
    mock_file = Mock()
    mock_file.read_text.return_value = "content"

    result = process_file(mock_file)

    assert result == "CONTENT"  # Uppercased
    mock_file.read_text.assert_called_once()
```

### Testing Timestamps

```python
def test_timestamp_ordering():
    """Test timestamp ordering"""
    ts1 = generate_iso_timestamp()
    time.sleep(0.01)  # Small delay
    ts2 = generate_iso_timestamp()

    assert_timestamps_ordered(ts1, ts2)
```

---

## Debugging Tests

### Run Single Test

```bash
pytest Working_Gold/TASK_205/tests/unit/test_example.py::TestBasicAssertions::test_basic_equality -v
```

### Print Debug Output

```python
def test_with_debug():
    """Test with debug output"""
    task = create_test_task()
    print(f"Task: {task}")  # Will show if test fails or with -s flag

    assert task['task_id'] == 'TASK_999'
```

**Run with output**:
```bash
pytest -s  # Show print statements
pytest -v  # Verbose output
pytest --tb=short  # Short traceback
pytest --pdb  # Drop into debugger on failure
```

### Last Failed Tests

```bash
pytest --lf   # Run only last failed tests
pytest --ff   # Run failed tests first, then others
```

---

## Performance

### Fast Tests

- Use fixtures to avoid repeated setup
- Mock slow operations (network, disk I/O)
- Use temp_path for file operations (memory-based when possible)
- Run tests in parallel: `pytest -n auto`

### Slow Tests

Mark slow tests:
```python
@pytest.mark.slow
def test_large_dataset():
    """This test takes >1 second"""
    # ...
```

Skip slow tests during development:
```bash
pytest -m "not slow"
```

---

## CI/CD Integration

### GitHub Actions (Phase 5)

Tests will run automatically on every commit:
- All tests must pass before merge
- Coverage must be ≥80%
- Test results visible in PR

### Pre-Commit Hook (Optional)

Run tests before each commit:
```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/unit -q
```

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**: Ensure pytest runs from project root and paths are correct in conftest.py

### Coverage Not Working

**Problem**: "No data to report"

**Solution**: Ensure you're testing actual code, not just test utilities

### Slow Tests

**Problem**: Tests take >5 minutes

**Solution**: Run tests in parallel (`pytest -n auto`) or mark/skip slow tests

### Flaky Tests

**Problem**: Tests pass sometimes, fail other times

**Solution**: Ensure tests are isolated, no timing dependencies, proper cleanup

---

## Test Coverage Goals

| Phase | Tests | Coverage | Target |
|-------|-------|----------|--------|
| Phase 1 | 35 | N/A | Foundation |
| Phase 2 | 150+ | 80%+ | Unit tests |
| Phase 3 | +35-47 | 80%+ | Integration |
| Phase 4 | +17-20 | 80%+ | E2E |
| Phase 5 | 200+ | 80%+ | CI/CD |

**Current**: Phase 1 complete (35 tests, foundation operational)

---

## Getting Help

**Documentation**:
- pytest docs: https://docs.pytest.org/
- pytest-cov docs: https://pytest-cov.readthedocs.io/
- This guide: `Working_Gold/TASK_205/tests/TESTING_GUIDE.md`

**Examples**:
- See `tests/unit/test_example.py` for comprehensive examples
- See `tests/helpers/` for utilities and factories
- See `conftest.py` for available fixtures

**Questions**:
- Review test examples first
- Check pytest documentation
- Ask in code reviews

---

## Next Steps

**Phase 2** (Weeks 3-6): Unit Tests
- Implement 150+ unit tests
- Achieve 80%+ coverage
- Test all core functions

**Phase 3** (Weeks 7-8): Integration Tests
- Test complete workflows
- Multi-task dependencies
- Error recovery

**Phase 4** (Weeks 9-10): E2E Tests
- Full system scenarios
- Performance benchmarks
- Load testing

**Phase 5** (Weeks 11-12): CI/CD
- GitHub Actions
- Automated testing
- Coverage reporting

---

**Guide Version**: 1.0
**Created**: 2026-01-29
**Status**: Complete (Phase 1)
**Next Update**: After Phase 2
