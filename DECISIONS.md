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

## Decision Summary

| ADR | Decision | Task | Risk Level |
|-----|----------|------|------------|
| ADR-001 | FastAPI | TASK_206 | Low |
| ADR-002 | SQLite + SQLAlchemy | TASK_207 | Low |
| ADR-003 | Plain HTML Dashboard | TASK_208 | Low |
| ADR-004 | Docker | TASK_209 | Low |
| ADR-005 | In-Memory Metrics | TASK_210 | Low |

**All decisions**: High reversibility, Low risk, Human-approved.
