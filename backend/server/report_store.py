"""
SQLite-based report store for GPT Researcher.
Replaces the plain JSON file store with a proper database for:
- Data integrity (ACID transactions)
- Concurrent access safety
- Better performance with large datasets
- Automatic WAL mode for crash resistance
"""

import asyncio
import json
import sqlite3
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ReportStore:
    """SQLite-backed report storage with async-safe locking."""

    def __init__(self, path: Path):
        # If the old path ends with .json, switch to .db in the same directory
        if str(path).endswith('.json'):
            self._db_path = path.with_suffix('.db')
            self._old_json_path = path
        else:
            self._db_path = path
            self._old_json_path = None

        self._lock = asyncio.Lock()
        self._initialized = False

    def _get_conn(self) -> sqlite3.Connection:
        """Create a new connection (SQLite connections are not thread-safe)."""
        conn = sqlite3.connect(str(self._db_path), timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")       # Write-Ahead Logging for crash safety
        conn.execute("PRAGMA synchronous=NORMAL")      # Good balance of safety and speed
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self, conn: sqlite3.Connection) -> None:
        """Create tables if they don't exist."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at INTEGER DEFAULT (strftime('%s','now') * 1000),
                updated_at INTEGER DEFAULT (strftime('%s','now') * 1000)
            )
        """)
        conn.commit()

    def _migrate_from_json(self, conn: sqlite3.Connection) -> None:
        """One-time migration from old JSON file to SQLite."""
        if self._old_json_path and self._old_json_path.exists():
            try:
                raw = self._old_json_path.read_text(encoding="utf-8")
                data = json.loads(raw)
                if isinstance(data, dict):
                    count = 0
                    for report_id, report in data.items():
                        json_data = json.dumps(report, ensure_ascii=False)
                        timestamp = report.get("timestamp", 0)
                        conn.execute(
                            "INSERT OR IGNORE INTO reports (id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                            (report_id, json_data, timestamp, timestamp)
                        )
                        count += 1
                    conn.commit()
                    logger.info(f"Migrated {count} reports from JSON to SQLite")

                # Rename old file so we don't migrate again
                backup_path = self._old_json_path.with_suffix('.json.bak')
                self._old_json_path.rename(backup_path)
                logger.info(f"Old JSON file renamed to {backup_path}")
            except Exception as e:
                logger.error(f"Failed to migrate from JSON: {e}")

    async def _ensure_init(self) -> None:
        """Initialize database on first use."""
        if self._initialized:
            return
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._get_conn()
        try:
            self._ensure_tables(conn)
            self._migrate_from_json(conn)
        finally:
            conn.close()
        self._initialized = True

    async def list_reports(self, report_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            await self._ensure_init()
            conn = self._get_conn()
            try:
                if report_ids is None:
                    rows = conn.execute(
                        "SELECT data FROM reports ORDER BY updated_at DESC"
                    ).fetchall()
                else:
                    placeholders = ",".join("?" for _ in report_ids)
                    rows = conn.execute(
                        f"SELECT data FROM reports WHERE id IN ({placeholders}) ORDER BY updated_at DESC",
                        report_ids
                    ).fetchall()
                return [json.loads(row["data"]) for row in rows]
            finally:
                conn.close()

    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            await self._ensure_init()
            conn = self._get_conn()
            try:
                row = conn.execute(
                    "SELECT data FROM reports WHERE id = ?", (report_id,)
                ).fetchone()
                if row is None:
                    return None
                return json.loads(row["data"])
            finally:
                conn.close()

    async def upsert_report(self, report_id: str, report: Dict[str, Any]) -> None:
        async with self._lock:
            await self._ensure_init()
            conn = self._get_conn()
            try:
                json_data = json.dumps(report, ensure_ascii=False)
                timestamp = report.get("timestamp", 0)
                conn.execute(
                    """INSERT INTO reports (id, data, created_at, updated_at)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at""",
                    (report_id, json_data, timestamp, timestamp)
                )
                conn.commit()
            finally:
                conn.close()

    async def delete_report(self, report_id: str) -> bool:
        async with self._lock:
            await self._ensure_init()
            conn = self._get_conn()
            try:
                cursor = conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
                conn.commit()
                return cursor.rowcount > 0
            finally:
                conn.close()
