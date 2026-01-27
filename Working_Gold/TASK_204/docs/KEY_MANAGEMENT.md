# Key Management Guide
## AI Employee Vault - Encryption Key Procedures

**Document Version**: 1.0
**Created**: 2026-01-27
**Security Level**: CRITICAL
**Related**: TASK_204 Phase 2 - CRITICAL-2 Fix

---

## Overview

This document describes encryption key management procedures for the AI Employee Vault encrypted archive system. Proper key management is CRITICAL - losing the encryption key means losing access to all encrypted archives permanently.

**Encryption**: AES-256-GCM (256-bit keys)
**Key Storage**: File-based with 0600 permissions
**Default Location**: `~/.ai_employee_vault.key`

---

## Key Generation

### Initial Setup

**Generate Master Key**:
```bash
cd AI_Employee_vault
python Working_Gold/TASK_204/scripts/encryption_utils.py test

# This will generate a new key at ~/.ai_employee_vault.key
# if it doesn't exist
```

**Manual Key Generation**:
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Generate 256-bit key
key = AESGCM.generate_key(bit_length=256)

# Save to file
with open('~/.ai_employee_vault.key', 'wb') as f:
    f.write(key)

# Set restrictive permissions
import os
os.chmod('~/.ai_employee_vault.key', 0o600)
```

**Key Properties**:
- Length: 32 bytes (256 bits)
- Format: Binary
- Permissions: 0600 (owner read/write only)
- Location: User's home directory

---

## Key Storage

### Primary Key Storage

**Recommended Location**: `~/.ai_employee_vault.key`

**Security Requirements**:
- File permissions: 0600 (owner-only)
- Not in git repository
- Not in cloud sync folders (Dropbox, OneDrive, etc.)
- Encrypted disk recommended

**Verify Permissions**:
```bash
ls -l ~/.ai_employee_vault.key
# Should show: -rw------- (0600)

# Fix if needed:
chmod 0600 ~/.ai_employee_vault.key
```

---

### Backup Key Storage

⚠️ **CRITICAL**: Create backups of your encryption key!

**Backup Locations** (choose 2-3):

1. **Secure USB Drive**
   - Store on encrypted USB drive
   - Keep in safe/secure location
   - Label: "AI Vault Key Backup YYYY-MM-DD"

2. **Password Manager**
   - Convert key to base64
   - Store in secure note in password manager (1Password, LastPass, etc.)
   - Tag: "ai-employee-vault-key"

3. **Encrypted Cloud Storage**
   - Encrypt key with strong passphrase first
   - Upload to secure cloud storage
   - Document passphrase separately

4. **Physical Safe**
   - Print base64-encoded key on paper
   - Store in fireproof safe
   - Include recovery instructions

**Backup Command**:
```bash
# Base64 encode for storage
base64 ~/.ai_employee_vault.key > ~/ai_vault_key_backup.txt

# Encrypt backup (requires gpg)
gpg -c ~/ai_vault_key_backup.txt

# Store ai_vault_key_backup.txt.gpg securely
# Delete plaintext backup
rm ~/ai_vault_key_backup.txt
```

---

## Key Usage

### Creating Encrypted Archives

**Basic Usage**:
```bash
python encryption_utils.py create SOURCE_DIR OUTPUT_FILE.enc
```

**Specify Custom Key**:
```bash
python encryption_utils.py create SOURCE_DIR OUTPUT_FILE.enc --key /path/to/key
```

**Compression Level**:
```bash
# Level 1 (fastest, less compression)
python encryption_utils.py create SOURCE_DIR OUTPUT_FILE.enc --level 1

# Level 3 (balanced, default)
python encryption_utils.py create SOURCE_DIR OUTPUT_FILE.enc --level 3

# Level 10 (slower, better compression)
python encryption_utils.py create SOURCE_DIR OUTPUT_FILE.enc --level 10
```

---

### Extracting Encrypted Archives

**Basic Usage**:
```bash
python encryption_utils.py extract ENCRYPTED_FILE.enc OUTPUT_DIR
```

**Specify Custom Key**:
```bash
python encryption_utils.py extract ENCRYPTED_FILE.enc OUTPUT_DIR --key /path/to/key
```

---

## Key Rotation

### When to Rotate Keys

Rotate encryption keys if:
- Key may have been compromised
- Employee with key access leaves
- Regular schedule (annually recommended)
- Security audit recommendation
- Compliance requirement

### Key Rotation Procedure

**Step 1: Generate New Key**
```bash
# Backup old key
cp ~/.ai_employee_vault.key ~/.ai_employee_vault.key.old

# Generate new key
python -c "
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
with open(os.path.expanduser('~/.ai_employee_vault.key.new'), 'wb') as f:
    f.write(key)
os.chmod(os.path.expanduser('~/.ai_employee_vault.key.new'), 0o600)
print('[OK] New key generated: ~/.ai_employee_vault.key.new')
"
```

**Step 2: Re-encrypt All Archives**
```python
# rotate_keys.py
from pathlib import Path
from encryption_utils import ArchiveEncryption

# Initialize with old and new keys
old_encryptor = ArchiveEncryption('~/.ai_employee_vault.key.old')
new_encryptor = ArchiveEncryption('~/.ai_employee_vault.key.new')

# Find all encrypted archives
for enc_file in Path('Archive_Gold/Completed').rglob('*.enc'):
    print(f"[ROTATE] {enc_file}")

    # Decrypt with old key
    temp_dir = enc_file.parent / '.temp_rotate'
    temp_dir.mkdir(exist_ok=True)

    old_encryptor.extract_encrypted_archive(enc_file, temp_dir)

    # Re-encrypt with new key
    new_enc_file = enc_file.with_suffix('.enc.new')
    new_encryptor.create_encrypted_archive(temp_dir / enc_file.stem, new_enc_file)

    # Verify new archive
    test_dir = enc_file.parent / '.temp_verify'
    new_encryptor.extract_encrypted_archive(new_enc_file, test_dir)

    # If verification passes, replace old archive
    enc_file.replace(enc_file.with_suffix('.enc.old'))
    new_enc_file.replace(enc_file)

    # Clean up
    import shutil
    shutil.rmtree(temp_dir)
    shutil.rmtree(test_dir)

    print(f"[OK] Rotated: {enc_file}")
```

**Step 3: Activate New Key**
```bash
# Backup old key (keep for emergency)
mv ~/.ai_employee_vault.key ~/.ai_employee_vault.key.old.$(date +%Y%m%d)

# Activate new key
mv ~/.ai_employee_vault.key.new ~/.ai_employee_vault.key

echo "[OK] New key activated"
```

**Step 4: Verify**
```bash
# Test decryption with new key
python encryption_utils.py extract Archive_Gold/Completed/TASK_201/archive.enc test_extract

# If successful, old key can be archived securely
```

---

## Key Recovery

### If Key Is Lost

⚠️ **WARNING**: Without the encryption key, encrypted archives CANNOT be recovered.

**Recovery Steps**:

1. **Check Backup Locations**
   - USB drive
   - Password manager
   - Encrypted cloud storage
   - Physical safe

2. **Restore from Backup**
```bash
# From base64 backup
base64 -d ~/ai_vault_key_backup.txt > ~/.ai_employee_vault.key
chmod 0600 ~/.ai_employee_vault.key

# From encrypted backup (gpg)
gpg -d ~/ai_vault_key_backup.txt.gpg | base64 -d > ~/.ai_employee_vault.key
chmod 0600 ~/.ai_employee_vault.key
```

3. **Verify Recovery**
```bash
# Test with known encrypted archive
python encryption_utils.py extract test_archive.enc test_output
```

### If Key Cannot Be Recovered

If the key is permanently lost:
- **Encrypted archives are unrecoverable** (AES-256 is cryptographically secure)
- Restore from unencrypted backups if available
- Implement prevention measures for future:
  - Multiple backup locations
  - Regular backup verification
  - Key recovery testing

---

## Security Best Practices

### DO

✅ **Keep Multiple Backups**
- At least 2 backup locations
- Test backups regularly
- Update backups after key rotation

✅ **Restrict Permissions**
- Always 0600 for key files
- Never share keys via email/chat
- Use secure transfer methods if needed

✅ **Document Key Location**
- Document in secure location
- Include recovery procedures
- Keep up-to-date

✅ **Regular Testing**
- Test key recovery quarterly
- Verify backups work
- Practice rotation procedure

✅ **Monitor Key Access**
- Review file access logs
- Audit who has key access
- Revoke access when needed

### DON'T

❌ **Store in Git**
- Never commit key to git repository
- Add to .gitignore
- Scan history for accidental commits

❌ **Store in Cloud Sync**
- Don't keep in Dropbox/OneDrive/etc.
- Risk of unauthorized access
- Sync conflicts can corrupt key

❌ **Share Unencrypted**
- Never email key
- Never paste in chat/tickets
- Don't store in unencrypted notes

❌ **Use Weak Permissions**
- Never 0644 or 0777
- Always 0600 (owner-only)
- Validate permissions regularly

❌ **Single Point of Failure**
- Don't rely on single backup
- Don't store all backups together
- Test recovery procedures

---

## Compliance & Audit

### Key Management Audit Checklist

- [ ] Primary key exists at documented location
- [ ] Primary key has 0600 permissions
- [ ] At least 2 backup copies exist
- [ ] Backup locations documented
- [ ] Backup verification tested (last 90 days)
- [ ] Key rotation schedule defined
- [ ] Key access list documented and current
- [ ] Recovery procedures documented
- [ ] Recovery procedures tested (last 180 days)
- [ ] No keys in git history
- [ ] No keys in cloud sync folders
- [ ] Encryption tested on sample archives

### Compliance Requirements

**PCI-DSS** (if applicable):
- Key rotation: Annually minimum
- Access control: Documented and enforced
- Audit trail: Key access logged

**HIPAA** (if applicable):
- Encryption: AES-256 compliant
- Key management: Documented procedures
- Access control: Role-based

**GDPR** (if applicable):
- Data protection: Encryption at rest
- Key security: Proper storage and backups
- Breach notification: 72-hour window

---

## Troubleshooting

### Key File Not Found

```bash
# Check if key exists
ls -l ~/.ai_employee_vault.key

# If not found, check backups
# If no backups, generate new key (old archives unrecoverable)
```

### Wrong Permissions

```bash
# Fix permissions
chmod 0600 ~/.ai_employee_vault.key

# Verify
ls -l ~/.ai_employee_vault.key
```

### Decryption Fails

Possible causes:
1. **Wrong Key**: Using different key than encryption
   - Check key file location
   - Try backup keys

2. **Corrupted File**: Archive file damaged
   - Verify file integrity
   - Restore from backup

3. **Tampered Data**: File modified after encryption
   - AES-GCM detects tampering
   - Cannot decrypt tampered files

### Key Rotation Fails

```bash
# Verify old key works
python encryption_utils.py extract test.enc test_out --key ~/.ai_employee_vault.key.old

# Verify new key is valid
python encryption_utils.py test --key ~/.ai_employee_vault.key.new

# Re-run rotation for failed archives
```

---

## Emergency Procedures

### Key Compromise Suspected

**Immediate Actions** (within 1 hour):
1. Generate new key immediately
2. Begin key rotation for all archives
3. Audit key access logs
4. Identify potential exposure scope
5. Notify security team/stakeholders

**Follow-up Actions** (within 24 hours):
1. Complete key rotation
2. Review and update access controls
3. Document incident
4. Implement additional safeguards
5. Consider breach notification requirements

### Encryption Key Lost

**Immediate Actions**:
1. Check all backup locations
2. Attempt recovery procedures
3. If unrecoverable, assess impact
4. Document loss incident

**Recovery Actions**:
1. Restore from unencrypted backups if available
2. Recreate lost archives if possible
3. Implement enhanced backup procedures
4. Generate new key for future archives

---

## Support & Contacts

**Key Management Issues**: Contact system administrator
**Security Incidents**: Follow incident response procedures
**Technical Support**: Reference TASK_204 documentation

---

**Document Status**: APPROVED
**Next Review**: 2027-01-27
**Maintained By**: AI_Employee
