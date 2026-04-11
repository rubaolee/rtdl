from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "build" / "system_audit" / "rtdl_system_audit.sqlite"


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a system audit pass into the RTDL audit database.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--scope-label", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--status-json", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.status_json.read_text(encoding="utf-8"))
    conn = sqlite3.connect(args.db)
    try:
        commit = (
            __import__("subprocess")
            .check_output(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True)
            .strip()
        )
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO audit_runs (created_at_utc, repo_root, git_commit, scope_label, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (created_at, str(REPO_ROOT), commit, args.scope_label, args.notes),
        )
        run_id = cur.lastrowid

        for item in payload["files"]:
            row = cur.execute("SELECT file_id FROM file_inventory WHERE path = ?", (item["path"],)).fetchone()
            if row is None:
                raise SystemExit(f"unknown tracked file: {item['path']}")
            file_id = row[0]
            cur.execute(
                """
                UPDATE file_audit_status
                SET review_status = ?,
                    correctness_status = ?,
                    quality_status = ?,
                    link_status = ?,
                    duplication_status = ?,
                    acronym_status = ?,
                    release_relevance = ?,
                    reviewer = ?,
                    last_run_id = ?,
                    reviewed_at_utc = ?,
                    summary = ?,
                    suggestions = ?,
                    predictions = ?
                WHERE file_id = ?
                """,
                (
                    item.get("review_status", "reviewed"),
                    item.get("correctness_status", "pass"),
                    item.get("quality_status", "pass"),
                    item.get("link_status", "pass"),
                    item.get("duplication_status", "pass"),
                    item.get("acronym_status", "pass"),
                    item.get("release_relevance", "critical"),
                    args.reviewer,
                    run_id,
                    created_at,
                    item.get("summary", ""),
                    item.get("suggestions", ""),
                    item.get("predictions", ""),
                    file_id,
                ),
            )
            for finding in item.get("findings", []):
                cur.execute(
                    """
                    INSERT INTO audit_findings
                    (file_id, run_id, severity, category, title, details, suggested_fix, prediction)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        file_id,
                        run_id,
                        finding["severity"],
                        finding["category"],
                        finding["title"],
                        finding["details"],
                        finding.get("suggested_fix", ""),
                        finding.get("prediction", ""),
                    ),
                )
        conn.commit()
        print(f"recorded run_id={run_id} files={len(payload['files'])}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
