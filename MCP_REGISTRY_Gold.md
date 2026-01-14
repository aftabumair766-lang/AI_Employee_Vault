# MCP REGISTRY - GOLD LEVEL

**Level**: Gold (Advanced complexity workflows)
**Last Updated**: 2026-01-14

This registry documents MCP tools and native Claude Code tools authorized for Gold-level tasks.

---

## Tool Categories

### Read-Only Tools
- **READ**: Read file contents
- **GLOB**: Pattern-based file search
- **GREP**: Content search with regex
- **WebFetch**: Fetch and analyze web content
- **WebSearch**: Search the web for information

### Safe Write Tools
- **WRITE**: Create new files
- **EDIT**: Modify existing files
- **NotebookEdit**: Edit Jupyter notebooks

### Task Management
- **TodoWrite**: Track task progress
- **Task**: Launch specialized agents for complex operations
  - Explore agent: Deep codebase exploration
  - Plan agent: Advanced implementation planning
  - General-purpose agent: Complex multi-step tasks
  - **Multiple agent orchestration** (Gold+)

### System Tools
- **BASH**: Execute shell commands with full capabilities
- **BashOutput**: Monitor background processes (Gold+)
- **KillShell**: Terminate background processes (Gold+)

### Advanced Tools (Gold)
- **EnterPlanMode**: Enter planning mode for complex implementations
- **Skill**: Execute specialized skills (if available)
- **SlashCommand**: Custom command execution (if configured)

### Approval-Optimized Tools
- **Contextual approval**: Many operations pre-approved in Gold level
- **Performance monitoring**: KPI tracking and reporting
- **Multi-task orchestration**: Complex dependency management

---

## Gold Level Capabilities

Gold level includes **all Bronze + Silver tools** PLUS:
- Advanced agent orchestration (5+ concurrent agents)
- Background process management
- Planning mode for complex architectures
- Performance monitoring and KPIs
- Production-grade implementations
- Extended human-in-the-loop with escalation protocols
- Advanced rollback and recovery mechanisms

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
| BashOutput, KillShell | - | - | ✓ | No |
| EnterPlanMode | - | - | ✓ | No |
| Skill, SlashCommand | - | - | ✓ | Context |
| Destructive ops | - | ✓ | ✓ | Context |
| External APIs | - | ✓ | ✓ | Context |
| Multi-agent orchestration | - | Limited | ✓ | No |

---

## Gold-Specific Guidelines

1. **Agent Orchestration**: Up to 10 concurrent agents for complex tasks
2. **Production Readiness**: All implementations must include:
   - Complete error handling
   - Performance monitoring
   - Rollback procedures
   - Documentation
3. **External Integrations**: Most operations pre-approved with logging
4. **Data Operations**: Full ACID compliance where applicable
5. **Error Recovery**: Advanced multi-level recovery protocols
6. **Performance KPIs**: Track execution time, resource usage, success rates

---

## Gold Task Characteristics

- **Full Lifecycle**: Complete task lifecycle from planning to deployment
- **Multi-Task Dependencies**: Complex task graphs with dependencies
- **Extended Approval Workflows**: Multi-level approval with escalation
- **Performance Targets**: Must meet defined SLAs and KPIs
- **Production Grade**: Code quality, testing, and documentation standards

---

## Task ID Range

Gold-level tasks: TASK_201 - TASK_300
Gold-level errors: ERROR_201 - ERROR_300

---

**Note**: For complete tool specifications, see root-level MCP_REGISTRY.md
