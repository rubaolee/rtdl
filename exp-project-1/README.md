# exp-project-1

This directory is an isolated experimental workspace for post-v2.14 RTDL
research. It is not part of the public v2.14 product surface.

The repository root remains the v2.14 user-facing project. Read this directory
only if you want the experimental project record.

## Snapshot

- archived branch: `codex/v4-tier2-section8`
- archived commit: `35e295a83d2186f717276babc649b94a17659a22`
- public root tag: `v2.14`
- public root commit: `03a3201c04d391f8f08148da14445d4cd1b1149c`
- created: 2026-06-30

## Contents

- `MIGRATION_RECORD_2026-06-30.md`: migration and verification record.
- `untracked-current/`: reports, reviews, scripts, and other local experiment
  material that was not already tracked.

## Recovering the Archived Tracked Source

The full tracked source snapshot is available from git history:

```bash
git show --stat 35e295a83d2186f717276babc649b94a17659a22
git switch codex/v4-tier2-section8
```

A local-only `current-head-source.tar` may exist beside this README on the
machine that performed the migration. It is intentionally ignored and is not
published to the repository because it is too large for a normal source tree.
