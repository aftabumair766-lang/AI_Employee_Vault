# TASK_202: System Cleanup - Remove Legacy Root-Level Files

**Task ID**: TASK_202
**Level**: Gold (System Improvement)
**Created**: 2026-01-26 21:48:04
**Priority**: CRITICAL
**Type**: Technical Debt Remediation (Gold Level)

---

## Objective

Remove legacy root-level files identified as CRITICAL technical debt in TASK_201 assessment, eliminating ambiguity about authoritative data sources and improving system maintainability.

**This task demonstrates Gold-level capabilities:**
- **System improvement** based on multi-agent assessment findings
- **Risk management** with backup and validation procedures
- **Impact analysis** across entire system
- **Rollback planning** for production safety
- **Documentation updates** to reflect cleanup

**Direct Application**: Implements Action #1 from TASK_201 executive report

---

## Background & Context

### From TASK_201 Assessment (Agent A - Architecture Analysis)

**DEBT #1: Legacy Root-Level Files (CRITICAL)**

**Issue**: Dual file structure creates ambiguity
```
Root level:
- TASKS.md (legacy Bronze?)
- TASKS_Silver.md (active Silver)
- TASKS_Gold.md (active Gold)
- STATUS.md (legacy)
- STATUS_Silver.md (active Silver)
- STATUS_Gold.md (active Gold)
- ERRORS.md (legacy)
- ERRORS_Silver.md (active Silver)
- ERRORS_Gold.md (active Gold)
- Archive/ (legacy)
- Archive_Silver/ (active Silver)
- Archive_Gold/ (active Gold)
```

**Impact**:
- Confusion about authoritative data source
- Potential for stale data
- Maintenance burden
- Risk of updating wrong file

**Recommendation**: Archive or delete legacy files within 7 days

---

## Requirements

### Files to Remove/Archive

**Core Governance Files** (3 files):
1. `TASKS.md` (legacy Bronze ledger, superseded by Bronze/TASKS_Bronze.md)
2. `STATUS.md` (legacy status file, superseded by Bronze/STATUS_Bronze.md)
3. `ERRORS.md` (legacy error log, superseded by Bronze/ERRORS_Bronze.md)

**Legacy Directories** (4 directories):
4. `Archive/` (superseded by Bronze/Archive/)
5. `Logs/` (superseded by Bronze/Logs/)
6. `Approvals/` (superseded by Bronze/Approvals/)
7. `Working/` (superseded by Bronze/Working/)

**Other Legacy Artifacts**:
8. `Needs_Action/` (superseded by Bronze/Needs_Action/)
9. `Planning/` (superseded by Bronze/Planning/)
10. `Outputs/` (superseded by Bronze/Outputs/)

### Deliverables

1. **Pre-Cleanup Backup**: Complete archive of all legacy files
2. **Validation Report**: Confirm Bronze/Silver/Gold files are authoritative
3. **Cleanup Execution**: Remove identified legacy files/directories
4. **Post-Cleanup Verification**: Confirm system integrity
5. **Documentation Update**: Update README.md and ARCHITECTURE.md

---

## Success Criteria

- [ ] All legacy files backed up to `Archive_Gold/System_Cleanup_Backup/`
- [ ] Verification confirms Bronze/Silver/Gold files contain all data
- [ ] Legacy files removed from root directory
- [ ] System state files (TASKS, STATUS) remain consistent
- [ ] Git history preserved (files removed via git rm, not deleted)
- [ ] No data loss (verified by comparing Bronze vs legacy)
- [ ] Documentation updated (README.md, new ARCHITECTURE.md)
- [ ] Rollback procedure documented
- [ ] Task duration: 15-25 minutes (shorter than typical Gold task)

---

## Acceptance Criteria

### Functional Requirements
- [ ] Root directory contains only Bronze/Silver/Gold level-specific files
- [ ] No ambiguous file references remain
- [ ] Bronze level is authoritative for TASK_001-004 data
- [ ] Silver/Gold levels retain complete data
- [ ] System can still create new tasks at all levels

### Quality Requirements
- [ ] Complete backup exists before deletion
- [ ] Validation report documents comparison results
- [ ] Git commit message explains cleanup rationale
- [ ] Documentation reflects new single-source-of-truth architecture

### Safety Requirements
- [ ] Rollback procedure tested (restore from backup)
- [ ] No active tasks interrupted
- [ ] DASHBOARD files updated to reflect cleanup

---

## Technical Approach

### Phase 1: Pre-Cleanup Analysis (5 minutes)
1. List all root-level files and directories
2. Identify legacy vs. active files
3. Check for any references to legacy files in documentation
4. Verify Bronze/ directory contains complete Bronze data

### Phase 2: Backup (3 minutes)
5. Create backup directory: `Archive_Gold/System_Cleanup_Backup/`
6. Copy all legacy files to backup with timestamps
7. Create backup manifest (list of all backed-up files)

### Phase 3: Validation (5 minutes)
8. Compare TASKS.md vs Bronze/TASKS_Bronze.md (confirm data match)
9. Compare STATUS.md vs Bronze/STATUS_Bronze.md
10. Compare ERRORS.md vs Bronze/ERRORS_Bronze.md
11. Compare Archive/ vs Bronze/Archive/
12. Document validation results

### Phase 4: Cleanup Execution (5 minutes)
13. Use `git rm` to remove legacy files (preserves history)
14. Remove legacy directories
15. Verify removal with `git status`
16. Create cleanup summary

### Phase 5: Post-Cleanup & Documentation (5-7 minutes)
17. Update README.md (remove references to legacy files)
18. Create ARCHITECTURE.md documenting structure
19. Update DASHBOARD files if needed
20. Commit changes with descriptive message
21. Push to GitHub

---

## Risk Assessment

### High-Risk Elements

**Risk #1**: Accidental deletion of active files
- **Mitigation**: Complete backup before any deletion
- **Mitigation**: Explicit validation that Bronze/ is authoritative
- **Rollback**: Restore from backup within 2 minutes

**Risk #2**: Breaking existing workflows or scripts
- **Mitigation**: Check for hardcoded paths to legacy files
- **Mitigation**: Update documentation proactively
- **Impact**: LOW (file-based system, no scripts identified)

**Risk #3**: Git history loss
- **Mitigation**: Use `git rm` not manual delete
- **Verification**: Check git log shows deletion commit
- **Benefit**: History preserved, can recover if needed

### Approval Required

This Gold-level task requires approval due to:
- System-wide structural changes
- Potential impact on existing workflows
- File deletion (even with backup)

---

## Expected Outcomes

### Quantitative
- 10+ files/directories removed
- Root directory cleaner (20-30% fewer items)
- Single source of truth established (3 levels: Bronze, Silver, Gold)
- Technical debt reduced from 65/100 to 75/100 (estimated)

### Qualitative
- Eliminated ambiguity about authoritative files
- Improved maintainability (clear structure)
- Reduced cognitive load for operators
- Foundation for future system improvements

---

## Validation Checklist

**Pre-Cleanup Validation**:
- [ ] Bronze/TASKS_Bronze.md exists and contains TASK_001-004 data
- [ ] Bronze/STATUS_Bronze.md exists and is current
- [ ] Bronze/ERRORS_Bronze.md exists and contains ERROR_001, ERROR_002
- [ ] Bronze/Archive/ contains completed task archives
- [ ] Legacy files have been stale since multi-level restructure

**Post-Cleanup Validation**:
- [ ] Root directory clean (no legacy TASKS.md, STATUS.md, ERRORS.md)
- [ ] Bronze/Silver/Gold structure intact
- [ ] Git status shows clean working tree
- [ ] README.md updated
- [ ] ARCHITECTURE.md created

---

## Rollback Procedure

If cleanup causes issues:

1. **Immediate Rollback** (< 2 minutes):
   ```bash
   git reset --hard HEAD~1
   ```

2. **Restore from Backup** (< 5 minutes):
   ```bash
   cp -r Archive_Gold/System_Cleanup_Backup/* .
   git add .
   git commit -m "Rollback: Restore legacy files from backup"
   ```

3. **Verify Restoration**:
   - Check TASKS.md exists
   - Check STATUS.md exists
   - Confirm system operational

---

## Gold Level Demonstration

**This task showcases Gold-level capabilities:**

✨ **System Improvement** - Applying multi-agent assessment findings
✨ **Risk Management** - Backup, validation, rollback procedures
✨ **Impact Analysis** - System-wide structural change
✨ **Production Safety** - No data loss, complete audit trail
✨ **Documentation Excellence** - ARCHITECTURE.md creation
✨ **Technical Debt Reduction** - CRITICAL issue resolution

---

## Workflow State Machine

```
NEEDS_ACTION (current)
    ↓
PLANNING
    ↓
AWAITING_APPROVAL (Gold requirement)
    ↓
IN_PROGRESS
    ↓
COMPLETED
    ↓
DONE
```

---

## Dependencies

**Requires**:
- TASK_201 assessment completed ✓
- Bronze/Silver/Gold structure validated ✓
- No active tasks in legacy directories ✓
- Git repository in clean state ✓

**Blocks**:
- Future system improvements (cleaner foundation)
- TASK_203+ (cleaner baseline for continued Gold demonstrations)

---

**Created By**: AI_Employee
**Assigned To**: AI_Employee
**Status**: NEEDS_ACTION
**Next Step**: Create execution plan in Planning_Gold/Active/
**Estimated Duration**: 15-25 minutes (efficient Gold task)
**Impact**: CRITICAL technical debt resolution, system improvement
