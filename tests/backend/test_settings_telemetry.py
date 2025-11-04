import asyncio
import os
import sys
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from database import Database


class ConnCtx:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return await self.conn.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        return await self.conn.__aexit__(exc_type, exc, tb)


class MetricsConn:
    def __init__(self):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, query, *params):
        self.calls.append((query, params))
        return None


class HealthConn:
    def __init__(self, fetch_sequences):
        self.fetch_sequences = fetch_sequences
        self.fetch_index = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def fetch(self, query, *params):
        result = self.fetch_sequences[self.fetch_index]
        self.fetch_index += 1
        return result

    async def fetchrow(self, query, *params):
        return None

    async def execute(self, query, *params):
        return None


class OverviewConn:
    def __init__(self, fetchrow_results):
        self.fetchrow_results = fetchrow_results
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def fetchrow(self, query, *params):
        self.calls.append((query, params))
        return self.fetchrow_results.pop(0)

    async def fetch(self, query, *params):
        return []

    async def execute(self, query, *params):
        return None


async def noop(*args, **kwargs):
    return None


def test_record_api_metric_tracks_success_and_error_counts():
    db = Database()
    db.ensure_settings_telemetry_schema = noop  # type: ignore
    conn = MetricsConn()
    db.get_connection = lambda: ConnCtx(conn)  # type: ignore

    asyncio.run(db.record_api_metric("GET", "/health", 200, 45))

    assert conn.calls, "expected metric insert"
    query, params = conn.calls[0]
    assert "success_count" in query and "error_count" in query
    # success request should increment success column
    assert params[-2] == 1
    assert params[-1] == 0


def test_get_service_health_summary_computes_uptime():
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    fetch_sequences = [
        [
            {
                "service_name": "postgres",
                "success_count": 5,
                "total_count": 5,
                "avg_latency": 12.5,
                "last_checked": now,
            },
            {
                "service_name": "redis",
                "success_count": 3,
                "total_count": 5,
                "avg_latency": None,
                "last_checked": now,
            },
        ],
        [
            {
                "service_name": "postgres",
                "status": True,
                "latency_ms": 10,
                "checked_at": now,
            },
            {
                "service_name": "redis",
                "status": False,
                "latency_ms": None,
                "checked_at": now,
            },
        ],
    ]

    db = Database()
    db.ensure_settings_telemetry_schema = noop  # type: ignore
    db.get_connection = lambda: ConnCtx(HealthConn(fetch_sequences))  # type: ignore

    summary = asyncio.run(db.get_service_health_summary(["postgres", "redis"], 1440))

    assert summary["postgres"]["uptime"] == 100.0
    assert summary["redis"]["uptime"] == 60.0
    assert summary["redis"]["latest_status"] is False


def test_get_api_overview_metrics_reports_previous_window():
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    fetchrow_results = [
        {
            "total_calls": 10,
            "total_latency": 250,
            "success_calls": 8,
            "error_calls": 2,
            "last_seen": now,
        },
        {"total_calls": 6},
    ]
    db = Database()
    db.ensure_settings_telemetry_schema = noop  # type: ignore
    db.get_connection = lambda: ConnCtx(OverviewConn(fetchrow_results))  # type: ignore

    metrics = asyncio.run(db.get_api_overview_metrics(window_days=7))

    assert metrics["total_calls"] == 10
    assert metrics["error_calls"] == 2
    assert metrics["previous_calls"] == 6
    assert metrics["avg_latency_ms"] == 25.0
