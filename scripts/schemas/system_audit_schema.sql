PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS audit_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at_utc TEXT NOT NULL,
    repo_root TEXT NOT NULL,
    git_commit TEXT NOT NULL,
    scope_label TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS file_inventory (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    subdomain TEXT NOT NULL,
    priority_tier INTEGER NOT NULL,
    extension TEXT NOT NULL,
    line_count INTEGER NOT NULL,
    size_bytes INTEGER NOT NULL,
    is_front_surface INTEGER NOT NULL DEFAULT 0,
    is_active_release_surface INTEGER NOT NULL DEFAULT 0,
    exists_on_disk INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS file_audit_status (
    file_id INTEGER PRIMARY KEY,
    review_status TEXT NOT NULL DEFAULT 'not_reviewed',
    correctness_status TEXT NOT NULL DEFAULT 'unchecked',
    quality_status TEXT NOT NULL DEFAULT 'unchecked',
    link_status TEXT NOT NULL DEFAULT 'unchecked',
    duplication_status TEXT NOT NULL DEFAULT 'unchecked',
    acronym_status TEXT NOT NULL DEFAULT 'unchecked',
    release_relevance TEXT NOT NULL DEFAULT 'unknown',
    reviewer TEXT NOT NULL DEFAULT '',
    last_run_id INTEGER,
    reviewed_at_utc TEXT,
    summary TEXT NOT NULL DEFAULT '',
    suggestions TEXT NOT NULL DEFAULT '',
    predictions TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(file_id) REFERENCES file_inventory(file_id) ON DELETE CASCADE,
    FOREIGN KEY(last_run_id) REFERENCES audit_runs(run_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_findings (
    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    run_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    details TEXT NOT NULL,
    suggested_fix TEXT NOT NULL DEFAULT '',
    prediction TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(file_id) REFERENCES file_inventory(file_id) ON DELETE CASCADE,
    FOREIGN KEY(run_id) REFERENCES audit_runs(run_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_file_inventory_domain
    ON file_inventory(domain, subdomain, priority_tier);

CREATE INDEX IF NOT EXISTS idx_file_audit_status_review
    ON file_audit_status(review_status, correctness_status, quality_status);

CREATE INDEX IF NOT EXISTS idx_audit_findings_file
    ON audit_findings(file_id, severity);
