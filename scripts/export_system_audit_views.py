from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "build" / "system_audit" / "rtdl_system_audit.sqlite"
DEFAULT_OUTDIR = REPO_ROOT / "build" / "system_audit" / "views"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export system audit summary views.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(args.db)
    try:
        conn.row_factory = sqlite3.Row
        rows = list(
            conn.execute(
                """
                SELECT fi.path, fi.domain, fi.subdomain, fi.priority_tier,
                       fas.review_status, fas.correctness_status, fas.quality_status,
                       fas.link_status, fas.duplication_status, fas.acronym_status,
                       fas.release_relevance, fas.reviewer, fas.reviewed_at_utc
                FROM file_inventory fi
                JOIN file_audit_status fas ON fi.file_id = fas.file_id
                ORDER BY fi.priority_tier, fi.domain, fi.path
                """
            )
        )
        with (args.outdir / "file_status.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(rows[0].keys() if rows else [])
            for row in rows:
                writer.writerow(list(row))

        summary = {
            "by_review_status": {
                row["review_status"]: row["count"]
                for row in conn.execute("SELECT review_status, COUNT(*) AS count FROM file_audit_status GROUP BY review_status")
            },
            "by_priority_and_review": [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT fi.priority_tier, fas.review_status, COUNT(*) AS count
                    FROM file_inventory fi
                    JOIN file_audit_status fas ON fi.file_id = fas.file_id
                    GROUP BY fi.priority_tier, fas.review_status
                    ORDER BY fi.priority_tier, fas.review_status
                    """
                )
            ],
            "recent_runs": [dict(row) for row in conn.execute("SELECT * FROM audit_runs ORDER BY run_id DESC LIMIT 10")],
        }
        (args.outdir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
