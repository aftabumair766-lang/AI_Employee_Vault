# MCP REGISTRY - SILVER LEVEL

**Level**: Silver (Intermediate complexity workflows)
**Last Updated**: 2026-01-14

This registry documents MCP tools and native Claude Code tools authorized for Silver-level tasks.

---

## Tool Categories

### Read-Only Tools
- **READ**: Read file contents
- **GLOB**: Pattern-based file search
- **GREP**: Content search with regex
- **WebFetch**: Fetch and analyze web content (Silver+)
- **WebSearch**: Search the web for information (Silver+)

### Safe Write Tools
- **WRITE**: Create new files
- **EDIT**: Modify existing files
- **NotebookEdit**: Edit Jupyter notebooks (Silver+)

### Task Management
- **TodoWrite**: Track task progress
- **Task**: Launch specialized agents for complex operations (Silver+)
  - Explore agent: Codebase exploration
  - Plan agent: Implementation planning
  - General-purpose agent: Multi-step tasks

### System Tools
- **BASH**: Execute shell commands with enhanced capabilities

### Approval-Required Tools
- **Destructive operations**: Require AWAITING_APPROVAL state
- **External API calls**: Logged and monitored
- **Multi-agent coordination**: Tracked in execution logs

---

## Silver Level Capabilities

Silver level includes **all Bronze tools** PLUS:
- Web research and content fetching
- Agent spawning for complex task decomposition
- Jupyter notebook editing for data science workflows
- Enhanced bash operations with monitoring
- External service integrations (with approval)

---

## Authorization Matrix

| Tool | Bronze | Silver | Gold | Approval Required |
|------|--------|--------|------|-------------------|
| READ, WRITE, EDIT | ✓ | ✓ | ✓ | No |
| GLOB, GREP | ✓ | ✓ | ✓ | No |
| TodoWrite | ✓ | ✓ | ✓ | No |
| BASH (basic) | ✓ | ✓ | ✓ | No |
| WebFetch, WebSearch | - | ✓ | ✓ | No |
| Task (agents) | - | ✓ | ✓ | No |
| NotebookEdit | - | ✓ | ✓ | No |
| Destructive ops | - | ✓ | ✓ | Yes |
| External APIs | - | ✓ | ✓ | Yes (Silver) / Context (Gold) |

---

## Silver-Specific Guidelines

1. **Web Operations**: All web fetches and searches must be logged
2. **Agent Spawning**: Maximum 3 concurrent agents for Silver tasks
3. **External Integrations**: Require approval unless explicitly whitelisted
4. **Data Modifications**: Tracked with complete audit trail
5. **Error Handling**: Enhanced recovery protocols expected

---

## Task ID Range

Silver-level tasks: TASK_101 - TASK_200
Silver-level errors: ERROR_101 - ERROR_200

---

**Note**: For complete tool specifications, see root-level MCP_REGISTRY.md
