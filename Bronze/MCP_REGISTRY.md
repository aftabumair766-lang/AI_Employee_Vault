# MCP REGISTRY - BRONZE LEVEL

**Level**: Bronze (Basic workflow demonstration)
**Last Updated**: 2026-01-14

This registry documents the MCP tools and native Claude Code tools used for Bronze-level tasks.

---

## Tool Categories

### Read-Only Tools
- **READ**: Read file contents
- **GLOB**: Pattern-based file search
- **GREP**: Content search with regex

### Safe Write Tools
- **WRITE**: Create new files
- **EDIT**: Modify existing files

### Task Management
- **TodoWrite**: Track task progress

### System Tools
- **BASH**: Execute shell commands

---

## Tools Used in Bronze Tasks

### TASK_001: Basic Workflow
- WRITE (create hello_world.txt)
- EDIT (update tracking files)
- BASH (timestamp generation)

### TASK_002: Approval Workflow
- WRITE (create approval requests)
- READ (validate approvals)
- EDIT (update tracking files)

### TASK_003: Planning & Blocker Recovery
- WRITE (create plans, error logs)
- READ (read specifications)
- EDIT (update tracking files)
- BASH (file operations)

### TASK_004: Critical Failure Handling
- WRITE (create failure reports)
- READ (validate error logs)
- EDIT (update tracking files)
- BASH (archival operations)

---

## Authorization Levels

**Bronze Level**: Basic tools only
- File operations (read/write/edit)
- Task tracking (TodoWrite)
- System commands (bash for basic operations)
- No destructive operations without approval

---

**Note**: For complete tool specifications, see root-level MCP_REGISTRY.md
