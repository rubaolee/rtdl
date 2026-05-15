# Goal2101 Frontpage Navigation Link Audit

Status: complete.

Purpose: browse the project like a new GitHub reader starting from the front
page, then verify that active learner/user navigation has no dead local links,
wrong moved-path links, or old-version clutter.

## Scope

Audited active public navigation files:

- `README.md`
- `examples/README.md`
- current `docs/*.md`
- `docs/learn/**`
- `docs/tutorials/**`
- `docs/features/**`
- `docs/rtdl/**`

Excluded from the active learner scan:

- `docs/reports/**`
- `docs/reviews/**`
- `docs/release_reports/**`
- `docs/handoff/**`
- `docs/history/**`
- `docs/audit/**`
- `docs/research/**`

Those excluded directories are audit/research/history stores. They can preserve
old paths, old release wording, and evidence-context references without
interrupting normal learners.

## Findings And Operations

| Area | Finding | Operation |
| --- | --- | --- |
| Active public links | 55 public Markdown files contained 384 local links. | Verified all active local links resolve. Broken link count: 0. |
| Active old-version markers | Initial scan found old-version wording in `performance_model.md`, `vision.md`, and archive-link labels. | Rewrote `performance_model.md` and `vision.md` as current v2.0-facing pages; changed active link labels to archive/version wording. |
| Top-level docs folders | `docs/archive`, `docs/directives`, `docs/proposals`, and `docs/technical_app_notes` were visible as old-looking top-level doors. | Moved them to `docs/history/release_archive`, `docs/audit/process/directives`, `docs/research/proposals`, and `docs/research/app_notes`. |
| Moved archive links | Release archive links needed new relative paths after moving under `docs/history`. | Fixed the release archive local links. |
| Technical app notes | The app quickstart still pointed to the old top-level technical notes path. | Updated it to `docs/research/app_notes/README.md`. |
| Tutorial archive | Active tutorial index linked to a `legacy_tutorials` path. | Renamed the archive path to `docs/history/tutorial_archive`. |
| Learner version notes | Active docs linked to a `legacy_learner_doc_version_notes` path. | Renamed it to `docs/history/learner_doc_version_notes.md`. |

## Final Scan Result

| Metric | Result |
| --- | ---: |
| Active public Markdown files scanned | 55 |
| Active local links checked | 384 |
| Broken active local links | 0 |
| Active old-version markers | 0 |

## Regression Gate

`tests/goal2101_frontpage_navigation_link_audit_test.py` now checks:

- active public local Markdown links resolve;
- active learner/user navigation has no old-version markers;
- old topic directories do not reappear as top-level `docs/` doors.

## Boundary

This audit does not rewrite old evidence stores. Historical reports, reviews,
handoffs, and release reports may intentionally preserve old paths and old
release context. The rule enforced here is that a normal learner navigating from
the front page gets a clean current v2.0-facing path.

