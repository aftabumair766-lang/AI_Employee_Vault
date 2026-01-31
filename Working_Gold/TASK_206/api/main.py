"""
TASK_206: REST API for AI Employee Vault Security Services
Uses existing skills from TASK_204
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

# Import existing security skills
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "TASK_204" / "scripts"))

from path_validator import PathValidator
from encryption_utils import ArchiveEncryption
from integrity_checker import IntegrityChecker
from input_validator import InputValidator

app = FastAPI(
    title="AI Employee Vault API",
    description="Security services API using production-ready modules",
    version="1.0.0"
)

# Initialize security modules
path_validator = PathValidator()
encryptor = ArchiveEncryption()
integrity_checker = IntegrityChecker()
input_validator = InputValidator()

# Request/Response Models
class PathValidationRequest(BaseModel):
    path: str

class PathValidationResponse(BaseModel):
    is_safe: bool
    sanitized_path: Optional[str]
    message: str

class IntegrityRequest(BaseModel):
    file_path: str

class IntegrityResponse(BaseModel):
    checksum: str
    algorithm: str = "sha256"

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "AI Employee Vault API",
        "version": "1.0.0",
        "endpoints": {
            "security": "/api/v1/security/*",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "path_validator": "up",
            "encryptor": "up",
            "integrity_checker": "up"
        }
    }

@app.post("/api/v1/security/validate-path", response_model=PathValidationResponse)
async def validate_path(request: PathValidationRequest):
    """Validate file path using PathValidator skill"""
    try:
        is_safe = path_validator.is_safe_path(request.path)

        if is_safe:
            sanitized = path_validator.sanitize_path(request.path)
            return PathValidationResponse(
                is_safe=True,
                sanitized_path=sanitized,
                message="Path is safe"
            )
        else:
            return PathValidationResponse(
                is_safe=False,
                sanitized_path=None,
                message="Path validation failed - potential security risk"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/security/integrity/generate", response_model=IntegrityResponse)
async def generate_checksum(file: UploadFile = File(...)):
    """Generate SHA-256 checksum using IntegrityChecker skill"""
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        content = await file.read()

        with open(temp_path, 'wb') as f:
            f.write(content)

        checksum = integrity_checker.generate_checksum(temp_path)

        return IntegrityResponse(
            checksum=checksum,
            algorithm="sha256"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/security/encrypt")
async def encrypt_file(file: UploadFile = File(...)):
    """Encrypt file using ArchiveEncryption skill"""
    try:
        temp_input = f"/tmp/{file.filename}"
        temp_output = f"/tmp/{file.filename}.enc"

        content = await file.read()
        with open(temp_input, 'wb') as f:
            f.write(content)

        success = encryptor.encrypt_file(temp_input, temp_output)

        if success:
            return {"status": "encrypted", "output": temp_output}
        else:
            raise HTTPException(status_code=500, detail="Encryption failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tasks")
async def list_tasks():
    """List tasks from TASKS_Gold.md"""
    tasks_file = Path(__file__).parent.parent.parent.parent / "TASKS_Gold.md"

    if tasks_file.exists():
        content = tasks_file.read_text()
        # Simple parsing - return raw for now
        return {"tasks": "See TASKS_Gold.md", "file": str(tasks_file)}
    else:
        raise HTTPException(status_code=404, detail="Tasks file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
