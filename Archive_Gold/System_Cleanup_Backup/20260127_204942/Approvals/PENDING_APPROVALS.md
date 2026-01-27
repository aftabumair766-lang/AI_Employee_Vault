# PENDING APPROVALS

**Last Updated**: 2026-01-14 01:55:12

No pending approval requests.

## Recently Processed

### APPROVAL_20260114015353_TASK_002
- **Task**: TASK_002
- **Status**: APPROVED
- **Requested At**: 2026-01-14 01:53:53
- **Approved At**: 2026-01-14 01:55:12
- **Approved By**: Human Operator
- **Approval Record**: Approvals/Granted/TASK_002_APPROVAL.md

---

## Approval Request Format

```yaml
approval_id: "APPROVAL_{TIMESTAMP}_{TASK_ID}"
task_id: "TASK_XXX"
requester: "AI_Employee"
request_type: "pre_execution | checkpoint | destructive_operation"
timestamp: "YYYY-MM-DDTHH:MM:SS.mmmZ"
timeout: 3600  # seconds
priority: "low | medium | high | critical"

description: "Human-readable explanation of what requires approval"

details:
  operation: "[What is being requested]"
  target: "[What is affected]"
  impact: "[Consequences]"
  reversible: [true/false]

rationale: "[Why approval is needed]"

risks:
  - "[Risk 1]"
  - "[Risk 2]"

mitigations:
  - "[Mitigation 1]"
  - "[Mitigation 2]"

alternatives_considered:
  - name: "[Alternative approach]"
    rejected_because: "[Reason]"
```
