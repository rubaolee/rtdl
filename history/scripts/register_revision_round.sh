#!/bin/zsh
set -euo pipefail

sql_escape() {
  printf "%s" "$1" | sed "s/'/''/g"
}

html_escape() {
  printf "%s" "$1" | \
    sed -e 's/&/\&amp;/g' \
        -e 's/</\&lt;/g' \
        -e 's/>/\&gt;/g' \
        -e 's/"/\&quot;/g'
}

if [[ $# -lt 10 ]]; then
  echo "usage: $0 <repo_root> <round_slug> <title> <version> <status> <started_on> <source_commit> <gemini_review> <codex_revision> <final_result> [summary] [file ...]" >&2
  exit 1
fi

repo_root="$1"
round_slug="$2"
title="$3"
version="$4"
round_status="$5"
started_on="$6"
source_commit="$7"
gemini_review="$8"
codex_revision="$9"
final_result="${10}"
shift 10

summary="$title"
if [[ $# -gt 0 && ! -f "$1" ]]; then
  summary="$1"
  shift 1
fi

history_dir="$repo_root/history"
db_path="$history_dir/history.db"
round_dir="$history_dir/revisions/$round_slug"
external_dir="$round_dir/external_reports"
snapshot_dir="$round_dir/project_snapshot"
dashboard_path="$history_dir/revision_dashboard.html"
ledger_path="$history_dir/revision_dashboard.md"

mkdir -p "$external_dir" "$snapshot_dir"
sqlite3 "$db_path" < "$history_dir/schema.sql"

sqlite3 "$db_path" <<SQL
INSERT OR IGNORE INTO revision_rounds (slug, title, started_on, closed_on, source_commit, summary)
VALUES (
  '$(sql_escape "$round_slug")',
  '$(sql_escape "$title")',
  '$(sql_escape "$started_on")',
  '$(sql_escape "$started_on")',
  '$(sql_escape "$source_commit")',
  '$(sql_escape "$summary")'
);
SQL

round_id="$(sqlite3 "$db_path" "SELECT id FROM revision_rounds WHERE slug = '$round_slug';")"

sqlite3 "$db_path" <<SQL
INSERT INTO revision_round_status (round_id, version, status, gemini_review, codex_revision, final_result)
VALUES (
  $round_id,
  '$(sql_escape "$version")',
  '$(sql_escape "$round_status")',
  '$(sql_escape "$gemini_review")',
  '$(sql_escape "$codex_revision")',
  '$(sql_escape "$final_result")'
)
ON CONFLICT(round_id) DO UPDATE SET
  version = excluded.version,
  status = excluded.status,
  gemini_review = excluded.gemini_review,
  codex_revision = excluded.codex_revision,
  final_result = excluded.final_result;
SQL

for file_path in "$@"; do
  if [[ ! -f "$file_path" ]]; then
    echo "warning: skipping missing file: $file_path" >&2
    continue
  fi

  base_name="$(basename "$file_path")"
  archive_subdir="$snapshot_dir"
  category="project_snapshot"

  case "$file_path" in
    /Users/rl2025/gemini-work/*)
      archive_subdir="$external_dir"
      category="external_report"
      ;;
    "$history_dir"/ad_hoc_reviews/*)
      archive_subdir="$external_dir"
      category="external_report"
      ;;
    "$round_dir"/external_reports/*)
      archive_subdir="$external_dir"
      category="external_report"
      ;;
  esac

  archive_path="$archive_subdir/$base_name"
  if [[ "$file_path" != "$archive_path" ]]; then
    cp "$file_path" "$archive_path"
  fi
  checksum="$(shasum -a 256 "$archive_path" | awk '{print $1}')"

  sqlite3 "$db_path" <<SQL
INSERT OR IGNORE INTO archived_files (round_id, category, label, source_path, archive_path, sha256)
VALUES (
  $round_id,
  '$(sql_escape "$category")',
  '$(sql_escape "$base_name")',
  '$(sql_escape "$file_path")',
  '$(sql_escape "$archive_path")',
  '$(sql_escape "$checksum")'
);
SQL
done

cat > "$round_dir/metadata.txt" <<EOF
slug: $round_slug
title: $title
version: $version
status: $round_status
started_on: $started_on
closed_on: $started_on
source_commit: $source_commit
gemini_review: $gemini_review
codex_revision: $codex_revision
final_result: $final_result
summary: $summary
EOF

total_rounds="$(sqlite3 "$db_path" "SELECT COUNT(*) FROM revision_rounds;")"
total_archived_files="$(sqlite3 "$db_path" "SELECT COUNT(*) FROM archived_files;")"
total_external_reports="$(sqlite3 "$db_path" "SELECT COUNT(*) FROM archived_files WHERE category = 'external_report';")"
total_project_snapshots="$(sqlite3 "$db_path" "SELECT COUNT(*) FROM archived_files WHERE category = 'project_snapshot';")"

cat > "$dashboard_path" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RTDL Revision Dashboard</title>
  <style>
    :root {
      --bg: #f4efe5;
      --panel: #fffdf8;
      --ink: #1e1b18;
      --muted: #6d655c;
      --line: #d7cabb;
      --accent: #0f766e;
      --accent-soft: #d7f3ee;
      --warn: #a16207;
      --warn-soft: #fdf1c7;
      --shadow: 0 18px 40px rgba(44, 33, 20, 0.08);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.12), transparent 28rem),
        linear-gradient(180deg, #fbf7f0 0%, var(--bg) 100%);
      color: var(--ink);
    }

    .page {
      max-width: 1280px;
      margin: 0 auto;
      padding: 40px 28px 56px;
    }

    .hero {
      display: grid;
      gap: 18px;
      margin-bottom: 28px;
    }

    .eyebrow {
      margin: 0;
      color: var(--accent);
      font-size: 0.92rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 700;
    }

    h1 {
      margin: 0;
      font-size: clamp(2.2rem, 4vw, 4rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
      max-width: 12ch;
    }

    .lead {
      margin: 0;
      max-width: 56rem;
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.6;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 14px;
      margin: 24px 0 32px;
    }

    .stat {
      background: rgba(255, 253, 248, 0.82);
      border: 1px solid rgba(215, 202, 187, 0.9);
      border-radius: 18px;
      padding: 18px 18px 16px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }

    .stat-label {
      display: block;
      color: var(--muted);
      font-size: 0.86rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }

    .stat-value {
      display: block;
      font-size: 2rem;
      line-height: 1;
      font-weight: 700;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .panel-head {
      padding: 22px 24px 12px;
      border-bottom: 1px solid rgba(215, 202, 187, 0.7);
    }

    .panel-head h2 {
      margin: 0 0 6px;
      font-size: 1.25rem;
      letter-spacing: -0.02em;
    }

    .panel-head p {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }

    .table-wrap {
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 980px;
    }

    th, td {
      padding: 16px 18px;
      text-align: left;
      vertical-align: top;
      border-bottom: 1px solid rgba(215, 202, 187, 0.65);
    }

    th {
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      background: #faf3e8;
    }

    tr:last-child td {
      border-bottom: 0;
    }

    .status {
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.84rem;
      font-weight: 700;
      white-space: nowrap;
    }

    .summary-cell {
      min-width: 16rem;
      line-height: 1.45;
    }

    code {
      font-family: "SFMono-Regular", "Menlo", "Consolas", monospace;
      font-size: 0.9em;
      background: #f4efe6;
      padding: 2px 6px;
      border-radius: 6px;
    }

    .footer {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    @media (max-width: 720px) {
      .page { padding: 24px 14px 40px; }
      .panel-head, th, td { padding-left: 14px; padding-right: 14px; }
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">RTDL History</p>
      <h1>Revision Dashboard</h1>
      <p class="lead">Manager-facing summary of RTDL review and revision rounds. The table below is generated directly from <code>history/history.db</code> so the HTML file stays readable while SQLite remains the source of truth.</p>
    </section>

    <section class="stats">
      <article class="stat">
        <span class="stat-label">Revision Rounds</span>
        <span class="stat-value">$total_rounds</span>
      </article>
      <article class="stat">
        <span class="stat-label">Archived Files</span>
        <span class="stat-value">$total_archived_files</span>
      </article>
      <article class="stat">
        <span class="stat-label">External Reports</span>
        <span class="stat-value">$total_external_reports</span>
      </article>
      <article class="stat">
        <span class="stat-label">Project Snapshots</span>
        <span class="stat-value">$total_project_snapshots</span>
      </article>
    </section>

    <section class="panel">
      <header class="panel-head">
        <h2>Round Summary</h2>
        <p>Each row represents one completed review/revision round, including the version tag, review outcome, Codex response, and final project status.</p>
      </header>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Version</th>
              <th>Date</th>
              <th>Status</th>
              <th>Round</th>
              <th>Gemini Review</th>
              <th>Codex Revision</th>
              <th>Final Result</th>
              <th>Commit</th>
              <th>Archive</th>
            </tr>
          </thead>
          <tbody>
EOF

cat > "$ledger_path" <<'EOF'
# Revision Dashboard

Manager-facing summary of RTDL review and revision rounds. This Markdown file is generated from `history/history.db` for direct reading on GitHub. The richer browser view remains available in `history/revision_dashboard.html`.

## Summary

EOF

printf -- "- Revision rounds: %s\n" "$total_rounds" >> "$ledger_path"
printf -- "- Archived files: %s\n" "$total_archived_files" >> "$ledger_path"
printf -- "- External reports: %s\n" "$total_external_reports" >> "$ledger_path"
printf -- "- Project snapshots: %s\n\n" "$total_project_snapshots" >> "$ledger_path"

cat >> "$ledger_path" <<'EOF'
## Rounds

| Version | Date | Status | Round | Gemini Review | Codex Revision | Final Result | Commit | Archive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
EOF

sqlite3 -separator '|' "$db_path" <<SQL | while IFS='|' read -r db_version db_started_on db_status db_title db_gemini_review db_codex_revision db_final_result db_source_commit db_slug; do
SELECT
  revision_round_status.version,
  revision_rounds.started_on,
  revision_round_status.status,
  revision_rounds.title,
  revision_round_status.gemini_review,
  revision_round_status.codex_revision,
  revision_round_status.final_result,
  revision_rounds.source_commit,
  revision_rounds.slug
FROM revision_rounds
JOIN revision_round_status ON revision_round_status.round_id = revision_rounds.id
ORDER BY revision_rounds.started_on DESC, revision_rounds.id DESC;
SQL
  printf '            <tr>\n' >> "$dashboard_path"
  printf '              <td><strong>%s</strong></td>\n' "$(html_escape "$db_version")" >> "$dashboard_path"
  printf '              <td>%s</td>\n' "$(html_escape "$db_started_on")" >> "$dashboard_path"
  printf '              <td><span class="status">%s</span></td>\n' "$(html_escape "$db_status")" >> "$dashboard_path"
  printf '              <td class="summary-cell">%s</td>\n' "$(html_escape "$db_title")" >> "$dashboard_path"
  printf '              <td class="summary-cell">%s</td>\n' "$(html_escape "$db_gemini_review")" >> "$dashboard_path"
  printf '              <td class="summary-cell">%s</td>\n' "$(html_escape "$db_codex_revision")" >> "$dashboard_path"
  printf '              <td class="summary-cell">%s</td>\n' "$(html_escape "$db_final_result")" >> "$dashboard_path"
  printf '              <td><code>%s</code></td>\n' "$(html_escape "$db_source_commit")" >> "$dashboard_path"
  printf '              <td><code>%s</code></td>\n' "$(html_escape "$db_slug")" >> "$dashboard_path"
  printf '            </tr>\n' >> "$dashboard_path"
  printf '| %s | %s | %s | %s | %s | %s | %s | `%s` | `%s` |\n' \
    "$db_version" \
    "$db_started_on" \
    "$db_status" \
    "$db_title" \
    "$db_gemini_review" \
    "$db_codex_revision" \
    "$db_final_result" \
    "$db_source_commit" \
    "$db_slug" >> "$ledger_path"
done

cat >> "$dashboard_path" <<'EOF'
          </tbody>
        </table>
      </div>
    </section>

    <p class="footer">Generated by <code>history/scripts/register_revision_round.sh</code>. Update the SQLite archive first, then regenerate this HTML summary from the database.</p>
  </main>
</body>
</html>
EOF
