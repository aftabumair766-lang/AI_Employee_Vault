# ARCHITECTURAL DECISION RECORDS

Per CONSTITUTION.md Article V, Section 5.4 and Article III, Section 3.3

---

## ADR-001: FastAPI as API Framework

**Date**: 2026-02-01
**Status**: Approved (Human approval received)
**Task**: TASK_206

### Context
Need REST API framework to expose TASK_204 security modules as web services.

### Decision
Selected **FastAPI** over alternatives.

### Alternatives Considered

| Framework | Pros | Cons |
|-----------|------|------|
| **FastAPI** (chosen) | Auto OpenAPI docs, async support, type validation, modern | Newer, smaller community than Flask |
| Flask | Mature, large ecosystem, simple | No auto docs, no async, manual validation |
| Django REST | Full-featured, admin panel | Heavy, overkill for API-only |

### Rationale
1. Auto-generated Swagger docs at `/docs` (saves documentation time)
2. Built-in Pydantic validation (reuses type hints)
3. Async support (better performance)
4. Aligns with modern Python practices

### Risks
- Newer framework, but stable (v0.109.0)
- Mitigated: Well-tested, backed by large community

### Reversibility
High - Routes can be migrated to Flask with minimal changes.

---

## ADR-002: SQLite as Database

**Date**: 2026-02-01
**Status**: Approved (Human approval received)
**Task**: TASK_207

### Context
Need database to persist tasks, security logs, and metrics.

### Decision
Selected **SQLite** with SQLAlchemy ORM.

### Alternatives Considered

| Database | Pros | Cons |
|----------|------|------|
| **SQLite** (chosen) | Zero config, file-based, portable, no server needed | Limited concurrency, no network access |
| PostgreSQL | Full-featured, scalable, concurrent | Requires server setup, complex config |
| MongoDB | Flexible schema, JSON-native | Different paradigm, overkill for structured data |

### Rationale
1. Zero setup - single file (`ai_employee.db`)
2. Portable - database travels with project
3. SQLAlchemy ORM - can migrate to PostgreSQL later without code changes
4. Sufficient for project scope (single user, low concurrency)

### Risks
- Limited concurrent writes
- Mitigated: Single-user application, SQLAlchemy abstracts migration path

### Reversibility
High - SQLAlchemy ORM allows database swap by changing connection string only.

---

## ADR-003: HTML Dashboard over React/Vue

**Date**: 2026-02-01
**Status**: Approved (Human approval received)
**Task**: TASK_208

### Context
Need visual dashboard to display task status, security metrics, and system health.

### Decision
Selected **plain HTML/CSS/JS** served by FastAPI with Jinja2 templates.

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **Plain HTML/JS** (chosen) | Zero build step, instant deploy, simple | Limited interactivity, no component reuse |
| React | Component-based, rich ecosystem | Build tooling, npm dependencies, complexity |
| Streamlit | Python-native, fast prototyping | Limited customization, separate server |

### Rationale
1. No build tooling needed (no npm, webpack, etc.)
2. Served directly from FastAPI (single server)
3. Auto-refresh via `setInterval` provides live updates
4. Sufficient for monitoring dashboard use case

### Risks
- Limited for complex UIs
- Mitigated: Dashboard is read-only monitoring, not interactive app

### Reversibility
High - Can add React frontend later, API endpoints remain same.

---

## ADR-004: Docker for Deployment

**Date**: 2026-02-01
**Status**: Approved (Human approval received)
**Task**: TASK_209

### Context
Need containerized deployment for portability and production readiness.

### Decision
**Docker** with multi-stage build + docker-compose.

### Rationale
1. Industry standard for containerization
2. Multi-stage build reduces image size
3. docker-compose enables single-command startup
4. Health checks ensure reliability

### Reversibility
High - Application runs with or without Docker.

---

## ADR-005: In-Memory Metrics over Prometheus Server

**Date**: 2026-02-01
**Status**: Approved (Human approval received)
**Task**: TASK_210

### Context
Need application monitoring and system resource tracking.

### Decision
Custom **MetricsCollector** class with in-memory storage + psutil for system metrics.

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **In-memory MetricsCollector** (chosen) | Zero dependencies, simple, fast | Lost on restart, limited history |
| Prometheus + Grafana | Industry standard, persistent, rich dashboards | Complex setup, multiple services |
| StatsD | Lightweight, UDP-based | Requires separate server |

### Rationale
1. Zero external dependencies (no Prometheus server needed)
2. Metrics served via API endpoint (`/api/v1/metrics`)
3. Dashboard consumes metrics directly
4. psutil provides real system resource data
5. Sufficient for demonstration and monitoring

### Risks
- Metrics lost on restart
- Mitigated: Can add persistence to database (MetricRecord table exists)

### Reversibility
High - prometheus-client already in requirements, can add Prometheus exporter later.

---

## ADR-006: PyPI for Package Distribution

**Date**: 2026-02-01
**Status**: Approved (Human approval received)
**Task**: TASK_211

### Context
Security skills (TASK_204) needed to be reusable across projects and available as a dependency for cloud deployment.

### Decision
Published as **PyPI package** (`ai-employee-security-skills`).

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **PyPI** (chosen) | Global install via pip, versioned, standard | Requires account setup |
| Git submodule | No external service | Complex, version management difficult |
| Copy files manually | Simple | No versioning, no dependency management |

### Rationale
1. Standard Python distribution method
2. `pip install` works everywhere
3. Versioned releases (v1.0.0)
4. Solves Docker build context issues (no need to COPY skills/)
5. Professional - demonstrates package publishing expertise

### Reversibility
High - Package can be unpublished, code still exists in repo.

---

## ADR-007: Railway.app for Cloud Deployment

**Date**: 2026-02-01
**Status**: Approved (Human approval received)
**Task**: TASK_212

### Context
Need free cloud deployment for public API access. No credit card charge risk.

### Decision
Selected **Railway.app** over alternatives.

### Alternatives Considered

| Platform | Pros | Cons |
|----------|------|------|
| **Railway.app** (chosen) | No credit card risk, GitHub login, Docker support, $5 free/month | Limited free tier |
| Google Cloud Run | Industry standard, generous free tier | Credit card required, accidental charge risk |
| Render.com | Free tier, no card | Sleep after 15 min, slower |
| Azure | Enterprise standard | Credit card required, complex setup |

### Rationale
1. Zero charge risk (no credit card required)
2. GitHub integration (one-click login)
3. Docker support (uses existing Dockerfile)
4. Free tier sufficient ($5/month credit, project uses ~$0.50)
5. Human explicitly requested no-charge-risk option

### Reversibility
High - Can migrate to any cloud platform, API code is platform-independent.

---

## ADR-008: Dual-Agent Architecture (Cloud + Local)

**Date**: 2026-02-04
**Status**: Approved (Human approval received)
**Task**: TASK_213

### Context
Need always-on automation (email triage, monitoring) while keeping executive authority (sends, payments, secrets) on a local machine under human control.

### Decision
Selected **Dual-Agent Architecture**: Cloud Agent (24/7 drafter) + Local Agent (executive authority).

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **Dual-Agent** (chosen) | Secret isolation, always-on drafts, human approval | More complex, file sync needed |
| Single Cloud Agent | Simple, always-on | Secrets on cloud, no human gate |
| Single Local Agent | Full control, simple | Not always-on, misses emails |

### Rationale
1. Cloud Agent drafts 24/7 - never misses incoming email or tasks
2. Local Agent holds all secrets - banking, WhatsApp, payment tokens
3. Claim-by-move rule prevents double-work between agents
4. Draft-only cloud operations ensure no unauthorized external actions
5. Constitutional requirement (Article X)

### Risks
- File sync latency between cloud and local
- Mitigated: VaultSync with configurable interval, heartbeat monitoring

### Reversibility
High - Agents are independent modules, can run either standalone.

---

## ADR-009: Pydantic-Settings for Configuration

**Date**: 2026-02-05
**Status**: Approved (Human approval received)
**Task**: TASK_214

### Context
Need centralized configuration supporting environment variables, .env files, and separate Cloud/Local settings.

### Decision
Selected **pydantic-settings** (`PlatinumSettings` class) with .env file support.

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **pydantic-settings** (chosen) | Type validation, .env support, IDE autocomplete | Extra dependency |
| python-dotenv + os.environ | Simple, no validation dependency | No type checking, manual parsing |
| YAML config files | Human-readable, nested | No env var override, another parser |

### Rationale
1. Built-in type validation (int ports, bool flags auto-parsed)
2. .env file loading with `PLATINUM_` prefix for namespace isolation
3. Property helpers (`has_imap`, `has_odoo`) simplify conditional logic
4. Singleton pattern with `get_settings()` prevents duplicate loading

### Reversibility
High - Settings class can be replaced with any config loader, consumers use the same interface.

---

## ADR-010: IMAP/SMTP for Email (not API)

**Date**: 2026-02-05
**Status**: Approved (Human approval received)
**Task**: TASK_214

### Context
Need email integration for Cloud Agent (read inbox) and Local Agent (send replies).

### Decision
Selected **IMAP for reading** + **SMTP for sending** over Gmail API.

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **IMAP/SMTP** (chosen) | Works with any provider, App Passwords, simple | Less features than API |
| Gmail API (OAuth2) | Full API, labels, threads | OAuth complexity, Google-specific, token refresh |
| Microsoft Graph API | Enterprise features | Azure AD setup, Microsoft-specific |

### Rationale
1. Provider-agnostic - works with Gmail, Outlook, any IMAP server
2. Gmail App Passwords avoid OAuth2 complexity
3. Clear separation: Cloud reads (IMAP), Local sends (SMTP)
4. Standard library `imaplib`/`smtplib` - zero extra dependencies

### Reversibility
High - EmailReader/EmailSender are abstracted, can swap to API clients.

---

## ADR-011: XML-RPC for Odoo (not MCP)

**Date**: 2026-02-05
**Status**: Approved (Human approval received)
**Task**: TASK_217

### Context
Need Odoo Community integration for accounting operations (draft invoices, payments).

### Decision
Selected **XML-RPC** (Odoo's native API) wrapped in an MCP-compatible interface.

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **XML-RPC + MCP wrapper** (chosen) | Odoo-native, no extra server, MCP-compatible | XML-RPC verbose |
| JSON-RPC | Slightly cleaner syntax | Not standard in Odoo Community docs |
| OdooRPC library | Higher-level abstraction | Extra dependency, less control |

### Rationale
1. XML-RPC is Odoo Community's documented API protocol
2. Standard library `xmlrpc.client` - zero extra dependencies
3. MCP wrapper layer satisfies Constitution Section 10.5.2 ("via MCP")
4. Cloud creates drafts only, Local confirms - role enforcement in client

### Reversibility
High - OdooClient is self-contained, can swap to JSON-RPC or OdooRPC.

---

## ADR-012: Oracle Cloud Free Tier for Deployment

**Date**: 2026-02-05
**Status**: Approved (Human approval received)
**Task**: TASK_218

### Context
Need always-on cloud VM for Cloud Agent, Odoo, and monitoring. Must be free with no charge risk.

### Decision
Selected **Oracle Cloud Free Tier** (Always Free ARM VM).

### Alternatives Considered

| Platform | Pros | Cons |
|----------|------|------|
| **Oracle Cloud Free Tier** (chosen) | Always Free, 4 OCPU, 24GB RAM, no card charge | ARM architecture, Oracle UI complexity |
| AWS Free Tier | Industry standard, familiar | 12-month limit, t2.micro only, charge risk |
| Google Cloud Free Tier | f1-micro always free | Very limited (0.6GB RAM), charge risk |
| Railway.app | Simple, already used for Gold | Not suitable for always-on VM + Odoo |

### Rationale
1. Always Free tier (no expiration, no charges)
2. ARM VM with 4 OCPU + 24GB RAM - generous for Odoo + Agent
3. Docker support via standard Ubuntu/Oracle Linux
4. Caddy reverse proxy for HTTPS
5. systemd service for auto-restart

### Reversibility
High - Docker Compose is portable, can deploy on any cloud VM.

---

## ADR-013: File-Based A2A Transport (Phase 1)

**Date**: 2026-02-05
**Status**: Approved (Human approval received)
**Task**: TASK_219

### Context
Need inter-agent communication between Cloud and Local agents. Constitution allows optional A2A upgrade (Section 10.7).

### Decision
Selected **File-Based Transport** (Phase 1) with abstract interface for future upgrades.

### Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **File-Based Transport** (chosen) | Simple, works with git sync, debuggable | Not real-time |
| WebSocket A2A | Real-time, bidirectional | Requires persistent connection, complex |
| gRPC | Typed messages, efficient | Heavy setup, proto files, code generation |
| Redis Pub/Sub | Fast, lightweight | External dependency, needs Redis server |

### Rationale
1. A2AMessage dataclass with TTL support for message expiry
2. A2ATransport ABC allows pluggable backends (file, WebSocket, gRPC)
3. FileBasedTransport works with existing git-based vault sync
4. Messages are JSON files in Platinum/Signals/ - easily debuggable
5. Phase 2 can swap to WebSocket/gRPC without changing message format

### Reversibility
High - ABC interface means any transport can be plugged in.

---

## Decision Summary

| ADR | Decision | Task | Risk Level |
|-----|----------|------|------------|
| ADR-001 | FastAPI | TASK_206 | Low |
| ADR-002 | SQLite + SQLAlchemy | TASK_207 | Low |
| ADR-003 | Plain HTML Dashboard | TASK_208 | Low |
| ADR-004 | Docker | TASK_209 | Low |
| ADR-005 | In-Memory Metrics | TASK_210 | Low |
| ADR-006 | PyPI Package | TASK_211 | Low |
| ADR-007 | Railway.app Cloud | TASK_212 | Low |
| ADR-008 | Dual-Agent Architecture | TASK_213 | Low |
| ADR-009 | Pydantic-Settings Config | TASK_214 | Low |
| ADR-010 | IMAP/SMTP for Email | TASK_214 | Low |
| ADR-011 | XML-RPC + MCP for Odoo | TASK_217 | Low |
| ADR-012 | Oracle Cloud Free Tier | TASK_218 | Low |
| ADR-013 | File-Based A2A Transport | TASK_219 | Low |

**All decisions**: High reversibility, Low risk, Human-approved.
