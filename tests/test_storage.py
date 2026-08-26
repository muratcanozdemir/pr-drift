import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pr_drift.storage import Storage


class TestStorage(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "test.db"

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_creates_table(self):
        Storage(self.db_path)
        conn = sqlite3.connect(self.db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        self.assertIn(("pr_events",), tables)

    def test_record_round_trip(self):
        store = Storage(self.db_path)
        store.record(
            owner="acme",
            repo="widgets",
            pr_number=42,
            diff_bytes=123,
            score=0.5,
            z_score=1.2,
        )

        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT owner, repo, pr_number, diff_bytes, score, z_score FROM pr_events"
        ).fetchone()
        conn.close()

        self.assertEqual(row, ("acme", "widgets", 42, 123, 0.5, 1.2))

    def test_record_appends_multiple_rows(self):
        store = Storage(self.db_path)
        for i in range(3):
            store.record(
                owner="acme",
                repo="widgets",
                pr_number=i,
                diff_bytes=10,
                score=0.1,
                z_score=0.0,
            )

        conn = sqlite3.connect(self.db_path)
        count = conn.execute("SELECT COUNT(*) FROM pr_events").fetchone()[0]
        conn.close()

        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()
