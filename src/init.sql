CREATE TABLE pr_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    owner TEXT NOT NULL,
    repo TEXT NOT NULL,
    pr_number INTEGER NOT NULL,
    diff_bytes INTEGER NOT NULL,
    score REAL NOT NULL,
    z_score REAL NOT NULL
);
