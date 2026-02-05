"""
Platinum Tier - Dual-Agent Architecture Skills
Article X of CONSTITUTION.md

Core Skills:
- VaultSync: Git-based vault synchronization
- DraftManager: Draft creation & approval workflow
- ClaimManager: Claim-by-move task ownership
- AgentHeartbeat: Agent health monitoring
- SecretGuard: Secret boundary enforcement

Integration Modules:
- EmailReader / EmailSender: Gmail IMAP/SMTP
- SocialDrafter / SocialPoster: Twitter/X integration
- WhatsAppStub: WhatsApp Business API (stub)
- BankingStub: Banking API (stub)
- OdooClient: Odoo Community XML-RPC
- HealthMonitor: Health monitoring daemon
- A2ATransport: Agent-to-Agent communication
"""

from Platinum.src.vault_sync import VaultSync
from Platinum.src.draft_manager import DraftManager
from Platinum.src.claim_manager import ClaimManager
from Platinum.src.agent_heartbeat import AgentHeartbeat
from Platinum.src.secret_guard import SecretGuard
from Platinum.src.config import PlatinumSettings, get_settings
from Platinum.src.email_client import EmailReader, EmailSender
from Platinum.src.social_client import SocialDrafter, SocialPoster
from Platinum.src.whatsapp_stub import WhatsAppStub
from Platinum.src.banking_stub import BankingStub
from Platinum.src.odoo_client import OdooClient
from Platinum.src.health_monitor import HealthMonitor
from Platinum.src.a2a_interface import A2AMessage, A2ATransport, FileBasedTransport
from Platinum.src.sync_daemon import SyncDaemon

__all__ = [
    # Core Skills
    "VaultSync",
    "DraftManager",
    "ClaimManager",
    "AgentHeartbeat",
    "SecretGuard",
    # Config
    "PlatinumSettings",
    "get_settings",
    # Integrations
    "EmailReader",
    "EmailSender",
    "SocialDrafter",
    "SocialPoster",
    "WhatsAppStub",
    "BankingStub",
    "OdooClient",
    "HealthMonitor",
    # A2A (Phase 2)
    "A2AMessage",
    "A2ATransport",
    "FileBasedTransport",
    # Daemons
    "SyncDaemon",
]
