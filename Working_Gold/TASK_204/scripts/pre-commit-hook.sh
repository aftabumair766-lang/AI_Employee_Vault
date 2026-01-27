#!/bin/bash
# pre-commit-hook.sh - Prevent secrets from being committed
# CRITICAL-7 Fix: Git History May Contain Secrets (CVSS 7.0)
# Created: 2026-01-27 for TASK_204
# Purpose: Scan staged files for potential secrets before commit

# Secret patterns to detect
declare -a SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]+['\"]"
    "api[_-]?key\s*=\s*['\"][^'\"]+['\"]"
    "secret\s*=\s*['\"][^'\"]+['\"]"
    "token\s*=\s*['\"][^'\"]+['\"]"
    "[A-Za-z0-9+/]{40,}"
    "sk-[A-Za-z0-9]{32,}"
    "ghp_[A-Za-z0-9]{36}"
    "AKIA[0-9A-Z]{16}"
)

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "[OK] No files staged for commit"
    exit 0
fi

FOUND_SECRETS=0

echo "============================================"
echo "AI Employee Vault - Secret Scanning"
echo "CRITICAL-7 Fix: Pre-Commit Hook"
echo "============================================"
echo ""
echo "Scanning $(echo "$STAGED_FILES" | wc -l) staged files..."
echo ""

for file in $STAGED_FILES; do
    # Skip binary files
    if file "$file" | grep -q "text"; then
        for pattern in "${SECRET_PATTERNS[@]}"; do
            if grep -iP "$pattern" "$file" > /dev/null 2>&1; then
                echo "[ERR] Potential secret found in $file"
                grep -inP "$pattern" "$file" | head -5
                echo ""
                FOUND_SECRETS=1
            fi
        done
    fi
done

if [ $FOUND_SECRETS -eq 1 ]; then
    echo ""
    echo "============================================"
    echo "[BLOCKED] Commit blocked: Potential secrets detected"
    echo "============================================"
    echo ""
    echo "Please remove secrets before committing."
    echo "If this is a false positive, you can:"
    echo "1. Remove the detected pattern"
    echo "2. Use git commit --no-verify (NOT recommended)"
    echo ""
    exit 1
fi

echo "[OK] No secrets detected"
echo "[OK] Commit allowed"
echo ""
exit 0
