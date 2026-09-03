"""
SQLite persistence — audit trail. Every compiled strategy, its crash-test
results, its gate decision, and any orders placed get a row here, so nothing
in a demo or a judge's review is "trust me, it happened."
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "crash_test.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    strategy_json TEXT NOT NULL,
    crash_test_summary_json TEXT,
    gate_decision_json TEXT,
    order_json TEXT
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def create_run(strategy_json: dict) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO runs (created_at, strategy_json) VALUES (?, ?)",
        (datetime.now(timezone.utc).isoformat(), json.dumps(strategy_json)),
    )
    conn.commit()
    run_id = cur.lastrowid
    conn.close()
    return run_id


def update_run(run_id: int, *, crash_test_summary: dict | None = None,
                gate_decision: dict | None = None, order: dict | None = None) -> None:
    conn = get_conn()
    if crash_test_summary is not None:
        conn.execute("UPDATE runs SET crash_test_summary_json = ? WHERE id = ?",
                     (json.dumps(crash_test_summary, default=str), run_id))
    if gate_decision is not None:
        conn.execute("UPDATE runs SET gate_decision_json = ? WHERE id = ?",
                     (json.dumps(gate_decision), run_id))
    if order is not None:
        conn.execute("UPDATE runs SET order_json = ? WHERE id = ?",
                     (json.dumps(order), run_id))
    conn.commit()
    conn.close()


def get_run(run_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    cols = ["id", "created_at", "strategy_json", "crash_test_summary_json", "gate_decision_json", "order_json"]
    record = dict(zip(cols, row))
    for key in ("strategy_json", "crash_test_summary_json", "gate_decision_json", "order_json"):
        if record[key]:
            record[key] = json.loads(record[key])
    return record


def list_runs(limit: int = 20) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT id, created_at, strategy_json FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [{"id": r[0], "created_at": r[1], "strategy": json.loads(r[2])} for r in rows]
