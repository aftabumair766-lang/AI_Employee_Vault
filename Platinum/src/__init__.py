"""
Platinum Tier - Dual-Agent Architecture Skills
Article X of CONSTITUTION.md

5 Reusable Skills:
- VaultSync: Git-based vault synchronization
- DraftManager: Draft creation & approval workflow
- ClaimManager: Claim-by-move task ownership
- AgentHeartbeat: Agent health monitoring
- SecretGuard: Secret boundary enforcement
"""

from Platinum.src.vault_sync import VaultSync
from Platinum.src.draft_manager import DraftManager
from Platinum.src.claim_manager import ClaimManager
from Platinum.src.agent_heartbeat import AgentHeartbeat
from Platinum.src.secret_guard import SecretGuard

__all__ = [
    "VaultSync",
    "DraftManager",
    "ClaimManager",
    "AgentHeartbeat",
    "SecretGuard",
]
