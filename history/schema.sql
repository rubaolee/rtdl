CREATE TABLE IF NOT EXISTS revision_rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    started_on TEXT NOT NULL,
    closed_on TEXT,
    source_commit TEXT,
    summary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS revision_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER NOT NULL,
    event_order INTEGER NOT NULL,
    event_date TEXT NOT NULL,
    actor TEXT NOT NULL,
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    related_path TEXT,
    FOREIGN KEY (round_id) REFERENCES revision_rounds(id)
);

CREATE TABLE IF NOT EXISTS revision_round_status (
    round_id INTEGER PRIMARY KEY,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    gemini_review TEXT NOT NULL,
    codex_revision TEXT NOT NULL,
    final_result TEXT NOT NULL,
    FOREIGN KEY (round_id) REFERENCES revision_rounds(id)
);

CREATE TABLE IF NOT EXISTS archived_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    label TEXT NOT NULL,
    source_path TEXT NOT NULL,
    archive_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    FOREIGN KEY (round_id) REFERENCES revision_rounds(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS archived_files_round_archive_sha_idx
ON archived_files(round_id, archive_path, sha256);
