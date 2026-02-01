# CHANGELOG

All notable changes to the AI Employee Vault project.

---

## [2.1.0] - 2026-02-01

### Added
- **TASK_211**: PyPI Package Published - `ai-employee-security-skills` v1.0.0
  - 6 security modules available globally via `pip install ai-employee-security-skills`
  - Package includes: PathValidator, ArchiveEncryption, InputValidator, IntegrityChecker, SecureLogging, ApprovalVerifier
  - MIT License, pyproject.toml build system
- **TASK_212**: Cloud Deployment on Railway.app
  - Live public URL: ai-employee-vault-production.up.railway.app
  - Auto-deploy from local, health checks passing
  - All 5 services running (path_validator, encryptor, integrity_checker, database, monitoring)

### Changed
- **main.py**: Imports now use PyPI package (`from ai_employee_security import ...`) instead of local files
- **requirements.txt**: Added `ai-employee-security-skills==1.0.0` as dependency
- **Dockerfile**: Removed skills COPY and PYTHONPATH (now installed via pip)
- **.gitignore**: Added security key protections (*.key, *.pem, secrets/, *.db)

### Security
- .gitignore blocks all key files, certificates, and database files
- API token used via environment variable (not stored in files)
- No credentials committed to version control

---

## [2.0.0] - 2026-02-01

### Added
- **TASK_206**: REST API with 15+ endpoints (FastAPI)
- **TASK_207**: SQLite database with SQLAlchemy ORM (4 tables: Tasks, SecurityLogs, Metrics, ApiKeys)
- **TASK_208**: Live web dashboard with auto-refresh (HTML/JS)
- **TASK_209**: Docker deployment (Dockerfile + docker-compose.yml)
- **TASK_210**: Monitoring system (MetricsCollector - CPU, Memory, Disk, API metrics)
- **SKILLS.md**: Comprehensive reusable skills library documentation (1200+ lines)
- **CHANGELOG.md**: This file (Constitutional compliance - Article V, Section 5.4)
- **DECISIONS.md**: Architectural decision records (Constitutional compliance - Article V, Section 5.4)
- Constitutional Compliance Audit with 11 violations identified and fixed

### Changed
- **main.py**: Upgraded from v1.0 (6 endpoints) to v2.0 (15+ endpoints)
- **requirements.txt**: Added sqlalchemy, jinja2, psutil, prometheus-client
- **README.md**: Updated with SKILLS.md reference and current progress
- **TASKS_Gold.md**: Updated with TASK_206-210 entries
- **STATUS_Gold.md**: Updated with latest activity log

### Security
- All API endpoints use existing TASK_204 security modules
- SecurityLog table records all security operations
- Input validation on all user-facing endpoints
- No credentials committed to version control

---

## [1.0.0] - 2026-02-01

### Added
- **TASK_205**: Testing Infrastructure Foundation (360 tests, CI/CD)
  - 260 unit tests, 36 integration tests, 27 E2E tests
  - GitHub Actions workflows (tests, e2e-tests, quality-gates)
  - Codecov integration, 73% average coverage
- **TASK_204**: Critical Security Hardening (8 CRITICAL vulnerabilities fixed)
  - PathValidator (CVSS 7.5), ArchiveEncryption (CVSS 8.0)
  - InputValidator (CVSS 7.0), ApprovalVerifier (CVSS 7.5)
  - IntegrityChecker (CVSS 6.5), SecureLogging (CVSS 6.0)
  - Security score: 55 → 81/100 (+47%)
- **TASK_203**: Advanced Multi-Agent Performance & Security Analysis
- **TASK_202**: System Cleanup - Legacy file removal
- **TASK_201**: Multi-Agent Code Quality Assessment

---

## [0.3.0] - 2026-01-27

### Added
- Silver Level tasks (TASK_101-103)
  - Web research & synthesis
  - Architecture analysis
  - Jupyter notebook data analysis

---

## [0.2.0] - 2026-01-15

### Added
- Bronze Level tasks (TASK_001-004)
  - Basic execution, approval workflows, planning, failure handling
  - 100% state coverage (all 8 states demonstrated)

---

## [0.1.0] - 2026-01-13

### Added
- CONSTITUTION.md - Core governance framework
- Multi-level architecture (Bronze/Silver/Gold)
- File-based workflow system
- MCP Registry configurations
