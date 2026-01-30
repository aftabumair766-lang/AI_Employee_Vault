"""
Factory functions for creating test data
TASK_205 - Testing Infrastructure Foundation
"""
from pathlib import Path
from datetime import datetime


def create_test_task(
    task_id='TASK_999',
    description='Test task',
    level='Gold',
    priority='MEDIUM',
    state='NEEDS_ACTION',
    **kwargs
):
    """
    Create test task specification

    Args:
        task_id: Task ID (default: TASK_999)
        description: Task description
        level: Task level (Bronze, Silver, Gold)
        priority: Task priority (LOW, MEDIUM, HIGH, CRITICAL)
        state: Task state
        **kwargs: Additional fields to include

    Returns:
        dict: Task specification
    """
    task = {
        'task_id': task_id,
        'description': description,
        'level': level,
        'priority': priority,
        'state': state,
    }

    # Add any additional fields
    task.update(kwargs)

    return task


def create_test_file(directory, filename, content=""):
    """
    Create test file

    Args:
        directory: Directory path (str or Path)
        filename: Filename
        content: File content

    Returns:
        Path: Path to created file
    """
    dir_path = Path(directory) if isinstance(directory, str) else directory
    file_path = dir_path / filename

    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write content
    file_path.write_text(content, encoding='utf-8')

    return file_path


def create_test_directory(base_path, dirname):
    """
    Create test directory

    Args:
        base_path: Base directory path
        dirname: Directory name

    Returns:
        Path: Path to created directory
    """
    base = Path(base_path) if isinstance(base_path, str) else base_path
    dir_path = base / dirname
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def create_task_directory_structure(vault_root, task_id, level='Gold'):
    """
    Create complete task directory structure

    Args:
        vault_root: Vault root directory
        task_id: Task ID
        level: Task level

    Returns:
        dict: Paths to created directories
    """
    vault = Path(vault_root) if isinstance(vault_root, str) else vault_root

    # Create directory structure
    working_dir = vault / f'Working_{level}' / task_id
    workspace_dir = working_dir / 'workspace'
    temp_dir = working_dir / 'temp'
    outputs_dir = working_dir / 'outputs'

    for dir_path in [working_dir, workspace_dir, temp_dir, outputs_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    return {
        'working': working_dir,
        'workspace': workspace_dir,
        'temp': temp_dir,
        'outputs': outputs_dir
    }


def generate_iso_timestamp():
    """
    Generate ISO 8601 timestamp with milliseconds

    Returns:
        str: Timestamp in format YYYY-MM-DD HH:MM:SS.mmm
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def create_execution_log_entry(task_id, state, level, message):
    """
    Create execution log entry

    Args:
        task_id: Task ID
        state: Task state
        level: Log level (INFO, WARN, ERROR)
        message: Log message

    Returns:
        str: Formatted log entry
    """
    timestamp = generate_iso_timestamp()
    return f"[{timestamp}] [{state}] [{level}] {message}"


def create_tasks_md_content(tasks):
    """
    Create TASKS.md file content

    Args:
        tasks: List of task dictionaries

    Returns:
        str: TASKS.md content
    """
    content = "# TASK TRACKING LEDGER - GOLD LEVEL\n\n"
    content += f"**Last Updated**: {generate_iso_timestamp()}\n\n"
    content += "## Active Tasks\n\n"
    content += "| Task ID | Description | Status | Started | Last Updated | Assigned To |\n"
    content += "|---------|-------------|--------|---------|--------------|-------------|\n"

    for task in tasks:
        if task['state'] not in ['DONE', 'FAILED']:
            content += f"| {task['task_id']} | {task['description']} | "
            content += f"{task['state']} | {task.get('started', '-')} | "
            content += f"{task.get('updated', generate_iso_timestamp())} | AI_Employee |\n"

    content += "\n## Completed Tasks\n\n"
    content += "| Task ID | Description | Status | Started | Completed | Duration |\n"
    content += "|---------|-------------|--------|---------|-----------|----------|\n"

    for task in tasks:
        if task['state'] in ['DONE']:
            content += f"| {task['task_id']} | {task['description']} | "
            content += f"{task['state']} | {task.get('started', '-')} | "
            content += f"{task.get('completed', '-')} | {task.get('duration', '-')} |\n"

    return content


def create_status_md_content(system_state='IDLE', current_activity=''):
    """
    Create STATUS.md file content

    Args:
        system_state: System state (IDLE, WORKING, etc.)
        current_activity: Description of current activity

    Returns:
        str: STATUS.md content
    """
    content = "# SYSTEM STATUS - GOLD LEVEL\n\n"
    content += f"**Last Updated**: {generate_iso_timestamp()}\n"
    content += f"**System State**: {system_state}\n\n"
    content += "## Current Activity\n\n"
    content += current_activity or "System is IDLE."
    content += "\n"
    return content


def create_sample_vault_structure(vault_root, level='Gold'):
    """
    Create sample vault structure for testing

    Args:
        vault_root: Vault root directory
        level: Level (Bronze, Silver, Gold)

    Returns:
        dict: Paths to created files and directories
    """
    vault = Path(vault_root) if isinstance(vault_root, str) else vault_root

    # Create directories
    working_dir = vault / f'Working_{level}'
    archive_dir = vault / f'Archive_{level}' / 'Completed'
    logs_dir = vault / f'Logs_{level}' / 'Executions'
    planning_dir = vault / f'Planning_{level}' / 'Active'
    approvals_dir = vault / f'Approvals_{level}' / 'Granted'
    outputs_dir = vault / f'Outputs_{level}'

    for dir_path in [working_dir, archive_dir, logs_dir, planning_dir, approvals_dir, outputs_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Create tracking files
    tasks_file = vault / f'TASKS_{level}.md'
    status_file = vault / f'STATUS_{level}.md'
    errors_file = vault / f'ERRORS_{level}.md'

    tasks_file.write_text(create_tasks_md_content([]))
    status_file.write_text(create_status_md_content())
    errors_file.write_text(f"# ERROR LOG - {level.upper()} LEVEL\n\n(No errors)\n")

    return {
        'vault_root': vault,
        'working': working_dir,
        'archive': archive_dir,
        'logs': logs_dir,
        'planning': planning_dir,
        'approvals': approvals_dir,
        'outputs': outputs_dir,
        'tasks_file': tasks_file,
        'status_file': status_file,
        'errors_file': errors_file,
    }
