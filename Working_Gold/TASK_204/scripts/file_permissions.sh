#!/bin/bash
# file_permissions.sh - Set secure permissions on sensitive files
# CRITICAL-1 Fix: World-Readable Sensitive Files (CVSS 8.5)
# Created: 2026-01-27 for TASK_204
# Purpose: Set 0600 (owner-only) permissions on all sensitive files

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "============================================"
echo "AI Employee Vault - File Permission Hardening"
echo "CRITICAL-1 Fix: Securing Sensitive Files"
echo "============================================"
echo ""
echo "Vault Root: $VAULT_ROOT"
echo "Target: Set 0600 permissions on sensitive files"
echo ""

# Change to vault root
cd "$VAULT_ROOT"

# Counter for files secured
SECURED_COUNT=0
ERROR_COUNT=0

# Function to secure file permissions
secure_file() {
    local file="$1"

    if [ -f "$file" ]; then
        # Get current permissions
        current_perms=$(stat -c "%a" "$file" 2>/dev/null || stat -f "%OLp" "$file" 2>/dev/null || echo "unknown")

        # Set 0600 permissions
        if chmod 0600 "$file" 2>/dev/null; then
            echo "✅ Secured: $file (was: $current_perms, now: 0600)"
            ((SECURED_COUNT++))
        else
            echo "❌ Failed: $file (permission denied)"
            ((ERROR_COUNT++))
        fi
    fi
}

# Function to secure directory permissions
secure_directory() {
    local dir="$1"

    if [ -d "$dir" ]; then
        # Set 0700 permissions for directories
        if chmod 0700 "$dir" 2>/dev/null; then
            echo "✅ Secured directory: $dir (0700)"
            ((SECURED_COUNT++))
        else
            echo "❌ Failed directory: $dir (permission denied)"
            ((ERROR_COUNT++))
        fi
    fi
}

echo "Step 1: Securing Gold-level tracking files..."
echo "---------------------------------------------"
secure_file "TASKS_Gold.md"
secure_file "STATUS_Gold.md"
secure_file "ERRORS_Gold.md"
echo ""

echo "Step 2: Securing Silver-level tracking files..."
echo "------------------------------------------------"
secure_file "TASKS_Silver.md"
secure_file "STATUS_Silver.md"
secure_file "ERRORS_Silver.md"
echo ""

echo "Step 3: Securing Bronze-level tracking files..."
echo "------------------------------------------------"
secure_file "TASKS_Bronze.md"
secure_file "STATUS_Bronze.md"
secure_file "ERRORS_Bronze.md"
echo ""

echo "Step 4: Securing Gold-level execution logs..."
echo "----------------------------------------------"
if [ -d "Logs_Gold/Executions" ]; then
    for log in Logs_Gold/Executions/*.log; do
        secure_file "$log"
    done
fi
echo ""

echo "Step 5: Securing Gold-level completion reports..."
echo "--------------------------------------------------"
if [ -d "Logs_Gold/Completions" ]; then
    for report in Logs_Gold/Completions/*.md; do
        secure_file "$report"
    done
fi
echo ""

echo "Step 6: Securing Silver-level logs..."
echo "--------------------------------------"
if [ -d "Logs_Silver/Executions" ]; then
    for log in Logs_Silver/Executions/*.log; do
        secure_file "$log"
    done
fi
if [ -d "Logs_Silver/Completions" ]; then
    for report in Logs_Silver/Completions/*.md; do
        secure_file "$report"
    done
fi
echo ""

echo "Step 7: Securing Bronze-level logs..."
echo "--------------------------------------"
if [ -d "Logs_Bronze/Executions" ]; then
    for log in Logs_Bronze/Executions/*.log; do
        secure_file "$log"
    done
fi
if [ -d "Logs_Bronze/Completions" ]; then
    for report in Logs_Bronze/Completions/*.md; do
        secure_file "$report"
    done
fi
echo ""

echo "Step 8: Securing planning documents..."
echo "---------------------------------------"
if [ -d "Planning_Gold/Active" ]; then
    for plan in Planning_Gold/Active/*.md; do
        secure_file "$plan"
    done
fi
if [ -d "Planning_Gold/Approved" ]; then
    for plan in Planning_Gold/Approved/*.md; do
        secure_file "$plan"
    done
fi
if [ -d "Planning_Silver/Active" ]; then
    for plan in Planning_Silver/Active/*.md; do
        secure_file "$plan"
    done
fi
if [ -d "Planning_Silver/Approved" ]; then
    for plan in Planning_Silver/Approved/*.md; do
        secure_file "$plan"
    done
fi
echo ""

echo "Step 9: Securing approval documents..."
echo "---------------------------------------"
if [ -d "Approvals_Gold" ]; then
    for approval in Approvals_Gold/*.json; do
        secure_file "$approval"
    done
fi
if [ -d "Approvals_Silver" ]; then
    for approval in Approvals_Silver/*.json; do
        secure_file "$approval"
    done
fi
echo ""

echo "Step 10: Securing archive directories..."
echo "-----------------------------------------"
if [ -d "Archive_Gold/Completed" ]; then
    for task_dir in Archive_Gold/Completed/*/; do
        if [ -d "$task_dir" ]; then
            secure_directory "$task_dir"
            # Secure all files in archive
            find "$task_dir" -type f -exec chmod 0600 {} \; 2>/dev/null && echo "  ✅ Secured all files in $(basename "$task_dir")"
        fi
    done
fi
if [ -d "Archive_Silver/Completed" ]; then
    for task_dir in Archive_Silver/Completed/*/; do
        if [ -d "$task_dir" ]; then
            secure_directory "$task_dir"
            find "$task_dir" -type f -exec chmod 0600 {} \; 2>/dev/null && echo "  ✅ Secured all files in $(basename "$task_dir")"
        fi
    done
fi
echo ""

echo "============================================"
echo "File Permission Hardening Complete"
echo "============================================"
echo "Files secured: $SECURED_COUNT"
echo "Errors: $ERROR_COUNT"
echo ""

if [ $ERROR_COUNT -eq 0 ]; then
    echo "✅ SUCCESS: All sensitive files secured with 0600 permissions"
    echo "✅ CRITICAL-1 vulnerability mitigated"
    exit 0
else
    echo "⚠️  WARNING: Some files could not be secured ($ERROR_COUNT errors)"
    echo "⚠️  Review errors above and address permission issues"
    exit 1
fi
