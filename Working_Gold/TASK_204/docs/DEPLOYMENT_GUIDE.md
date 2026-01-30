# TASK_204 - Deployment Guide
## AI Employee Vault Security Hardening

**Version**: 1.0
**Created**: 2026-01-29
**Target Audience**: System Administrators, DevOps Engineers
**Estimated Deployment Time**: 4-8 hours

---

## Overview

This guide provides step-by-step instructions for deploying all 8 CRITICAL security fixes implemented in TASK_204. The deployment is designed to be incremental, allowing you to deploy in phases with minimal disruption.

**Security Improvements**:
- 8 CRITICAL vulnerabilities fixed
- Security score: 55/100 → 81/100
- Risk level: MEDIUM-HIGH → LOW (enterprise-ready)

---

## Prerequisites

### System Requirements

**Operating System**:
- Windows 10/11 or Linux (Ubuntu 20.04+, CentOS 8+)
- macOS 11+ (for development environments)

**Software**:
- Python 3.7+ (3.9+ recommended)
- Git 2.x+
- Bash shell (Git Bash on Windows)

**Permissions**:
- Administrator/root access (for file permissions)
- Write access to AI_Employee_vault directory
- Write access to .git/hooks directory

### Python Package Installation

```bash
# Install required packages
pip install cryptography>=41.0.0
pip install zstandard>=0.21.0

# Verify installation
python -c "import cryptography; import zstandard; print('Packages installed successfully')"
```

---

## Deployment Strategy

### Recommended Deployment Order

1. **Phase 1 - File Security** (30 minutes) - IMMEDIATE
   - Secure sensitive files
   - Setup git hooks
   - Verify integrity checking

2. **Phase 3 - Validation** (1-2 hours) - HIGH PRIORITY
   - Deploy path validation
   - Deploy input validation
   - Test with sample operations

3. **Phase 4 - Workflow & Logging** (1-2 hours) - HIGH PRIORITY
   - Deploy approval verification
   - Replace logging with secure logging
   - Test approval workflow

4. **Phase 2 - Encryption** (2-4 hours) - MEDIUM PRIORITY
   - Setup encryption keys
   - Encrypt existing archives
   - Test encryption/decryption

### Rollback Strategy

Each phase can be rolled back independently:
- Phase 1: Restore previous file permissions
- Phase 2: Keep plaintext archives alongside encrypted ones initially
- Phase 3: Remove validation imports from code
- Phase 4: Revert to standard Python logging

---

## Phase 1 Deployment: File Security

### Step 1.1: Secure Sensitive Files (5 minutes)

**Execute file permission hardening**:

```bash
cd C:\Users\Lab One\AI_Employee_vault
bash Working_Gold/TASK_204/scripts/file_permissions.sh
```

**Expected Output**:
```
============================================================
AI Employee Vault - File Permission Hardener
CRITICAL-1 Fix: World-Readable Sensitive Files (CVSS 8.5)
============================================================
...
[OK] Secured: 45 files
[OK] Security hardening complete
```

**Verification**:
```bash
# Check file permissions (should show 0600 or -rw-------)
ls -l TASKS_Gold.md
ls -l STATUS_Gold.md
ls -l ERRORS_Gold.md
```

### Step 1.2: Install Git Pre-Commit Hook (10 minutes)

**Install the hook**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# Copy hook to .git/hooks
cp Working_Gold/TASK_204/scripts/pre-commit-hook.sh .git/hooks/pre-commit

# Make executable (Linux/Mac)
chmod +x .git/hooks/pre-commit

# On Windows (Git Bash)
# The hook should work automatically
```

**Test the hook**:

```bash
# Create a test file with a fake secret
echo "password=test123" > test_secret.txt
git add test_secret.txt

# Try to commit (should be blocked)
git commit -m "test"

# Expected: Hook blocks commit and shows warning
# Clean up
rm test_secret.txt
git reset
```

### Step 1.3: Run Git History Scan (Optional, 10 minutes)

**Only if concerned about existing secrets in git history**:

```bash
cd C:\Users\Lab One\AI_Employee_vault
bash Working_Gold/TASK_204/scripts/scan_git_history.sh > git_scan_results.txt

# Review results
cat git_scan_results.txt
```

**If secrets found**:
- Review each finding manually
- Use `git filter-repo` or BFG Repo-Cleaner to remove secrets
- Rotate any exposed credentials immediately

### Step 1.4: Setup Integrity Checking (5 minutes)

**Test integrity checker**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# Generate checksums for an existing archive
python Working_Gold/TASK_204/scripts/integrity_checker.py create \
  Archive_Gold/Completed/TASK_201 \
  Archive_Gold/Completed/TASK_201/checksums.json

# Verify integrity
python Working_Gold/TASK_204/scripts/integrity_checker.py verify \
  Archive_Gold/Completed/TASK_201 \
  Archive_Gold/Completed/TASK_201/checksums.json
```

**Setup weekly integrity checks** (cron job or Task Scheduler):

```bash
# Linux cron (weekly on Sunday at 2 AM)
0 2 * * 0 cd /path/to/AI_Employee_vault && python Working_Gold/TASK_204/scripts/integrity_checker.py verify-all

# Windows Task Scheduler (create a scheduled task)
# Action: python
# Arguments: C:\Users\Lab One\AI_Employee_vault\Working_Gold\TASK_204\scripts\integrity_checker.py verify-all
# Schedule: Weekly, Sunday 2:00 AM
```

---

## Phase 3 Deployment: Validation Frameworks

### Step 3.1: Deploy Path Validation (30 minutes)

**Import path validator in your code**:

```python
# Add to your file operation modules
from Working_Gold.TASK_204.scripts.path_validator import PathValidator, SecurityError

# Initialize validator
validator = PathValidator(vault_root='C:\\Users\\Lab One\\AI_Employee_vault')

# Validate paths before file operations
def safe_read_file(file_path):
    """Read file with path validation"""
    # Validate path
    if not validator.is_safe_path(file_path):
        raise SecurityError(f"Unsafe path: {file_path}")

    # Check for traversal attempts
    if validator.check_directory_traversal(file_path):
        raise SecurityError(f"Directory traversal detected: {file_path}")

    # Safe to read
    with open(file_path, 'r') as f:
        return f.read()
```

**Test path validation**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# Run tests
python Working_Gold/TASK_204/scripts/path_validator.py test

# Test specific paths
python Working_Gold/TASK_204/scripts/path_validator.py validate "Working_Gold/TASK_204/test.txt"
python Working_Gold/TASK_204/scripts/path_validator.py validate "../../../etc/passwd"
```

### Step 3.2: Deploy Input Validation (30 minutes)

**Import input validator in your code**:

```python
# Add to your task management modules
from Working_Gold.TASK_204.scripts.input_validator import InputValidator, ValidationError

# Validate task specifications
def create_task(task_spec):
    """Create task with validation"""
    try:
        # Validate complete spec
        validated_spec = InputValidator.validate_task_specification(task_spec)

        # Proceed with task creation
        # ...

    except ValidationError as e:
        print(f"Invalid task spec: {e}")
        return None
```

**Test input validation**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# Run comprehensive tests
python Working_Gold/TASK_204/scripts/input_validator.py test

# Test specific validations
python Working_Gold/TASK_204/scripts/input_validator.py validate-task-id "TASK_204"
python Working_Gold/TASK_204/scripts/input_validator.py validate-timestamp "2026-01-29 10:00:00.000"
python Working_Gold/TASK_204/scripts/input_validator.py sanitize-log "password=secret123"
```

---

## Phase 4 Deployment: Workflow & Logging

### Step 4.1: Deploy Approval Verification (1 hour)

**Import approval verifier in your code**:

```python
# Add to your state management modules
from Working_Gold.TASK_204.scripts.approval_verifier import verify_transition, ApprovalBypassError

# Verify state transitions
def transition_task_state(task_id, from_state, to_state, level, priority):
    """Transition task state with approval verification"""
    try:
        # Verify transition is allowed
        verify_transition(
            task_id=task_id,
            from_state=from_state,
            to_state=to_state,
            level=level,
            priority=priority
        )

        # Transition allowed, proceed
        # Update TASKS.md, STATUS.md, etc.
        # ...

    except ApprovalBypassError as e:
        # Transition blocked - log security violation
        print(f"Security violation: {e}")
        # Alert administrators
        return False

    return True
```

**Test approval verification**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# Run comprehensive tests
python Working_Gold/TASK_204/scripts/approval_verifier.py test

# Test specific transitions
python Working_Gold/TASK_204/scripts/approval_verifier.py verify \
  --task-id TASK_204 \
  --from-state AWAITING_APPROVAL \
  --to-state IN_PROGRESS \
  --level Gold \
  --priority CRITICAL
```

**Create approval log directories**:

```bash
mkdir -p Logs_Gold/Approvals
mkdir -p Logs_Silver/Approvals
mkdir -p Logs_Bronze/Approvals
```

### Step 4.2: Deploy Secure Logging (1 hour)

**Replace standard logging with secure logging**:

```python
# OLD CODE:
# import logging
# logger = logging.getLogger('my_component')

# NEW CODE:
import sys
sys.path.insert(0, 'C:\\Users\\Lab One\\AI_Employee_vault\\Working_Gold\\TASK_204\\scripts')
from secure_logging import get_secure_logger

logger = get_secure_logger(
    'my_component',
    log_file='Logs_Gold/Executions/my_component.log'
)

# Use exactly the same API
logger.info('Processing data...')  # Automatically sanitized
logger.error(f'Error with password={password}')  # Automatically sanitized
```

**Test secure logging**:

```bash
cd C:\Users\Lab One\AI_Employee_vault\Working_Gold\TASK_204\scripts

# Run tests
python secure_logging.py test

# Test sanitization
python secure_logging.py sanitize "API key: AKIA1234567890123456"
```

---

## Phase 2 Deployment: Encryption (Advanced)

### Step 2.1: Generate Encryption Key (10 minutes)

**Generate master key**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# Test encryption utils (generates key automatically)
python Working_Gold/TASK_204/scripts/encryption_utils.py test

# Verify key created
ls -l ~/.ai_employee_vault.key
# Should show: -rw------- (0600 permissions)
```

**Create key backups**:

```bash
# Backup 1: Base64 encoded to file
base64 ~/.ai_employee_vault.key > ~/ai_vault_key_backup.txt
# Store this file in password manager or secure USB drive

# Backup 2: Encrypted backup (requires gpg)
gpg -c ~/ai_vault_key_backup.txt
# Creates: ~/ai_vault_key_backup.txt.gpg
# Store this in cloud backup

# Delete plaintext backup
rm ~/ai_vault_key_backup.txt

# IMPORTANT: Test recovery before proceeding!
```

### Step 2.2: Test Encryption (15 minutes)

**Create test encrypted archive**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# Create a small test directory
mkdir -p test_encrypt/data
echo "Test file 1" > test_encrypt/data/file1.txt
echo "Test file 2" > test_encrypt/data/file2.txt

# Encrypt it
python Working_Gold/TASK_204/scripts/encryption_utils.py create \
  test_encrypt \
  test_archive.enc

# Verify encrypted file created
ls -lh test_archive.enc
ls -l test_archive.enc.json

# Extract it
python Working_Gold/TASK_204/scripts/encryption_utils.py extract \
  test_archive.enc \
  test_extract

# Verify contents match
diff -r test_encrypt test_extract
# Should show no differences

# Cleanup
rm -rf test_encrypt test_extract test_archive.enc test_archive.enc.json
```

### Step 2.3: Encrypt Existing Archives (2-4 hours)

**Encrypt Gold-level archives**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# For each completed task archive
for task_dir in Archive_Gold/Completed/TASK_*; do
    if [ -d "$task_dir" ]; then
        task_id=$(basename "$task_dir")
        echo "Encrypting $task_id..."

        # Create encrypted archive
        python Working_Gold/TASK_204/scripts/encryption_utils.py create \
          "$task_dir" \
          "$task_dir/archive.enc"

        # Verify it worked
        python Working_Gold/TASK_204/scripts/encryption_utils.py extract \
          "$task_dir/archive.enc" \
          "$task_dir.verify"

        # Compare (should match)
        diff -r "$task_dir" "$task_dir.verify" && echo "OK: $task_id verified"

        # Clean up verification
        rm -rf "$task_dir.verify"

        # Optional: Remove plaintext (ONLY after verifying backup!)
        # rm -rf "$task_dir"/*
        # Keep only archive.enc and archive.enc.json
    fi
done
```

**IMPORTANT**: Keep plaintext archives for at least 30 days until encryption proven stable.

---

## Integration Testing

### Test 1: Complete Workflow Simulation

**Simulate TASK_205 creation and execution**:

```bash
cd C:\Users\Lab One\AI_Employee_vault

# 1. Create task with input validation
python -c "
from Working_Gold.TASK_204.scripts.input_validator import InputValidator

spec = {
    'task_id': 'TASK_205',
    'description': 'Test task for deployment verification',
    'level': 'Gold',
    'priority': 'HIGH',
    'state': 'NEEDS_ACTION'
}

try:
    validated = InputValidator.validate_task_specification(spec)
    print('✓ Input validation passed')
except Exception as e:
    print(f'✗ Input validation failed: {e}')
"

# 2. Create working directory with path validation
python -c "
from Working_Gold.TASK_204.scripts.path_validator import PathValidator

validator = PathValidator()
try:
    task_dir = validator.validate_path('TASK_205', 'Working_Gold')
    print(f'✓ Path validation passed: {task_dir}')
except Exception as e:
    print(f'✗ Path validation failed: {e}')
"

# 3. Test state transition with approval verification
python Working_Gold/TASK_204/scripts/approval_verifier.py verify \
  --task-id TASK_205 \
  --from-state NEEDS_ACTION \
  --to-state PLANNING \
  --level Gold \
  --priority HIGH

# 4. Test secure logging
python -c "
from Working_Gold.TASK_204.scripts.secure_logging import get_secure_logger

logger = get_secure_logger('test_task_205', console=True)
logger.info('TASK_205 created successfully')
logger.info('Processing with password=secret123')  # Should be sanitized
print('✓ Secure logging working')
"
```

### Test 2: Security Verification

**Attempt to bypass each security control**:

```bash
# Test 1: Try to access file outside allowed directories
python -c "
from Working_Gold.TASK_204.scripts.path_validator import PathValidator
validator = PathValidator()
print('Attempting path traversal...')
print('Safe:', validator.is_safe_path('../../../etc/passwd'))  # Should be False
"

# Test 2: Try to transition without approval
python Working_Gold/TASK_204/scripts/approval_verifier.py verify \
  --task-id TASK_999 \
  --from-state PLANNING \
  --to-state IN_PROGRESS \
  --level Gold \
  --priority HIGH
# Should fail: requires AWAITING_APPROVAL first

# Test 3: Verify log sanitization
python -c "
from Working_Gold.TASK_204.scripts.input_validator import InputValidator
msg = 'User login: password=secret123, api_key=AKIA1234567890123456'
sanitized = InputValidator.sanitize_log_message(msg)
print('Original:', msg)
print('Sanitized:', sanitized)
assert 'secret123' not in sanitized, 'Password not sanitized!'
assert 'AKIA1234567890123456' not in sanitized, 'API key not sanitized!'
print('✓ Sanitization working')
"

# Test 4: Verify file permissions
ls -l TASKS_Gold.md | grep -- "^-rw-------" && echo "✓ File permissions secure"

# Test 5: Test encryption integrity
python -c "
import os
from Working_Gold.TASK_204.scripts.encryption_utils import ArchiveEncryption

# Create temp test
os.makedirs('test_enc_integrity/data', exist_ok=True)
with open('test_enc_integrity/data/test.txt', 'w') as f:
    f.write('Original content')

enc = ArchiveEncryption()
enc.create_encrypted_archive('test_enc_integrity', 'test_enc_integrity.enc')

# Tamper with encrypted file
with open('test_enc_integrity.enc', 'rb') as f:
    data = bytearray(f.read())
data[50] ^= 0xFF  # Flip bits
with open('test_enc_integrity.enc', 'wb') as f:
    f.write(data)

# Try to decrypt (should fail)
try:
    enc.extract_encrypted_archive('test_enc_integrity.enc', 'test_dec')
    print('✗ Tampering not detected!')
except:
    print('✓ Tampering detected (decryption failed as expected)')

# Cleanup
import shutil
shutil.rmtree('test_enc_integrity', ignore_errors=True)
os.remove('test_enc_integrity.enc')
"
```

---

## Post-Deployment Verification

### Verification Checklist

Run this checklist after deployment:

```bash
cd C:\Users\Lab One\AI_Employee_vault

echo "=== TASK_204 Deployment Verification ==="

# Phase 1 Verification
echo "[Phase 1] Checking file permissions..."
ls -l TASKS_Gold.md | grep "^-rw-------" && echo "✓ TASKS_Gold.md secured" || echo "✗ TASKS_Gold.md not secured"
ls -l STATUS_Gold.md | grep "^-rw-------" && echo "✓ STATUS_Gold.md secured" || echo "✗ STATUS_Gold.md not secured"
ls -l ERRORS_Gold.md | grep "^-rw-------" && echo "✓ ERRORS_Gold.md secured" || echo "✗ ERRORS_Gold.md not secured"

echo "[Phase 1] Checking git hooks..."
[ -f .git/hooks/pre-commit ] && echo "✓ Pre-commit hook installed" || echo "✗ Pre-commit hook missing"

echo "[Phase 1] Checking integrity checker..."
python Working_Gold/TASK_204/scripts/integrity_checker.py test > /dev/null 2>&1 && echo "✓ Integrity checker working" || echo "✗ Integrity checker failed"

# Phase 2 Verification
echo "[Phase 2] Checking encryption key..."
[ -f ~/.ai_employee_vault.key ] && echo "✓ Encryption key exists" || echo "✗ Encryption key missing"
ls -l ~/.ai_employee_vault.key | grep "^-rw-------" && echo "✓ Key permissions secure" || echo "✗ Key permissions insecure"

echo "[Phase 2] Checking encryption packages..."
python -c "import cryptography; import zstandard" 2>/dev/null && echo "✓ Encryption packages installed" || echo "✗ Encryption packages missing"

# Phase 3 Verification
echo "[Phase 3] Testing path validation..."
python Working_Gold/TASK_204/scripts/path_validator.py test > /dev/null 2>&1 && echo "✓ Path validator working" || echo "✗ Path validator failed"

echo "[Phase 3] Testing input validation..."
python Working_Gold/TASK_204/scripts/input_validator.py test > /dev/null 2>&1 && echo "✓ Input validator working" || echo "✗ Input validator failed"

# Phase 4 Verification
echo "[Phase 4] Testing approval verification..."
python Working_Gold/TASK_204/scripts/approval_verifier.py test > /dev/null 2>&1 && echo "✓ Approval verifier working" || echo "✗ Approval verifier failed"

echo "[Phase 4] Checking approval log directories..."
[ -d Logs_Gold/Approvals ] && echo "✓ Approval log directory exists" || echo "✗ Approval log directory missing"

echo "=== Verification Complete ==="
```

---

## Troubleshooting

### Issue: File permissions not set

**Symptoms**: `ls -l TASKS_Gold.md` shows `-rw-r--r--` instead of `-rw-------`

**Solution**:
```bash
chmod 0600 TASKS_Gold.md
# Or re-run the file permissions script
bash Working_Gold/TASK_204/scripts/file_permissions.sh
```

### Issue: Pre-commit hook not triggering

**Symptoms**: Can commit files with secrets

**Solution**:
```bash
# Ensure hook is executable
chmod +x .git/hooks/pre-commit

# Test manually
.git/hooks/pre-commit

# Check git config
git config core.hooksPath  # Should be empty or .git/hooks
```

### Issue: Encryption key not found

**Symptoms**: `FileNotFoundError: ~/.ai_employee_vault.key`

**Solution**:
```bash
# Generate new key
python Working_Gold/TASK_204/scripts/encryption_utils.py test

# Or restore from backup
base64 -d ~/key_backup.txt > ~/.ai_employee_vault.key
chmod 0600 ~/.ai_employee_vault.key
```

### Issue: Python packages not found

**Symptoms**: `ModuleNotFoundError: No module named 'cryptography'`

**Solution**:
```bash
pip install cryptography zstandard

# Or with specific versions
pip install cryptography==41.0.0 zstandard==0.21.0
```

### Issue: Decryption fails after encryption

**Symptoms**: `cryptography.exceptions.InvalidTag`

**Solution**:
- File may be corrupted or tampered with
- Verify using wrong key (check key file location)
- Try restoring from backup
- Check disk space (encryption requires temp space)

---

## Maintenance

### Weekly Tasks

1. **Integrity Verification** (automated via cron/Task Scheduler)
   ```bash
   python Working_Gold/TASK_204/scripts/integrity_checker.py verify-all
   ```

2. **Review Approval Audit Logs**
   ```bash
   tail -100 Logs_Gold/Approvals/approval_audit.log
   # Look for [BLOCKED] entries indicating bypass attempts
   ```

3. **Review Security Logs**
   ```bash
   grep -i "password\|api.key\|secret" Logs_Gold/Executions/*.log
   # Should show *** instead of actual values
   ```

### Monthly Tasks

1. **Key Backup Verification**
   ```bash
   # Test recovery from backup
   mv ~/.ai_employee_vault.key ~/.ai_employee_vault.key.original
   base64 -d ~/key_backup.txt > ~/.ai_employee_vault.key
   chmod 0600 ~/.ai_employee_vault.key

   # Test decryption with restored key
   python Working_Gold/TASK_204/scripts/encryption_utils.py extract \
     test_archive.enc test_restore

   # Restore original if test passed
   mv ~/.ai_employee_vault.key.original ~/.ai_employee_vault.key
   ```

2. **Git History Scan**
   ```bash
   bash Working_Gold/TASK_204/scripts/scan_git_history.sh > monthly_scan.txt
   # Review for any new secrets
   ```

### Annual Tasks

1. **Key Rotation** (see KEY_MANAGEMENT.md for detailed procedure)
2. **Security Audit** (review all 8 CRITICAL fixes still effective)
3. **Update Encryption Packages**
   ```bash
   pip install --upgrade cryptography zstandard
   ```

---

## Rollback Procedures

### Rollback Phase 1 (File Permissions)

```bash
# Reset to default permissions (not recommended)
find . -type f -name "*.md" -exec chmod 0644 {} \;
find Logs_Gold -type f -exec chmod 0644 {} \;

# Remove pre-commit hook
rm .git/hooks/pre-commit
```

### Rollback Phase 2 (Encryption)

```bash
# Extract all encrypted archives to plaintext
for enc_file in Archive_Gold/Completed/*/archive.enc; do
    task_dir=$(dirname "$enc_file")
    python Working_Gold/TASK_204/scripts/encryption_utils.py extract \
      "$enc_file" "${task_dir}.plaintext"
done

# Remove encryption key (after verifying all archives extracted)
# rm ~/.ai_employee_vault.key
```

### Rollback Phase 3 (Validation)

```python
# Remove validation imports from your code
# Comment out or remove:
# from path_validator import PathValidator
# from input_validator import InputValidator
```

### Rollback Phase 4 (Approval & Logging)

```python
# Remove approval verification from your code
# Replace secure_logging with standard logging:
import logging
logger = logging.getLogger('my_component')
```

---

## Security Best Practices Post-Deployment

1. **Never commit keys to git** - Always check .gitignore includes `*.key`
2. **Test backups regularly** - Verify key recovery procedure monthly
3. **Monitor approval logs** - Review for bypass attempts weekly
4. **Rotate keys annually** - Follow KEY_MANAGEMENT.md procedure
5. **Keep packages updated** - Update cryptography and zstandard quarterly
6. **Audit file permissions** - Re-run file_permissions.sh monthly
7. **Review sanitized logs** - Verify no sensitive data leaking
8. **Test disaster recovery** - Practice full system restore semi-annually

---

## Support & References

**Documentation**:
- `Working_Gold/TASK_204/docs/KEY_MANAGEMENT.md` - Encryption key management
- `Working_Gold/TASK_204/docs/PHASE1_SUMMARY.md` - File security details
- `Working_Gold/TASK_204/docs/PHASE2_SUMMARY.md` - Encryption details
- `Working_Gold/TASK_204/docs/PHASE3_SUMMARY.md` - Validation details
- `Working_Gold/TASK_204/docs/PHASE4_SUMMARY.md` - Workflow details
- `Working_Gold/TASK_204/docs/TASK_204_PROGRESS_REPORT.md` - Complete overview

**Testing Scripts**:
- All scripts have `test` command: `python script.py test`
- Use `--help` for usage: `python script.py --help`

**Security Incidents**:
- Follow KEY_MANAGEMENT.md emergency procedures
- Review approval_audit.log for security violations
- Rotate keys immediately if compromise suspected

---

**Deployment Guide Version**: 1.0
**Last Updated**: 2026-01-29
**Status**: Production Ready
