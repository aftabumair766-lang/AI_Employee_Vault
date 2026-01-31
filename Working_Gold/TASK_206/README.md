# TASK_206: REST API Development

## Quick Start

```bash
cd Working_Gold/TASK_206
pip install -r requirements.txt
python api/main.py
```

Visit: http://localhost:8000/docs

## Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /api/v1/security/validate-path` - Validate paths
- `POST /api/v1/security/integrity/generate` - Generate checksums
- `POST /api/v1/security/encrypt` - Encrypt files
- `GET /api/v1/tasks` - List tasks

## Skills Used

- PathValidator (TASK_204)
- ArchiveEncryption (TASK_204)
- IntegrityChecker (TASK_204)
- InputValidator (TASK_204)

## Status

Phase 1: ✅ Basic API with existing skills
