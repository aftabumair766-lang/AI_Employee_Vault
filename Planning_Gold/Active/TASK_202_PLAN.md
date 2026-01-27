# TASK PLAN: TASK_202 - System Cleanup (Remove Legacy Root-Level Files)

**Task ID**: TASK_202
**Level**: Gold (System Improvement)
**Created**: 2026-01-26 21:48:04
**Plan Created**: 2026-01-26 21:52:00
**Status**: AWAITING_APPROVAL

---

## Executive Summary

**Objective**: Remove legacy root-level files identified as CRITICAL technical debt in TASK_201 multi-agent assessment, establishing single source of truth architecture.

**Impact**: System-wide structural improvement, eliminating ambiguity about authoritative data sources.

**Duration**: 15-25 minutes (efficient Gold-level execution)

**Risk Level**: MEDIUM (destructive operations with complete backup/rollback)

---

## Why This Task Requires Approval

This Gold-level task requires approval due to:

1. **System-Wide Impact**: Affects root directory structure and file organization
2. **Destructive Operations**: File deletion (even with backup procedures)
3. **Potential Workflow Disruption**: Could impact existing processes or tooling
4. **Critical Technical Debt**: Implements Action #1 from TASK_201 CRITICAL findings
5. **Git History Changes**: Uses `git rm` to properly remove tracked files

**Approval Timeout**: 4 hours (Gold-level extended approval window)

---

## Pre-Cleanup Analysis - Files Identified

### Legacy Core Governance Files (Root Level)

**Files to Remove** (superseded by level-specific versions):

1. ✗ `TASKS.md` → Superseded by `Bronze/TASKS.md`
2. ✗ `STATUS.md` → Superseded by `Bronze/STATUS.md` (if exists)
3. ✗ `ERRORS.md` → Superseded by `Bronze/ERRORS.md`
4. ✗ `TASKS_Silver.md` → Superseded by `Silver/TASKS_Silver.md`
5. ✗ `TASKS_Gold.md` → Superseded by `Gold/TASKS_Gold.md`
6. ✗ `ERRORS_Silver.md` → Superseded by `Silver/ERRORS_Silver.md`
7. ✗ `ERRORS_Gold.md` → Superseded by `Gold/ERRORS_Gold.md`
8. ✗ `MCP_REGISTRY.md` → Superseded by `Bronze/MCP_REGISTRY.md`
9. ✗ `MCP_REGISTRY_Silver.md` → Superseded by `Silver/MCP_REGISTRY_Silver.md`
10. ✗ `MCP_REGISTRY_Gold.md` → Superseded by `Gold/MCP_REGISTRY_Gold.md`
11. ✗ `DASHBOARD_Silver.md` → Superseded by `Silver/DASHBOARD_Silver.md`
12. ✗ `DASHBOARD_Gold.md` → Superseded by `Gold/DASHBOARD_Gold.md`

### Legacy Empty/Obsolete Files

13. ✗ `2026-01-14.md` (empty placeholder)
14. ✗ `Company_Handbook.md` (empty placeholder)
15. ✗ `Dashboard.md` (empty placeholder)

### Legacy Directories (Root Level)

**Directories to Remove** (superseded by level-specific versions):

16. ✗ `Archive/` → Superseded by `Bronze/Archive/`, `Archive_Silver/`, `Archive_Gold/`
17. ✗ `Logs/` → Superseded by `Bronze/Logs/`, `Logs_Silver/`, `Logs_Gold/`
18. ✗ `Approvals/` → Superseded by `Bronze/Approvals/`, `Approvals_Silver/`, `Approvals_Gold/`
19. ✗ `Planning/` → Superseded by `Bronze/Planning/`, `Planning_Silver/`, `Planning_Gold/`
20. ✗ `Needs_Action/` → Superseded by `Bronze/Needs_Action/`, `Needs_Action_Silver/`, `Needs_Action_Gold/`
21. ✗ `Working/` → Superseded by `Bronze/Working/`, `Working_Silver/`, `Working_Gold/`
22. ✗ `Outputs/` → Superseded by `Bronze/Outputs/`, `Outputs_Silver/`, `Outputs_Gold/`
23. ✗ `Done/` (obsolete old directory)
24. ✗ `Approved/` (obsolete old directory)

**Total Items to Remove**: 24 files/directories

---

## Files to KEEP (Critical - Do Not Remove)

✓ `.git/` - Version control (CRITICAL)
✓ `.gitignore` - Git configuration
✓ `.obsidian/` - Obsidian vault metadata
✓ `CONSTITUTION.md` - Core governance document
✓ `README.md` - Project documentation
✓ `Bronze/` - Bronze level directory (with all contents)
✓ `Silver/` - Silver level directory (with all contents)
✓ `Gold/` - Gold level directory (with all contents)
✓ `Approvals_Silver/`, `Approvals_Gold/` - Active approval directories
✓ `Archive_Silver/`, `Archive_Gold/` - Active archive directories
✓ `Logs_Silver/`, `Logs_Gold/` - Active log directories
✓ `Planning_Silver/`, `Planning_Gold/` - Active planning directories
✓ `Needs_Action_Silver/`, `Needs_Action_Gold/` - Active needs action directories
✓ `Working_Silver/`, `Working_Gold/` - Active working directories
✓ `Outputs_Silver/`, `Outputs_Gold/` - Active output directories

---

## Execution Plan - 5 Phases

### PHASE 1: Pre-Cleanup Analysis & Verification (5 minutes)

**Objective**: Verify Bronze/Silver/Gold structure is complete and authoritative

**Steps**:

1. **Verify Bronze Structure** (Step 1.1)
   - Check `Bronze/TASKS.md` exists and contains TASK_001-004 data
   - Check `Bronze/STATUS.md` exists
   - Check `Bronze/ERRORS.md` exists
   - Check `Bronze/Archive/` contains completed task archives
   - Check `Bronze/MCP_REGISTRY.md` exists

2. **Verify Silver Structure** (Step 1.2)
   - Check `Silver/` directory exists with TASK_101-103 data
   - Check `TASKS_Silver.md`, `ERRORS_Silver.md`, `MCP_REGISTRY_Silver.md` exist
   - Check `Archive_Silver/` contains completed archives

3. **Verify Gold Structure** (Step 1.3)
   - Check `Gold/` directory exists with TASK_201 data
   - Check `TASKS_Gold.md`, `ERRORS_Gold.md`, `MCP_REGISTRY_Gold.md` exist
   - Check `Archive_Gold/` contains TASK_201 archive

4. **Document Current State** (Step 1.4)
   - Count total files in root directory
   - List all legacy files to be removed
   - Verify no active tasks in legacy directories

**Success Criteria**:
- ✓ Bronze/Silver/Gold structures validated
- ✓ All data confirmed present in level-specific locations
- ✓ No active work in legacy directories

---

### PHASE 2: Complete Backup (3 minutes)

**Objective**: Create comprehensive backup before any deletion

**Steps**:

1. **Create Backup Directory** (Step 2.1)
   ```bash
   mkdir -p "Archive_Gold/System_Cleanup_Backup/$(date +%Y%m%d_%H%M%S)"
   ```

2. **Backup Legacy Files** (Step 2.2)
   - Copy all 15 legacy .md files to backup directory
   - Preserve original timestamps
   - Create backup manifest listing all files

3. **Backup Legacy Directories** (Step 2.3)
   - Copy entire `Archive/`, `Logs/`, `Approvals/` directories
   - Copy `Planning/`, `Needs_Action/`, `Working/`, `Outputs/`
   - Copy `Done/`, `Approved/` directories
   - Preserve directory structure

4. **Create Backup Manifest** (Step 2.4)
   - List all backed-up files with sizes
   - Include MD5 checksums for verification
   - Document backup location and timestamp

**Success Criteria**:
- ✓ All 24 items backed up completely
- ✓ Backup manifest created
- ✓ Backup verified (checksums match)

---

### PHASE 3: Validation (5 minutes)

**Objective**: Confirm Bronze/Silver/Gold files contain all data before deletion

**Steps**:

1. **Compare TASKS Files** (Step 3.1)
   - Compare `TASKS.md` vs `Bronze/TASKS.md`
   - Confirm Bronze version contains all TASK_001-004 data
   - Check for any discrepancies

2. **Compare STATUS Files** (Step 3.2)
   - Check if root `STATUS.md` exists
   - If exists, compare vs `Bronze/STATUS.md`
   - Verify Bronze version is current

3. **Compare ERRORS Files** (Step 3.3)
   - Compare `ERRORS.md` vs `Bronze/ERRORS.md`
   - Confirm Bronze version contains ERROR_001, ERROR_002
   - Check for missing error entries

4. **Validate Archive Contents** (Step 3.4)
   - Compare `Archive/` vs `Bronze/Archive/`
   - Confirm all completed task archives present in Bronze
   - Check for any unique content in legacy Archive/

5. **Validate Level-Specific Files** (Step 3.5)
   - Verify `TASKS_Silver.md` data exists in Silver/
   - Verify `TASKS_Gold.md` data exists in Gold/
   - Verify all level-specific files have authoritative copies

6. **Create Validation Report** (Step 3.6)
   - Document comparison results
   - List any discrepancies found (expected: none)
   - Confirm safe to proceed with deletion

**Success Criteria**:
- ✓ All data confirmed present in Bronze/Silver/Gold
- ✓ No unique data found in legacy files
- ✓ Validation report shows 100% match
- ✓ Safe to proceed signal

---

### PHASE 4: Cleanup Execution (5 minutes)

**Objective**: Remove legacy files using proper git procedures

**Steps**:

1. **Remove Legacy Core Files** (Step 4.1)
   ```bash
   git rm TASKS.md ERRORS.md MCP_REGISTRY.md
   git rm TASKS_Silver.md TASKS_Gold.md
   git rm ERRORS_Silver.md ERRORS_Gold.md
   git rm MCP_REGISTRY_Silver.md MCP_REGISTRY_Gold.md
   git rm DASHBOARD_Silver.md DASHBOARD_Gold.md
   ```

2. **Remove Legacy Empty Files** (Step 4.2)
   ```bash
   git rm 2026-01-14.md Company_Handbook.md Dashboard.md
   ```
   (Remove STATUS.md if it exists)

3. **Remove Legacy Directories** (Step 4.3)
   ```bash
   git rm -r Archive/ Logs/ Approvals/
   git rm -r Planning/ Needs_Action/ Working/ Outputs/
   git rm -r Done/ Approved/
   ```

4. **Verify Removal** (Step 4.4)
   ```bash
   git status
   ```
   - Confirm all 24 items staged for deletion
   - Verify no unintended files staged
   - Check working directory clean

5. **Create Cleanup Summary** (Step 4.5)
   - List all removed files/directories
   - Document removal timestamp
   - Prepare for documentation phase

**Success Criteria**:
- ✓ All 24 legacy items removed
- ✓ Git history preserved (using git rm)
- ✓ No unintended deletions
- ✓ Working directory clean

---

### PHASE 5: Post-Cleanup Documentation & Commit (5-7 minutes)

**Objective**: Document cleanup, update references, commit changes

**Steps**:

1. **Update README.md** (Step 5.1)
   - Remove references to legacy file locations
   - Update directory structure documentation
   - Add multi-level architecture explanation
   - Document single source of truth principle

2. **Create ARCHITECTURE.md** (Step 5.2)
   - Document Bronze/Silver/Gold structure
   - Explain task ID ranges (001-100, 101-200, 201-300)
   - Document level progression criteria
   - Include directory structure diagram

3. **Update DASHBOARD Files** (Step 5.3)
   - Update `DASHBOARD_Gold.md` if needed
   - Reflect cleanup completion
   - Update metrics if applicable

4. **Create Completion Summary** (Step 5.4)
   - Create `Logs_Gold/Completions/TASK_202_COMPLETION.md`
   - Document all phases completed
   - List all removed items
   - Reference backup location
   - Include validation results

5. **Git Commit** (Step 5.5)
   ```bash
   git commit -m "Gold Level: TASK_202 - System Cleanup (Remove Legacy Files)

   Implements CRITICAL Action #1 from TASK_201 multi-agent assessment.

   Removed 24 legacy files/directories from root:
   - 12 legacy governance files (TASKS.md, ERRORS.md, etc.)
   - 3 empty placeholder files
   - 9 legacy directories (Archive/, Logs/, etc.)

   Established single source of truth architecture:
   - Bronze/ for TASK_001-100
   - Silver/ for TASK_101-200
   - Gold/ for TASK_201-300

   All legacy data backed up to Archive_Gold/System_Cleanup_Backup/
   All legacy data validated against Bronze/Silver/Gold before removal.
   Git history preserved via git rm (files recoverable if needed).

   Technical debt reduction: 65/100 → 75/100 (estimated)
   Maintainability improvement: Eliminated file ambiguity

   Duration: ~20 minutes
   Gold-level demonstration: System improvement, risk management, impact analysis

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   ```

6. **Push to GitHub** (Step 5.6)
   ```bash
   git push origin main
   ```

7. **Update Task Tracking** (Step 5.7)
   - Update `TASKS_Gold.md`: TASK_202 status = COMPLETED
   - Update `STATUS_Gold.md`: System State = IDLE
   - Update `DASHBOARD_Gold.md`: Add TASK_202 completion

**Success Criteria**:
- ✓ README.md updated
- ✓ ARCHITECTURE.md created
- ✓ Completion report generated
- ✓ Git commit successful
- ✓ Pushed to GitHub
- ✓ Task tracking updated

---

## Risk Assessment & Mitigation

### Risk #1: Accidental Deletion of Active Files
**Severity**: HIGH
**Probability**: LOW
**Mitigation**:
- Complete backup before any deletion (Phase 2)
- Explicit validation that Bronze/Silver/Gold are authoritative (Phase 3)
- Manual review of git status before commit (Phase 4.4)
**Rollback**: Restore from backup within 2 minutes (see Rollback Procedure)

### Risk #2: Data Loss from Unvalidated Deletion
**Severity**: HIGH
**Probability**: VERY LOW
**Mitigation**:
- Comprehensive validation comparing legacy vs current (Phase 3)
- Validation report must show 100% match before proceeding
- Backup preserved for 90+ days
**Rollback**: Git reset or restore from backup

### Risk #3: Breaking Existing Workflows or Scripts
**Severity**: MEDIUM
**Probability**: LOW
**Mitigation**:
- File-based system with no known external scripts
- Bronze/Silver/Gold structure already operational
- Documentation update to reflect new paths
**Impact**: Minimal (no scripts identified in codebase)

### Risk #4: Git History Corruption
**Severity**: LOW
**Probability**: VERY LOW
**Mitigation**:
- Use `git rm` not manual delete (preserves history)
- Verify git status before commit
- Test commit message formatting
**Benefit**: History preserved, files recoverable if needed

### Risk #5: Incomplete Cleanup
**Severity**: LOW
**Probability**: LOW
**Mitigation**:
- Explicit checklist of all 24 items
- Post-cleanup verification (Phase 5)
- Manual inspection of root directory
**Recovery**: Run cleanup again for missed items

---

## Rollback Procedures

### Immediate Rollback (< 2 minutes)
If issues discovered immediately after commit:
```bash
git reset --hard HEAD~1
```
This reverts the commit and restores all deleted files.

### Restore from Backup (< 5 minutes)
If rollback needed after additional commits:
```bash
cd "C:\Users\Lab One\AI_Employee_vault"
cp -r Archive_Gold/System_Cleanup_Backup/20260126_* .
git add .
git commit -m "Rollback: Restore legacy files from backup"
```

### Verification After Rollback
1. Verify TASKS.md exists
2. Verify STATUS.md exists (if previously existed)
3. Verify ERRORS.md exists
4. Verify all legacy directories restored
5. Confirm system operational

---

## Success Metrics

### Quantitative Metrics
- 24 legacy files/directories removed ✓
- Root directory reduced by 20-30% items ✓
- Single source of truth established (3 levels) ✓
- Technical debt score improvement: 65 → 75 (estimated) ✓
- Zero data loss ✓
- Execution time: 15-25 minutes ✓

### Qualitative Metrics
- Eliminated file ambiguity ✓
- Improved system maintainability ✓
- Reduced cognitive load for operators ✓
- Cleaner repository structure ✓
- Foundation for future improvements ✓

---

## Post-Cleanup Verification Checklist

**Root Directory Cleanliness**:
- [ ] No legacy TASKS.md, STATUS.md, ERRORS.md
- [ ] No legacy TASKS_Silver.md, TASKS_Gold.md
- [ ] No legacy ERRORS_Silver.md, ERRORS_Gold.md
- [ ] No legacy MCP_REGISTRY*.md
- [ ] No legacy DASHBOARD*.md
- [ ] No legacy Archive/, Logs/, Approvals/
- [ ] No legacy Planning/, Needs_Action/, Working/, Outputs/
- [ ] No legacy Done/, Approved/
- [ ] No empty placeholder files

**Bronze/Silver/Gold Integrity**:
- [ ] Bronze/ directory intact with all TASK_001-004 data
- [ ] Silver/ directory intact with all TASK_101-103 data
- [ ] Gold/ directory intact with all TASK_201-202 data
- [ ] All level-specific subdirectories operational

**System Operational**:
- [ ] Git status clean (no unintended changes)
- [ ] Git history preserved
- [ ] TASKS_Gold.md shows TASK_202 COMPLETED
- [ ] STATUS_Gold.md shows IDLE
- [ ] README.md updated
- [ ] ARCHITECTURE.md created

**Documentation**:
- [ ] Completion report generated
- [ ] Backup manifest exists
- [ ] Validation report exists
- [ ] Git commit successful
- [ ] Pushed to GitHub

---

## Gold-Level Capabilities Demonstrated

✨ **System Improvement**: Implementing multi-agent assessment findings
✨ **Risk Management**: Complete backup, validation, rollback procedures
✨ **Impact Analysis**: System-wide structural change management
✨ **Production Safety**: Zero data loss, complete audit trail
✨ **Documentation Excellence**: README, ARCHITECTURE.md updates
✨ **Technical Debt Reduction**: CRITICAL issue resolution (Action #1)

---

## Dependencies

**Requires**:
- ✓ TASK_201 assessment completed
- ✓ Bronze/Silver/Gold structure validated
- ✓ No active tasks in legacy directories
- ✓ Git repository in clean state

**Blocks**:
- Future system improvements (cleaner foundation)
- TASK_203+ (cleaner baseline for continued Gold demonstrations)

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Pre-Cleanup Analysis | 5 min | 5 min |
| Phase 2: Backup | 3 min | 8 min |
| Phase 3: Validation | 5 min | 13 min |
| Phase 4: Cleanup Execution | 5 min | 18 min |
| Phase 5: Documentation & Commit | 5-7 min | 23-25 min |

**Total Estimated Duration**: 23-25 minutes
**Buffer**: 0 minutes (efficient Gold execution)
**Target Completion**: 25 minutes maximum

---

## Approval Request

**This task requires approval to proceed due to:**
1. Destructive file operations (deletion of 24 items)
2. System-wide structural changes
3. Git history modifications (via git rm)
4. Potential workflow impact

**Approval Timeout**: 4 hours (Gold-level extended window)

**Upon Approval**:
1. Transition TASK_202 to IN_PROGRESS state
2. Create `Working_Gold/TASK_202/` directory
3. Begin Phase 1 execution
4. Log all phases to execution log
5. Update STATUS_Gold.md with real-time progress

**If Rejected**:
1. Document rejection reason
2. Create alternative approach if feedback provided
3. Archive task specification
4. Update task status to appropriate state

---

## Notes

- This task is **shorter than typical Gold tasks** (15-25 min vs 30-60 min) but demonstrates full Gold-level rigor
- Focus is on **quality of execution** rather than duration
- Demonstrates ability to implement findings from multi-agent coordination (TASK_201)
- Establishes cleaner foundation for future Gold demonstrations

---

**Plan Status**: AWAITING_APPROVAL
**Created By**: AI_Employee
**Plan Version**: 1.0
**Last Updated**: 2026-01-26 21:52:00
