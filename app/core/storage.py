import json
import sqlite3
from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.core.logging import logger


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    meta_json TEXT NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    ts_ms INTEGER NOT NULL,
                    latency_ms REAL NOT NULL,
                    ipc REAL NOT NULL,
                    cache_miss REAL NOT NULL,
                    power_w REAL NOT NULL,
                    warnings INTEGER NOT NULL,
                    errors INTEGER NOT NULL,
                    raw_line TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                );
                """
            )
            con.commit()
        logger.info("DB initialized.")

    def insert_run(self, run_id: str, created_at: str, meta: Dict[str, Any]) -> None:
        with self.connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO runs(run_id, created_at, meta_json) VALUES (?, ?, ?)",
                (run_id, created_at, json.dumps(meta)),
            )
            con.commit()

    def insert_samples(self, run_id: str, rows: List[Tuple]) -> None:
        # rows: (ts_ms, latency_ms, ipc, cache_miss, power_w, warnings, errors, raw_line)
        with self.connect() as con:
            con.executemany(
                """
                INSERT INTO samples(
                    run_id, ts_ms, latency_ms, ipc, cache_miss, power_w, warnings, errors, raw_line
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [(run_id, *r) for r in rows],
            )
            con.commit()

    def list_runs(self) -> List[Dict[str, Any]]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT run_id, created_at, meta_json FROM runs ORDER BY created_at DESC")
            out = []
            for run_id, created_at, meta_json in cur.fetchall():
                out.append({"run_id": run_id, "created_at": created_at, "meta": json.loads(meta_json)})
            return out

    def get_samples(self, run_id: str) -> List[Dict[str, Any]]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                SELECT ts_ms, latency_ms, ipc, cache_miss, power_w, warnings, errors, raw_line
                FROM samples
                WHERE run_id = ?
                ORDER BY ts_ms ASC
                """,
                (run_id,),
            )
            rows = []
            for r in cur.fetchall():
                rows.append(
                    {
                        "ts_ms": r[0],
                        "latency_ms": r[1],
                        "ipc": r[2],
                        "cache_miss": r[3],
                        "power_w": r[4],
                        "warnings": r[5],
                        "errors": r[6],
                        "raw_line": r[7],
                    }
                )
            return rows


storage = Storage(settings.DB_PATH)
