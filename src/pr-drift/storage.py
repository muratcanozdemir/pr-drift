import sqlite3
from datetime import datetime
from pathlib import Path


class Storage:
    def __init__(self, path="pr_drift.db"):
        self.path = Path(path)
        self._init()

    def _init(self):
        conn = sqlite3.connect(self.path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS pr_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            owner TEXT NOT NULL,
            repo TEXT NOT NULL,
            pr_number INTEGER NOT NULL,
            diff_bytes INTEGER NOT NULL,
            score REAL NOT NULL,
            z_score REAL NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    def record(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        diff_bytes: int,
        score: float,
        z_score: float,
    ):
        conn = sqlite3.connect(self.path)
        conn.execute(
            "INSERT INTO pr_events VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.utcnow().isoformat(),
                owner,
                repo,
                pr_number,
                diff_bytes,
                score,
                z_score,
            )
        )
        conn.commit()
        conn.close()
