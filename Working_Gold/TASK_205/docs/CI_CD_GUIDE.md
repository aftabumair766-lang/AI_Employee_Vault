# CI/CD Guide
## Automated Testing Infrastructure for AI Employee Vault

**Version**: 1.0
**Last Updated**: 2026-01-30
**TASK**: TASK_205 Phase 5

---

## Table of Contents

1. [Overview](#overview)
2. [GitHub Actions Workflows](#github-actions-workflows)
3. [Running Tests Locally](#running-tests-locally)
4. [Understanding Test Results](#understanding-test-results)
5. [Quality Gates](#quality-gates)
6. [Coverage Reporting](#coverage-reporting)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

The AI Employee Vault project uses GitHub Actions for continuous integration and testing. Every push and pull request automatically runs a comprehensive test suite to ensure code quality and prevent regressions.

### CI/CD Components

| Component | Purpose | Trigger |
|-----------|---------|---------|
| **tests.yml** | Unit & integration tests | Push/PR to main/develop |
| **e2e-tests.yml** | End-to-end tests | Push/PR to main, Daily at 2AM UTC |
| **quality-gates.yml** | Quality enforcement | Pull requests only |
| **codecov.yml** | Coverage tracking | Automatic on test runs |

### Test Coverage Goals

- **Minimum coverage**: 80%
- **Current coverage**: ~50% (360 tests across all phases)
- **E2E coverage**: 98%

---

## GitHub Actions Workflows

### 1. Main Test Workflow (`tests.yml`)

**Purpose**: Runs unit and integration tests on every push/PR

**Matrix**: Tests on Python 3.10, 3.11, 3.12

**Steps**:
1. Checkout code
2. Set up Python environment
3. Cache pip dependencies
4. Install test dependencies
5. Run unit tests with coverage
6. Run integration tests with coverage
7. Upload coverage to Codecov
8. Generate HTML coverage report
9. Verify 80% coverage threshold

**Triggers**:
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

**Badge**:
```markdown
![Tests](https://github.com/YOUR_USERNAME/AI_Employee_vault/workflows/Tests/badge.svg)
```

---

### 2. E2E Test Workflow (`e2e-tests.yml`)

**Purpose**: Runs comprehensive end-to-end tests

**Runs on**: Python 3.12 only (latest)

**Steps**:
1. Checkout code
2. Set up Python 3.12
3. Install dependencies
4. Run all 27 E2E tests
5. Generate coverage report
6. Upload coverage to Codecov
7. Generate HTML test report
8. Run performance benchmarks
9. Upload all artifacts

**Triggers**:
```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

**Artifacts Generated**:
- E2E coverage report (30 days retention)
- E2E test HTML report (30 days retention)
- Performance benchmark results (90 days retention)

**Badge**:
```markdown
![E2E Tests](https://github.com/YOUR_USERNAME/AI_Employee_vault/workflows/E2E%20Tests/badge.svg)
```

---

### 3. Quality Gates Workflow (`quality-gates.yml`)

**Purpose**: Enforces code quality standards on pull requests

**Quality Checks**:
1. ✅ Coverage must be ≥80%
2. ✅ All tests must pass
3. ✅ Code complexity check (Radon)
4. ✅ Security scan (Bandit)
5. ✅ Dependency vulnerability check (Safety)
6. ✅ All security-marked tests must pass

**Steps**:
1. Check coverage threshold (--cov-fail-under=80)
2. Ensure no failing tests (--maxfail=1)
3. Analyze code complexity with Radon
4. Run security scan with Bandit
5. Check dependencies with Safety
6. Verify all security tests pass

**Triggers**:
```yaml
on:
  pull_request:
    branches: [ main, develop ]
```

**Artifacts Generated**:
- Bandit security report (30 days)
- Safety vulnerability report (30 days)

---

## Running Tests Locally

### Prerequisites

```bash
cd Working_Gold/TASK_205
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# From AI_Employee_vault root directory
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# E2E tests only
pytest tests/e2e -v

# Security tests only
pytest -m security -v

# Fast tests only (exclude slow)
pytest -m "not slow" -v
```

### Run Tests with Coverage

```bash
# Generate terminal coverage report
pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Then open htmlcov/index.html in browser

# Generate XML coverage for tools
pytest --cov=. --cov-report=xml
```

### Run Tests in Parallel

```bash
# Automatically use all CPU cores
pytest -n auto

# Use specific number of workers
pytest -n 4
```

### Run Specific Tests

```bash
# By file
pytest tests/unit/test_path_validator.py

# By test name
pytest tests/unit/test_path_validator.py::TestIsSafePath::test_safe_path_in_allowed_directory

# By marker
pytest -m phase4

# By keyword
pytest -k "encryption"
```

### Performance Testing

```bash
# Show slowest 10 tests
pytest --durations=10

# Run only performance benchmarks
pytest tests/e2e/test_performance_baselines.py -v -s
```

---

## Understanding Test Results

### Test Output Format

```
tests/unit/test_path_validator.py::TestIsSafePath::test_safe_path PASSED [ 10%]
│                                   │           │                  │        └─ Progress
│                                   │           │                  └─ Status (PASSED/FAILED)
│                                   │           └─ Test method name
│                                   └─ Test class name
└─ Test file path
```

### Test Markers

Tests are organized with markers for easy filtering:

| Marker | Description | Example |
|--------|-------------|---------|
| `@pytest.mark.unit` | Unit tests | `pytest -m unit` |
| `@pytest.mark.integration` | Integration tests | `pytest -m integration` |
| `@pytest.mark.e2e` | End-to-end tests | `pytest -m e2e` |
| `@pytest.mark.slow` | Slow tests (>1s) | `pytest -m slow` |
| `@pytest.mark.security` | Security tests | `pytest -m security` |
| `@pytest.mark.phase4` | Phase 4 tests | `pytest -m phase4` |

### Coverage Report Interpretation

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
path_validator.py               153     66    56%   45-67, 89-102
encryption_utils.py             224     60    73%   105-125
-----------------------------------------------------------
TOTAL                          1070    549    49%
```

- **Stmts**: Total statements in file
- **Miss**: Uncovered statements
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

---

## Quality Gates

### Coverage Threshold

**Requirement**: Minimum 80% code coverage

**Check**:
```bash
pytest --cov=. --cov-fail-under=80
```

**If Failed**:
1. Identify uncovered code: `pytest --cov=. --cov-report=term-missing`
2. Write tests for uncovered lines
3. Re-run until ≥80%

### Test Passing Requirement

**Requirement**: Zero failing tests

**Check**:
```bash
pytest --maxfail=1
```

**If Failed**:
1. Read error message carefully
2. Fix the failing test or code
3. Re-run tests
4. Do NOT commit if tests fail

### Code Complexity

**Tool**: Radon

**Check**:
```bash
cd Working_Gold/TASK_204/scripts
radon cc . -a -s --min C
```

**Interpretation**:
- **A**: Simple (1-5) - Good
- **B**: Moderate (6-10) - OK
- **C**: Complex (11-20) - Refactor if possible
- **D**: Very complex (21-50) - Refactor
- **F**: Extremely complex (51+) - Must refactor

### Security Scanning

**Tool**: Bandit

**Check**:
```bash
cd Working_Gold/TASK_204/scripts
bandit -r . -f json
```

**Common Issues**:
- Use of `eval()` or `exec()`
- Hardcoded passwords
- SQL injection vulnerabilities
- Use of `pickle` (arbitrary code execution)
- Weak cryptography

### Dependency Vulnerabilities

**Tool**: Safety

**Check**:
```bash
safety check
```

**Action**: Update vulnerable packages immediately

---

## Coverage Reporting

### Codecov Integration

**Setup**:
1. Sign up at https://codecov.io
2. Add repository
3. Get CODECOV_TOKEN
4. Add token to GitHub Secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Create new secret: `CODECOV_TOKEN`
   - Paste token value

**Configuration**: `codecov.yml` in repository root

**Key Settings**:
```yaml
coverage:
  status:
    project:
      default:
        target: 80%  # Minimum coverage
        threshold: 1%  # Allow 1% drop
```

**Flags**:
- `unittests`: Unit test coverage
- `integration`: Integration test coverage
- `e2e`: E2E test coverage

### Coverage Badges

Add to README.md:

```markdown
[![codecov](https://codecov.io/gh/USERNAME/AI_Employee_vault/branch/main/graph/badge.svg)](https://codecov.io/gh/USERNAME/AI_Employee_vault)
```

### Viewing Coverage Reports

**Locally**:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

**On Codecov**:
1. Go to https://codecov.io/gh/USERNAME/AI_Employee_vault
2. View coverage graph, trends, file-by-file coverage
3. See pull request coverage changes

**On GitHub**:
- Coverage comments automatically added to PRs
- View artifacts: Actions → Workflow run → Artifacts section

---

## Troubleshooting

### Problem: Tests Pass Locally But Fail on CI

**Possible Causes**:
1. Environment differences (OS, Python version)
2. Missing dependencies in requirements-test.txt
3. Hardcoded paths (use temp_dir fixture)
4. Timing issues (use timeouts, not sleeps)

**Solution**:
```bash
# Test on same Python version as CI
pyenv install 3.12
pyenv shell 3.12
pytest

# Check for missing dependencies
pip freeze > current_deps.txt
diff current_deps.txt requirements-test.txt
```

### Problem: Coverage Below 80%

**Diagnosis**:
```bash
# Find uncovered files
pytest --cov=. --cov-report=term-missing | grep -E "^\S+\.py.*[0-7][0-9]%"

# Generate detailed HTML report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html and click on red files
```

**Solution**:
1. Focus on high-value uncovered code (core logic)
2. Skip trivial code (CLI entry points, `if __name__ == '__main__'`)
3. Add `# pragma: no cover` for truly untestable code
4. Write tests for remaining uncovered lines

### Problem: Tests Are Too Slow

**Diagnosis**:
```bash
# Find slow tests
pytest --durations=20
```

**Solutions**:
```bash
# Run tests in parallel
pytest -n auto

# Skip slow tests during development
pytest -m "not slow"

# Use pytest-xdist
pip install pytest-xdist
```

### Problem: Flaky Tests

**Symptoms**: Tests pass sometimes, fail other times

**Common Causes**:
1. Timing dependencies
2. Shared state between tests
3. External service dependencies
4. Random data without seed

**Solutions**:
```python
# Use fixtures for isolation
@pytest.fixture
def isolated_environment(temp_dir):
    env = setup_environment()
    yield env
    cleanup_environment(env)

# Use deterministic data
import random
random.seed(42)

# Add timeouts
@pytest.mark.timeout(10)
def test_slow_operation():
    ...
```

### Problem: Import Errors on CI

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
1. Check requirements-test.txt includes all dependencies
2. Verify PYTHONPATH in CI matches local
3. Add `sys.path.insert(0, ...)` if needed
4. Use absolute imports, not relative

### Problem: Permission Errors

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```python
# Use temp_dir fixture instead of hardcoded paths
def test_with_temp_dir(temp_dir):
    work_dir = temp_dir('test_name')
    # work_dir is automatically cleaned up
```

---

## Best Practices

### Writing CI-Friendly Tests

✅ **DO**:
- Use `temp_dir` fixture for file operations
- Use deterministic test data
- Make tests independent (no shared state)
- Add timeouts to slow tests
- Use markers to categorize tests
- Mock external dependencies
- Write clear, descriptive test names

❌ **DON'T**:
- Use hardcoded file paths
- Rely on specific OS or environment
- Create tests that depend on each other
- Use `time.sleep()` for timing
- Test implementation details
- Leave tests without assertions
- Write tests that are order-dependent

### Optimizing Test Performance

**Parallel Execution**:
```bash
# pytest.ini already configured with:
--dist=loadfile
--numprocesses=auto
```

**Selective Testing**:
```bash
# During development, run only related tests
pytest tests/unit/test_specific_module.py

# Skip slow E2E tests during rapid iteration
pytest -m "not e2e and not slow"

# Run only failed tests from last run
pytest --lf
```

**Caching**:
```python
# Use pytest's caching for expensive setups
@pytest.fixture(scope="session")
def expensive_resource():
    resource = create_expensive_resource()
    yield resource
    cleanup_resource(resource)
```

### Maintaining Coverage

**Add Tests for New Code**:
```bash
# Before committing
pytest --cov=. --cov-report=term-missing

# Ensure new code is covered
git diff main...HEAD | grep "^+"  # Your changes
pytest --cov=. --cov-report=html
# Check coverage of changed files in htmlcov/
```

**Regular Coverage Reviews**:
1. Weekly: Review coverage trends on Codecov
2. Before releases: Ensure ≥80% coverage
3. During PR reviews: Check coverage impact

### Security Testing

**Mark Security Tests**:
```python
@pytest.mark.security
def test_prevents_path_traversal():
    """Verify path traversal attacks are blocked"""
    ...
```

**Run Before Deployment**:
```bash
# Run all security tests
pytest -m security -v

# Run security scan
bandit -r Working_Gold/TASK_204/scripts/

# Check dependencies
safety check
```

### Documentation

**Keep Tests Self-Documenting**:
```python
def test_encryption_with_wrong_key_fails():
    """
    Test that decryption with wrong key fails gracefully.

    This prevents an attacker from decrypting archives without
    the correct key, ensuring CRITICAL-2 fix is working.
    """
    # Arrange
    encryptor1 = ArchiveEncryption(key_file=None)
    encryptor2 = ArchiveEncryption(key_file=None)  # Different key

    # Act & Assert
    with pytest.raises(Exception):
        encryptor2.decrypt_file(encrypted_file, output_file)
```

---

## Quick Reference

### Common Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific category
pytest -m unit
pytest -m integration
pytest -m e2e

# Run in parallel
pytest -n auto

# Show slow tests
pytest --durations=10

# Run only failed tests
pytest --lf

# Run until first failure
pytest -x

# Verbose output
pytest -v -s
```

### File Locations

| File | Location | Purpose |
|------|----------|---------|
| Test files | `Working_Gold/TASK_205/tests/` | All test code |
| pytest config | `pytest.ini` | pytest configuration |
| Test requirements | `requirements-test.txt` | Test dependencies |
| CI workflows | `.github/workflows/` | GitHub Actions |
| Coverage config | `codecov.yml` | Codecov settings |
| Coverage reports | `htmlcov/` | HTML coverage output |

### Useful Links

- **GitHub Actions**: https://github.com/YOUR_REPO/actions
- **Codecov Dashboard**: https://codecov.io/gh/YOUR_REPO
- **pytest Documentation**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/

---

## Summary

The CI/CD pipeline ensures:
- ✅ All tests run automatically on every push/PR
- ✅ Coverage maintained at ≥80%
- ✅ Code quality enforced via quality gates
- ✅ Security scans on every PR
- ✅ Performance benchmarks tracked
- ✅ E2E tests run daily

**For Contributors**:
1. Write tests for all new code
2. Ensure tests pass locally before pushing
3. Maintain ≥80% coverage
4. Fix failing CI checks immediately
5. Review coverage reports on PRs

---

**Last Updated**: 2026-01-30
**Maintained by**: TASK_205 Phase 5
**Questions**: See TESTING_GUIDE.md or create an issue
