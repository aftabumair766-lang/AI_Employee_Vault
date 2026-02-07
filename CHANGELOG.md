# CHANGELOG

All notable changes to the AI Employee Vault project.

---

## [3.2.0] - 2026-02-07

### Added
- **TASK_214**: Configuration Layer + Gmail Email Integration
  - PlatinumSettings centralized config with pydantic-settings and .env support
  - EmailReader (IMAP) for Cloud Agent inbox triage
  - EmailSender (SMTP) for Local Agent email dispatch
- **TASK_215**: Social Media + WhatsApp/Banking Stubs
  - SocialDrafter (Cloud) + SocialPoster (Local, Twitter/X API)
  - WhatsApp ABC interface + stub (Local only)
  - Banking ABC interface + stub (Local only)
- **TASK_216**: Health Monitoring Daemon
  - HealthMonitor with API, Odoo, Cloud VM, and heartbeat checks
  - Standalone daemon with signal handling
  - GET /api/v1/platinum/health endpoint
- **TASK_217**: Odoo Community Integration
  - OdooClient with XML-RPC (draft invoices/payments)
  - Cloud: create_draft_invoice, create_draft_payment (draft-only)
  - Local only: confirm_invoice, confirm_payment
  - Docker Compose for Odoo 17 + PostgreSQL 15
- **TASK_218**: Cloud VM Deployment + Live Vault Sync
  - docker-compose.cloud.yml (Agent + Monitor + Odoo + Caddy)
  - Dockerfile.cloud, Caddyfile, systemd service
  - setup-cloud-vm.sh for Oracle Cloud Free Tier
  - SyncDaemon with SSH key support
  - CLOUD_SETUP_GUIDE.md step-by-step manual
- **TASK_219**: A2A Interface Definitions
  - A2AMessage dataclass with TTL support
  - A2ATransport ABC for pluggable transports
  - FileBasedTransport using Platinum/Signals/
- **TASK_220-225**: Constitutional Compliance Completion
  - SELF_ASSESSMENT.md (Article IX compliance)
  - Odoo MCP wrapper (Section 10.5.2 compliance)
  - Full Section 10.6 demo with real directory flow
  - Updated CHANGELOG, DECISIONS, REQUESTS, RESPONSES

### Changed
- **DECISIONS.md**: Added ADR-008 through ADR-013 (6 Platinum decisions)
- **REQUESTS.md**: Added Platinum Level Requests section
- **RESPONSES.md**: Added Platinum Level Responses section
- **TASKS_Platinum.md**: Updated with TASK_220-225
- **DASHBOARD_Platinum.md**: Updated with final metrics

---

## [3.1.0] - 2026-02-04

### Added
- **TASK_213**: Platinum Tier Implementation (Article X of CONSTITUTION.md)
  - 5 reusable Platinum skills: VaultSync, DraftManager, ClaimManager, AgentHeartbeat, SecretGuard
  - CloudAgent: Always-on agent that scans, claims, drafts, and submits for approval
  - LocalAgent: Executive agent that reviews, approves, executes, and updates dashboard
  - 10 new API endpoints at `/api/v1/platinum/` (status, tasks, approve, reject, demo, audit)
  - 3 new database models: PlatinumTask, AgentStatus, PlatinumAuditLog
  - File-based delegation directories (Needs_Action, Pending_Approval, In_Progress, Done)
  - Claim-by-move rule preventing double-work between agents
  - Secret boundary enforcement (Cloud blocked from .env, .key, banking, payment tokens)
  - Section 10.6 demo gate: 7-step email triage workflow verified
  - 54 tests passing (47 unit + 7 integration), 79% coverage on skills

### Changed
- **database.py**: Added 3 Platinum models
- **main.py**: Mounted Platinum router
- **requirements.txt**: Added watchdog dependency
- **SKILLS.md**: Added 5 Platinum skills documentation

---

## [3.0.0] - 2026-02-01

### Added
- **CONSTITUTION.md v2.0**: Article X - Platinum Tier (Always-On Cloud + Local Executive)
  - Dual-agent architecture: Cloud Agent (24/7) + Local Agent (executive authority)
  - Work-zone specialization: Cloud owns drafts, Local owns approvals and execution
  - File-based delegation via synced vault (`/Needs_Action/`, `/Pending_Approval/`, `/Done/`)
  - Claim-by-move rule for preventing double-work
  - Secret isolation: Cloud NEVER stores WhatsApp sessions, banking creds, payment tokens
  - Odoo Community integration (draft-only via MCP, Local approval for posting)
  - Platinum demo gate: Email triage while Local offline → Cloud drafts → Local approves → send
  - Optional A2A upgrade path (Phase 2)

### Changed
- CONSTITUTION.md upgraded from v1.0 to v2.0 (10 Articles → 11 Articles)
- Article X (old Enforcement) renumbered to Article XI

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
