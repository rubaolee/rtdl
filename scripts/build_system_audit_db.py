from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "build" / "system_audit" / "rtdl_system_audit.sqlite"
DEFAULT_SUMMARY = REPO_ROOT / "build" / "system_audit" / "summary.json"
SCHEMA_PATH = REPO_ROOT / "schemas" / "system_audit_schema.sql"


FRONT_SURFACE = {
    "README.md",
    "docs/README.md",
    "docs/quick_tutorial.md",
    "docs/tutorials/README.md",
    "docs/release_facing_examples.md",
    "docs/v0_4_application_examples.md",
    "docs/release_reports/v0_4/README.md",
    "docs/release_reports/v0_4/release_statement.md",
    "examples/README.md",
}


ACTIVE_RELEASE_SURFACE_PREFIXES = (
    "docs/tutorials/",
    "docs/features/",
    "docs/release_reports/v0_4/",
    "examples/",
    "src/rtdsl/",
    "src/native/",
)


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", "-C", str(REPO_ROOT), *args], text=True).strip()


def tracked_files() -> list[Path]:
    lines = git(["ls-files", "README.md", "VERSION", "docs", "src", "tests", "examples", "scripts", "apps"]).splitlines()
    return [REPO_ROOT / line for line in lines if line]


def classify(rel_path: str) -> tuple[str, str, int]:
    if rel_path == "README.md":
        return ("root", "front_page", 1)
    if rel_path == "VERSION":
        return ("root", "release_anchor", 5)
    if rel_path.startswith("docs/tutorials/") or rel_path == "docs/quick_tutorial.md":
        return ("docs", "tutorials", 2)
    if rel_path.startswith("docs/"):
        return ("docs", "docs", 3)
    if rel_path.startswith("examples/"):
        return ("examples", "examples", 4)
    if rel_path.startswith(("src/", "apps/")):
        return ("code", "source", 5)
    if rel_path.startswith("scripts/"):
        return ("code", "scripts", 5)
    if rel_path.startswith("tests/"):
        return ("verification", "tests", 6)
    return ("other", "other", 6)


def line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    payload = path.read_bytes()
    if not payload:
        return 0
    return payload.count(b"\n") + 1


def build_database(db_path: Path) -> dict[str, object]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        commit = git(["rev-parse", "HEAD"])
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_runs (created_at_utc, repo_root, git_commit, scope_label, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                created_at,
                str(REPO_ROOT),
                commit,
                "system_level_audit_inventory",
                "Initial full-system file inventory for v0.4.0 audit program.",
            ),
        )
        run_id = cursor.lastrowid

        files = tracked_files()
        for path in files:
            rel_path = path.relative_to(REPO_ROOT).as_posix()
            domain, subdomain, tier = classify(rel_path)
            front = 1 if rel_path in FRONT_SURFACE else 0
            active = 1 if rel_path in FRONT_SURFACE or rel_path.startswith(ACTIVE_RELEASE_SURFACE_PREFIXES) else 0
            cursor.execute(
                """
                INSERT INTO file_inventory
                (path, domain, subdomain, priority_tier, extension, line_count, size_bytes,
                 is_front_surface, is_active_release_surface, exists_on_disk)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    rel_path,
                    domain,
                    subdomain,
                    tier,
                    path.suffix.lower(),
                    line_count(path),
                    path.stat().st_size if path.exists() else 0,
                    front,
                    active,
                ),
            )

        file_ids = [(row[0],) for row in cursor.execute("SELECT file_id FROM file_inventory")]
        cursor.executemany("INSERT INTO file_audit_status (file_id) VALUES (?)", file_ids)
        conn.commit()

        summary = {
            "repo_root": str(REPO_ROOT),
            "git_commit": commit,
            "run_id": run_id,
            "created_at_utc": created_at,
            "file_count": cursor.execute("SELECT COUNT(*) FROM file_inventory").fetchone()[0],
            "front_surface_count": cursor.execute("SELECT COUNT(*) FROM file_inventory WHERE is_front_surface = 1").fetchone()[0],
            "active_release_surface_count": cursor.execute(
                "SELECT COUNT(*) FROM file_inventory WHERE is_active_release_surface = 1"
            ).fetchone()[0],
            "counts_by_domain": {
                row[0]: row[1]
                for row in cursor.execute("SELECT domain, COUNT(*) FROM file_inventory GROUP BY domain ORDER BY domain")
            },
            "counts_by_tier": {
                str(row[0]): row[1]
                for row in cursor.execute("SELECT priority_tier, COUNT(*) FROM file_inventory GROUP BY priority_tier ORDER BY priority_tier")
            },
        }
        return summary
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the RTDL system audit inventory database.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = build_database(args.db)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
