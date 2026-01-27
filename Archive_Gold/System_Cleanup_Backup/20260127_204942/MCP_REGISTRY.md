# MCP REGISTRY

**Version**: 1.0
**Last Updated**: 2026-01-13

---

## FILE_READ

**Purpose**: Read file contents from filesystem

**Allowed Conditions**:
- Any task state
- No approval required

**Required Approval State**: NONE

**Inputs**:
- `file_path` (string, required): Absolute path to file
- `offset` (integer, optional): Line number to start reading
- `limit` (integer, optional): Number of lines to read

**Outputs**:
- File contents with line numbers
- Error if file not found or permission denied

---

## FILE_WRITE

**Purpose**: Write or overwrite file contents

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Target location: Within Working/TASK_{ID}/ OR approved deliverable path
- No secrets in content

**Required Approval State**: NONE (within workspace), AWAITING_APPROVAL (outside workspace)

**Inputs**:
- `file_path` (string, required): Absolute path to file
- `content` (string, required): File contents to write

**Outputs**:
- Success confirmation with file path
- Error if permission denied or path invalid

---

## FILE_EDIT

**Purpose**: Replace exact string in existing file

**Allowed Conditions**:
- Task state: IN_PROGRESS
- File must be read first in current session
- old_string must be unique in file

**Required Approval State**: NONE

**Inputs**:
- `file_path` (string, required): Absolute path to file
- `old_string` (string, required): Exact text to replace
- `new_string` (string, required): Replacement text
- `replace_all` (boolean, optional): Replace all occurrences

**Outputs**:
- Success confirmation with changes applied
- Error if old_string not found or not unique

---

## FILE_DELETE

**Purpose**: Delete file from filesystem

**Allowed Conditions**:
- Task state: AWAITING_APPROVAL
- Explicit human approval obtained
- File not in protected paths

**Required Approval State**: AWAITING_APPROVAL

**Inputs**:
- `file_path` (string, required): Absolute path to file

**Outputs**:
- Success confirmation
- Error if file not found or permission denied

---

## DIRECTORY_CREATE

**Purpose**: Create new directory

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Parent directory exists

**Required Approval State**: NONE

**Inputs**:
- `directory_path` (string, required): Absolute path to directory

**Outputs**:
- Success confirmation with directory path
- Error if parent not found or permission denied

---

## DIRECTORY_LIST

**Purpose**: List contents of directory

**Allowed Conditions**:
- Any task state
- No approval required

**Required Approval State**: NONE

**Inputs**:
- `directory_path` (string, required): Absolute path to directory
- `recursive` (boolean, optional): Include subdirectories

**Outputs**:
- List of files and directories
- Error if directory not found or permission denied

---

## DIRECTORY_DELETE

**Purpose**: Delete directory and contents

**Allowed Conditions**:
- Task state: AWAITING_APPROVAL
- Explicit human approval obtained
- Directory not in protected paths
- Backup created if non-empty

**Required Approval State**: AWAITING_APPROVAL

**Inputs**:
- `directory_path` (string, required): Absolute path to directory
- `recursive` (boolean, required): Delete contents recursively

**Outputs**:
- Success confirmation
- Error if directory not found or permission denied

---

## BASH_EXECUTE

**Purpose**: Execute shell command

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Non-destructive commands: no approval
- Destructive commands: requires approval
- No interactive commands

**Required Approval State**: CONDITIONAL (destructive operations only)

**Inputs**:
- `command` (string, required): Shell command to execute
- `timeout` (integer, optional): Timeout in milliseconds
- `working_directory` (string, optional): Working directory path

**Outputs**:
- stdout content
- stderr content
- exit code
- Error if timeout or execution failure

---

## GLOB_SEARCH

**Purpose**: Search files by pattern matching

**Allowed Conditions**:
- Any task state
- No approval required

**Required Approval State**: NONE

**Inputs**:
- `pattern` (string, required): Glob pattern (e.g., "**/*.js")
- `path` (string, optional): Directory to search in

**Outputs**:
- List of matching file paths sorted by modification time
- Error if path invalid

---

## GREP_SEARCH

**Purpose**: Search file contents with regex

**Allowed Conditions**:
- Any task state
- No approval required

**Required Approval State**: NONE

**Inputs**:
- `pattern` (string, required): Regex pattern to search
- `path` (string, optional): File or directory to search
- `glob` (string, optional): File filter pattern
- `output_mode` (string, optional): "content" | "files_with_matches" | "count"
- `case_insensitive` (boolean, optional): Ignore case

**Outputs**:
- Matching lines with file paths and line numbers OR file paths only OR count
- Error if pattern invalid

---

## GIT_STATUS

**Purpose**: Show working tree status

**Allowed Conditions**:
- Any task state
- Repository must exist

**Required Approval State**: NONE

**Inputs**:
- `repository_path` (string, optional): Path to git repository

**Outputs**:
- Staged changes
- Unstaged changes
- Untracked files
- Branch information

---

## GIT_DIFF

**Purpose**: Show changes in working tree

**Allowed Conditions**:
- Any task state
- Repository must exist

**Required Approval State**: NONE

**Inputs**:
- `repository_path` (string, optional): Path to git repository
- `staged` (boolean, optional): Show staged changes only

**Outputs**:
- Diff output with file changes
- Error if repository not found

---

## GIT_ADD

**Purpose**: Stage files for commit

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Files exist and are not secrets

**Required Approval State**: NONE

**Inputs**:
- `file_paths` (array[string], required): Paths to files to stage
- `repository_path` (string, optional): Path to git repository

**Outputs**:
- Success confirmation with staged files
- Error if files not found

---

## GIT_COMMIT

**Purpose**: Create git commit

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Changes staged
- Commit message follows conventions

**Required Approval State**: NONE

**Inputs**:
- `message` (string, required): Commit message
- `repository_path` (string, optional): Path to git repository

**Outputs**:
- Commit hash
- Files committed
- Error if nothing staged or hook failure

---

## GIT_PUSH

**Purpose**: Push commits to remote repository

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Commits exist locally
- Not force push to protected branches

**Required Approval State**: CONDITIONAL (protected branches require approval)

**Inputs**:
- `remote` (string, optional): Remote name (default: origin)
- `branch` (string, optional): Branch name
- `force` (boolean, optional): Force push flag
- `repository_path` (string, optional): Path to git repository

**Outputs**:
- Push confirmation
- Error if rejected or network failure

---

## HTTP_REQUEST

**Purpose**: Make HTTP request to external API

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Endpoint approved in task plan
- Rate limits respected

**Required Approval State**: AWAITING_APPROVAL (first-time endpoint)

**Inputs**:
- `url` (string, required): Target URL
- `method` (string, required): HTTP method (GET, POST, PUT, DELETE)
- `headers` (object, optional): Request headers
- `body` (string, optional): Request body
- `timeout` (integer, optional): Timeout in milliseconds

**Outputs**:
- Response status code
- Response headers
- Response body
- Error if timeout or network failure

---

## DATABASE_QUERY

**Purpose**: Execute database query

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Connection approved in plan
- SELECT queries: no approval
- INSERT/UPDATE: standard approval
- DELETE/DROP: awaiting approval

**Required Approval State**: CONDITIONAL (based on operation type)

**Inputs**:
- `connection_string` (string, required): Database connection string
- `query` (string, required): SQL query
- `parameters` (array, optional): Query parameters

**Outputs**:
- Query results (rows)
- Rows affected count
- Error if query fails or connection error

---

## TEST_EXECUTE

**Purpose**: Run test suite

**Allowed Conditions**:
- Any task state
- Test framework configured

**Required Approval State**: NONE

**Inputs**:
- `test_path` (string, optional): Path to test file or directory
- `framework` (string, optional): Test framework name
- `coverage` (boolean, optional): Generate coverage report

**Outputs**:
- Test results (passed/failed/skipped)
- Coverage percentage
- Error details for failed tests

---

## BUILD_EXECUTE

**Purpose**: Execute build process

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Build configuration exists

**Required Approval State**: NONE

**Inputs**:
- `build_command` (string, optional): Build command override
- `target` (string, optional): Build target

**Outputs**:
- Build success/failure status
- Build artifacts location
- Compilation errors/warnings

---

## PACKAGE_INSTALL

**Purpose**: Install package dependencies

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Package approved in plan OR in package.json/requirements.txt

**Required Approval State**: CONDITIONAL (new packages require approval)

**Inputs**:
- `package_name` (string, required): Package to install
- `version` (string, optional): Package version
- `package_manager` (string, optional): npm, yarn, pip, etc.

**Outputs**:
- Installation success confirmation
- Installed version
- Error if package not found or conflict

---

## LOG_WRITE

**Purpose**: Write entry to execution log

**Allowed Conditions**:
- Any task state
- Always allowed

**Required Approval State**: NONE

**Inputs**:
- `level` (string, required): DEBUG | INFO | WARN | ERROR | CRITICAL
- `message` (string, required): Log message
- `context` (object, optional): Additional context data

**Outputs**:
- Log entry written confirmation
- Timestamp of log entry

---

## APPROVAL_REQUEST

**Purpose**: Request human approval

**Allowed Conditions**:
- Any task state
- Valid approval request structure

**Required Approval State**: N/A (this creates approval state)

**Inputs**:
- `request_type` (string, required): pre_execution | checkpoint | destructive_operation
- `description` (string, required): Human-readable explanation
- `details` (object, required): Operation details
- `rationale` (string, required): Why approval needed
- `timeout` (integer, required): Timeout in seconds
- `priority` (string, required): low | medium | high | critical

**Outputs**:
- Approval request ID
- Status: pending
- Timeout timestamp

---

## APPROVAL_CHECK

**Purpose**: Check status of approval request

**Allowed Conditions**:
- Any task state
- Approval request exists

**Required Approval State**: NONE

**Inputs**:
- `approval_id` (string, required): Approval request ID

**Outputs**:
- Status: pending | granted | rejected | expired
- Approver name (if granted/rejected)
- Approval timestamp (if granted/rejected)
- Rejection reason (if rejected)

---

## CHECKPOINT_CREATE

**Purpose**: Create recovery checkpoint

**Allowed Conditions**:
- Task state: IN_PROGRESS
- Before risky operations

**Required Approval State**: NONE

**Inputs**:
- `checkpoint_name` (string, required): Checkpoint identifier
- `state_data` (object, required): Current state to save

**Outputs**:
- Checkpoint ID
- Checkpoint timestamp
- Checkpoint location

---

## CHECKPOINT_RESTORE

**Purpose**: Restore from checkpoint

**Allowed Conditions**:
- Task state: BLOCKED or IN_PROGRESS
- Checkpoint exists

**Required Approval State**: NONE

**Inputs**:
- `checkpoint_id` (string, required): Checkpoint to restore

**Outputs**:
- Restored state data
- Restoration timestamp
- Error if checkpoint not found

---

## WEB_FETCH

**Purpose**: Fetch and process web content

**Allowed Conditions**:
- Any task state
- URL is valid and accessible

**Required Approval State**: NONE (read-only operation)

**Inputs**:
- `url` (string, required): URL to fetch
- `prompt` (string, required): What information to extract

**Outputs**:
- Processed content based on prompt
- Error if URL unreachable or invalid

---

## WEB_SEARCH

**Purpose**: Search web for information

**Allowed Conditions**:
- Any task state
- Query is valid

**Required Approval State**: NONE

**Inputs**:
- `query` (string, required): Search query
- `allowed_domains` (array[string], optional): Domain filter
- `blocked_domains` (array[string], optional): Domains to exclude

**Outputs**:
- Search results with URLs
- Result snippets
- Error if search fails

---

## TASK_SPAWN

**Purpose**: Launch specialized sub-agent for complex task

**Allowed Conditions**:
- Any task state
- Sub-task within scope

**Required Approval State**: NONE

**Inputs**:
- `subagent_type` (string, required): Agent type to spawn
- `prompt` (string, required): Task for agent
- `model` (string, optional): Model to use

**Outputs**:
- Sub-agent final report
- Sub-agent task completion status
- Error if agent fails

---

## NOTIFICATION_SEND

**Purpose**: Send notification to human operator

**Allowed Conditions**:
- Any task state
- For errors, blockers, or status updates

**Required Approval State**: NONE

**Inputs**:
- `priority` (string, required): low | medium | high | critical
- `subject` (string, required): Notification subject
- `message` (string, required): Notification content
- `channels` (array[string], optional): Notification channels

**Outputs**:
- Notification sent confirmation
- Delivery timestamp
- Error if delivery fails

---

*This registry is normative. All MCP tool usage must comply with specified conditions and approval requirements per CONSTITUTION.md and TASK_IMPLEMENTATION_SPEC.md.*
