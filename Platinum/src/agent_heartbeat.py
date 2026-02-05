"""
AgentHeartbeat - Agent health monitoring and status tracking.

Reusable Platinum Skill: Tracks agent liveness via periodic heartbeat
files written to the Updates/ directory. Supports background threading
for continuous heartbeat emission.

Usage:
    hb = AgentHeartbeat("cloud_agent", "/path/to/vault")
    hb.beat(current_task="DRAFT-ABC123")
    print(hb.is_alive("cloud_agent"))
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path


class AgentHeartbeat:
    """Agent health monitoring via periodic heartbeat files."""

    def __init__(self, agent_name: str, vault_path: str, interval: int = 30):
        self.agent_name = agent_name
        self.vault_path = Path(vault_path)
        self.interval = interval
        self.updates_dir = self.vault_path / "Platinum" / "Updates"
        self.updates_dir.mkdir(parents=True, exist_ok=True)
        self._background_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _heartbeat_path(self, agent_name: str) -> Path:
        return self.updates_dir / f"{agent_name}_heartbeat.json"

    def beat(self, current_task: Optional[str] = None) -> None:
        """Write a heartbeat file for this agent."""
        heartbeat_data = {
            "agent_name": self.agent_name,
            "status": "online",
            "current_task": current_task,
            "timestamp": datetime.utcnow().isoformat(),
            "interval": self.interval,
        }
        path = self._heartbeat_path(self.agent_name)
        path.write_text(json.dumps(heartbeat_data, indent=2), encoding="utf-8")

    def is_alive(self, agent_name: str, timeout: int = 60) -> bool:
        """Check if an agent is responsive (heartbeat within timeout seconds)."""
        path = self._heartbeat_path(agent_name)
        if not path.exists():
            return False

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            last_beat = datetime.fromisoformat(data["timestamp"])
            return (datetime.utcnow() - last_beat) < timedelta(seconds=timeout)
        except (json.JSONDecodeError, KeyError, ValueError):
            return False

    def get_status(self, agent_name: str) -> dict:
        """Get the last heartbeat data for an agent."""
        path = self._heartbeat_path(agent_name)
        if not path.exists():
            return {
                "agent_name": agent_name,
                "status": "offline",
                "current_task": None,
                "timestamp": None,
            }

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Check if stale
            last_beat = datetime.fromisoformat(data["timestamp"])
            if (datetime.utcnow() - last_beat) > timedelta(seconds=self.interval * 2):
                data["status"] = "stale"
            return data
        except (json.JSONDecodeError, KeyError, ValueError):
            return {
                "agent_name": agent_name,
                "status": "error",
                "current_task": None,
                "timestamp": None,
            }

    def get_all_agents(self) -> List[dict]:
        """Get status of all known agents from heartbeat files."""
        agents = []
        if self.updates_dir.exists():
            for f in self.updates_dir.glob("*_heartbeat.json"):
                agent_name = f.stem.replace("_heartbeat", "")
                agents.append(self.get_status(agent_name))
        return agents

    @classmethod
    def get_health_summary(cls, vault_path: str, interval: int = 30) -> dict:
        """Get a health summary for all agents (for HealthMonitor).

        Returns:
            Dict with agent names as keys and health status dicts as values.
        """
        updates_dir = Path(vault_path) / "Platinum" / "Updates"
        summary = {}
        if updates_dir.exists():
            for f in updates_dir.glob("*_heartbeat.json"):
                agent_name = f.stem.replace("_heartbeat", "")
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    last_beat = datetime.fromisoformat(data["timestamp"])
                    age_seconds = (datetime.utcnow() - last_beat).total_seconds()
                    is_stale = age_seconds > interval * 2
                    summary[agent_name] = {
                        "status": "stale" if is_stale else data.get("status", "unknown"),
                        "current_task": data.get("current_task"),
                        "last_heartbeat": data["timestamp"],
                        "age_seconds": round(age_seconds, 1),
                        "healthy": not is_stale and data.get("status") == "online",
                    }
                except (json.JSONDecodeError, KeyError, ValueError):
                    summary[agent_name] = {
                        "status": "error",
                        "current_task": None,
                        "last_heartbeat": None,
                        "age_seconds": None,
                        "healthy": False,
                    }
        return summary

    def start_background(self) -> None:
        """Start emitting heartbeats in a background thread."""
        if self._background_thread and self._background_thread.is_alive():
            return

        self._stop_event.clear()

        def _heartbeat_loop():
            while not self._stop_event.is_set():
                self.beat()
                self._stop_event.wait(self.interval)

        self._background_thread = threading.Thread(
            target=_heartbeat_loop, daemon=True, name=f"{self.agent_name}-heartbeat"
        )
        self._background_thread.start()

    def stop_background(self) -> None:
        """Stop the background heartbeat thread."""
        self._stop_event.set()
        if self._background_thread:
            self._background_thread.join(timeout=5)
            self._background_thread = None

        # Write offline status
        path = self._heartbeat_path(self.agent_name)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                data["status"] = "offline"
                data["timestamp"] = datetime.utcnow().isoformat()
                path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except (json.JSONDecodeError, KeyError):
                pass
