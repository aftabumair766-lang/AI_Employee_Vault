"""
PlatinumSettings - Centralized configuration using pydantic-settings + .env

Loads configuration from environment variables and .env files.
Supports separate Cloud and Local configurations.

Usage:
    from Platinum.src.config import get_settings
    settings = get_settings()
    print(settings.AGENT_ROLE)
"""

import os
from typing import Optional
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # type: ignore[no-redef]

from pydantic import Field


class PlatinumSettings(BaseSettings):
    """Centralized configuration for the Platinum Tier."""

    # === Agent Identity ===
    AGENT_ROLE: str = Field(default="local", description="Agent role: 'cloud' or 'local'")
    VAULT_PATH: str = Field(default=".", description="Path to the vault root directory")

    # === Email / IMAP (Cloud reads inbox) ===
    IMAP_HOST: str = Field(default="imap.gmail.com", description="IMAP server hostname")
    IMAP_PORT: int = Field(default=993, description="IMAP server port")
    IMAP_USER: str = Field(default="", description="IMAP username (email address)")
    IMAP_PASSWORD: str = Field(default="", description="IMAP password (Gmail App Password)")

    # === Email / SMTP (Local sends email) ===
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP server hostname")
    SMTP_PORT: int = Field(default=587, description="SMTP server port (TLS)")
    SMTP_USER: str = Field(default="", description="SMTP username (email address)")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password (Gmail App Password)")

    # === Social Media / Twitter/X API (Local only) ===
    TWITTER_API_KEY: str = Field(default="", description="Twitter/X API key")
    TWITTER_API_SECRET: str = Field(default="", description="Twitter/X API secret")
    TWITTER_ACCESS_TOKEN: str = Field(default="", description="Twitter/X access token")
    TWITTER_ACCESS_SECRET: str = Field(default="", description="Twitter/X access token secret")

    # === WhatsApp (Local only, stub) ===
    WHATSAPP_API_URL: str = Field(default="", description="WhatsApp Business API URL")
    WHATSAPP_API_TOKEN: str = Field(default="", description="WhatsApp API token")

    # === Banking (Local only, stub) ===
    BANKING_API_URL: str = Field(default="", description="Banking API base URL")
    BANKING_API_KEY: str = Field(default="", description="Banking API key")

    # === Odoo ===
    ODOO_URL: str = Field(default="http://localhost:8069", description="Odoo server URL")
    ODOO_DB: str = Field(default="odoo", description="Odoo database name")
    ODOO_USER: str = Field(default="admin", description="Odoo username")
    ODOO_PASSWORD: str = Field(default="admin", description="Odoo password")

    # === Database ===
    DATABASE_URL: str = Field(default="sqlite:///./ai_employee.db", description="SQLAlchemy DB URL")

    # === Health Monitor ===
    HEALTH_CHECK_INTERVAL: int = Field(default=60, description="Health check interval in seconds")
    HEALTH_ALERT_EMAIL: str = Field(default="", description="Email to send health alerts to")
    HEALTH_CLOUD_URL: str = Field(default="", description="Cloud VM URL for HTTP ping")
    HEALTH_API_URL: str = Field(default="http://localhost:8000", description="API base URL")

    # === Vault Sync ===
    GIT_REMOTE: str = Field(default="origin", description="Git remote name")
    GIT_BRANCH: str = Field(default="main", description="Git branch name")
    GIT_SSH_KEY: str = Field(default="", description="Path to SSH private key for git sync")
    SYNC_INTERVAL: int = Field(default=300, description="Sync interval in seconds")

    # === Heartbeat ===
    HEARTBEAT_INTERVAL: int = Field(default=30, description="Heartbeat interval in seconds")

    model_config = {
        "env_prefix": "PLATINUM_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def is_cloud(self) -> bool:
        return self.AGENT_ROLE == "cloud"

    @property
    def is_local(self) -> bool:
        return self.AGENT_ROLE == "local"

    @property
    def vault(self) -> Path:
        return Path(self.VAULT_PATH)

    @property
    def has_imap(self) -> bool:
        return bool(self.IMAP_USER and self.IMAP_PASSWORD)

    @property
    def has_smtp(self) -> bool:
        return bool(self.SMTP_USER and self.SMTP_PASSWORD)

    @property
    def has_twitter(self) -> bool:
        return bool(self.TWITTER_API_KEY and self.TWITTER_API_SECRET)

    @property
    def has_odoo(self) -> bool:
        return bool(self.ODOO_URL and self.ODOO_USER and self.ODOO_PASSWORD)


# Singleton settings instance
_settings: Optional[PlatinumSettings] = None


def get_settings(**overrides) -> PlatinumSettings:
    """Get or create the singleton settings instance.

    Args:
        **overrides: Override specific settings values.

    Returns:
        PlatinumSettings instance.
    """
    global _settings
    if overrides or _settings is None:
        _settings = PlatinumSettings(**overrides)
    return _settings


def reset_settings() -> None:
    """Reset the singleton (useful for testing)."""
    global _settings
    _settings = None
