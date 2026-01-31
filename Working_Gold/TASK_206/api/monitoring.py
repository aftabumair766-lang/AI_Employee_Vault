"""
TASK_210: Monitoring & Observability
Prometheus metrics + system health monitoring
Uses existing skills: SecureLogging for safe log output
"""
import time
import psutil
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps


class MetricsCollector:
    """Collect and serve application metrics"""

    def __init__(self):
        self.request_count = defaultdict(int)
        self.request_duration = defaultdict(list)
        self.error_count = defaultdict(int)
        self.start_time = datetime.utcnow()
        self.security_operations = defaultdict(int)

    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record API request metrics"""
        key = f"{method}:{endpoint}"
        self.request_count[key] += 1
        self.request_duration[key].append(duration)

        if status_code >= 400:
            self.error_count[key] += 1

    def record_security_op(self, operation: str, success: bool):
        """Record security operation"""
        key = f"{operation}:{'success' if success else 'failure'}"
        self.security_operations[key] += 1

    def get_system_metrics(self) -> dict:
        """Get current system resource metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total_mb": round(psutil.virtual_memory().total / 1024 / 1024),
                "used_mb": round(psutil.virtual_memory().used / 1024 / 1024),
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total_gb": round(psutil.disk_usage('/').total / 1024 / 1024 / 1024, 1),
                "used_gb": round(psutil.disk_usage('/').used / 1024 / 1024 / 1024, 1),
                "percent": psutil.disk_usage('/').percent
            }
        }

    def get_api_metrics(self) -> dict:
        """Get API performance metrics"""
        metrics = {}
        for endpoint, durations in self.request_duration.items():
            if durations:
                metrics[endpoint] = {
                    "total_requests": self.request_count[endpoint],
                    "avg_duration_ms": round(sum(durations) / len(durations) * 1000, 2),
                    "min_duration_ms": round(min(durations) * 1000, 2),
                    "max_duration_ms": round(max(durations) * 1000, 2),
                    "errors": self.error_count.get(endpoint, 0)
                }
        return metrics

    def get_security_metrics(self) -> dict:
        """Get security operations summary"""
        return dict(self.security_operations)

    def get_uptime(self) -> str:
        """Get application uptime"""
        delta = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def get_dashboard_data(self) -> dict:
        """Get all metrics for dashboard"""
        total_requests = sum(self.request_count.values())
        total_errors = sum(self.error_count.values())
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0

        return {
            "uptime": self.get_uptime(),
            "started_at": self.start_time.isoformat(),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_percent": round(error_rate, 2),
            "system": self.get_system_metrics(),
            "api_endpoints": self.get_api_metrics(),
            "security_operations": self.get_security_metrics()
        }


# Singleton instance
metrics = MetricsCollector()
