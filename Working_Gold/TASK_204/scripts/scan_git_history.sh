#!/bin/bash
# scan_git_history.sh - Scan entire git history for secrets
# CRITICAL-7 Fix: Git History May Contain Secrets (CVSS 7.0)
# Created: 2026-01-27 for TASK_204
# Purpose: Scan all commits in git history for potential secrets

echo "============================================"
echo "AI Employee Vault - Git History Scanner"
echo "CRITICAL-7 Fix: Historical Secret Detection"
echo "============================================"
echo ""
echo "Scanning entire git history for secrets..."
echo "This may take a few minutes..."
echo ""

# Secret patterns
declare -a PATTERNS=(
    "password"
    "api[_-]?key"
    "secret"
    "token"
    "AKIA[0-9A-Z]{16}"
    "ghp_[A-Za-z0-9]{36}"
    "sk-[A-Za-z0-9]{32,}"
)

FOUND_SECRETS=0
COMMITS_SCANNED=0
SUSPICIOUS_COMMITS=()

# Get all commit hashes
ALL_COMMITS=$(git log --all --pretty=format:"%H")

for commit in $ALL_COMMITS; do
    ((COMMITS_SCANNED++))

    # Show progress every 10 commits
    if [ $((COMMITS_SCANNED % 10)) -eq 0 ]; then
        echo "[SCAN] Scanned $COMMITS_SCANNED commits..."
    fi

    # Check commit diff for patterns
    for pattern in "${PATTERNS[@]}"; do
        if git show $commit | grep -iP "$pattern" > /dev/null 2>&1; then
            echo ""
            echo "[WARN] Potential secret in commit: $commit"
            echo "       Pattern: $pattern"
            git show --stat $commit | head -5
            FOUND_SECRETS=1
            SUSPICIOUS_COMMITS+=("$commit")
            break
        fi
    done
done

echo ""
echo "============================================"
echo "Scan Complete"
echo "============================================"
echo "Commits scanned: $COMMITS_SCANNED"
echo "Suspicious commits: ${#SUSPICIOUS_COMMITS[@]}"
echo ""

if [ $FOUND_SECRETS -eq 1 ]; then
    echo "[WARN] Potential secrets found in git history"
    echo ""
    echo "Suspicious commits:"
    for commit in "${SUSPICIOUS_COMMITS[@]}"; do
        echo "  - $commit"
    done
    echo ""
    echo "Review these commits manually:"
    echo "  git show <commit-hash>"
    echo ""
    echo "If secrets are confirmed, consider:"
    echo "1. Rotate the exposed credentials immediately"
    echo "2. Use BFG Repo-Cleaner or git-filter-branch to remove secrets"
    echo "3. Force push cleaned history (requires coordination)"
    echo ""
    exit 1
else
    echo "[OK] No secrets detected in git history"
    exit 0
fi
