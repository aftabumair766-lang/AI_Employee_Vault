# TASK_004: Demonstrate FAILED State Handling

**Created**: 2026-01-14 02:32:58
**Priority**: HIGH (Critical failure demonstration)
**Type**: Demonstration

## Objective

Demonstrate the FAILED state in the AI Employee Vault workflow system, validating proper handling of critical, non-recoverable errors.

## Description

This task will showcase:
1. **PLANNING state**: Create plan acknowledging intentional failure
2. **IN_PROGRESS state**: Begin execution
3. **Critical Failure**: Encounter unrecoverable error
4. **FAILED state**: Proper failure handling, logging, and archival

## State Transitions to Demonstrate

```
NEEDS_ACTION → PLANNING → IN_PROGRESS → FAILED
```

## Intentional Failure Scenario

**Failure Type**: Critical validation failure (unrecoverable)
**Trigger**: Simulated data corruption during execution
**Expected Outcome**: Task transitions to FAILED state with complete failure report

## Success Criteria

- [ ] Task transitions through PLANNING state
- [ ] Plan explicitly mentions intentional failure
- [ ] Task begins execution in IN_PROGRESS
- [ ] Critical error encountered (simulated)
- [ ] Error logged in ERRORS.md with CRITICAL severity
- [ ] Task transitions to FAILED state
- [ ] Failure report created in Logs/Failures/
- [ ] All materials archived to Archive/Failed/TASK_004/
- [ ] System returns to IDLE state
- [ ] Complete audit trail maintained

## Deliverable

None (task fails before completion) - Failure report serves as documentation

---

**Status**: NEEDS_ACTION
**Next Step**: Transition to PLANNING state and create failure plan
**WARNING**: This task is designed to fail intentionally for demonstration purposes
