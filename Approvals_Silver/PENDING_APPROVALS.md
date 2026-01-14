# PENDING APPROVALS - SILVER LEVEL

**Level**: Silver (Intermediate complexity workflows)
**Last Updated**: 2026-01-14

---

## Current Pending Approvals

(No pending approvals)

---

## Approval Request Format

```yaml
# APPROVAL REQUEST: TASK_XXX

**Approval ID**: APPROVAL_YYYYMMDDHHMMSS_TASK_XXX
**Task ID**: TASK_XXX (Range: TASK_101-200)
**Requested**: YYYY-MM-DD HH:MM:SS
**Expires**: YYYY-MM-DD HH:MM:SS (default: 60 minutes)
**Priority**: LOW | MEDIUM | HIGH | CRITICAL

**Request Type**: [Task execution | Data modification | External API call | Agent spawning | etc.]

**Description**:
[What needs approval]

**Justification**:
[Why this action is necessary]

**Impact**:
[What will be affected]

**Risk Assessment**:
- Probability: [LOW | MEDIUM | HIGH]
- Impact: [LOW | MEDIUM | HIGH | CRITICAL]
- Mitigation: [Steps taken to reduce risk]

**Alternatives Considered**:
1. [Alternative 1]
2. [Alternative 2]

**Approval Required From**: [Human Operator | System Administrator]
```

---

**Status**: Ready for approval workflow at Silver level
