# Goal 241 Report: System-Level Audit Database

Date: 2026-04-11
Status: implemented

## Summary

This goal creates the first durable system-level audit database for the RTDL
repository. It is designed to support full-file review from the beginning of
the project to the current `v0.4.0` release state.

It does not claim that all files are already fully reviewed. It creates the
database and inventory structure required to do that work in an organized way.

## Files Added

- `[REPO_ROOT]/schemas/system_audit_schema.sql`
- `[REPO_ROOT]/scripts/build_system_audit_db.py`
- `[REPO_ROOT]/docs/goal_241_system_level_audit_database.md`
- `[REPO_ROOT]/docs/reports/goal241_system_level_audit_database_2026-04-11.md`

Generated artifacts:

- `[REPO_ROOT]/build/system_audit/rtdl_system_audit.sqlite`
- `[REPO_ROOT]/build/system_audit/summary.json`

## Database Structure

Main tables:

- `audit_runs`
  - records each inventory/review run
- `file_inventory`
  - one row per tracked file in scope
- `file_audit_status`
  - one current audit-state row per file
- `audit_findings`
  - detailed findings linked to file and run

Tracked status fields include:

- `review_status`
- `correctness_status`
- `quality_status`
- `link_status`
- `duplication_status`
- `acronym_status`
- `release_relevance`
- `summary`
- `suggestions`
- `predictions`

## Inventory Scope

Current inventory scope:

- `README.md`
- `VERSION`
- `docs/`
- `src/`
- `tests/`
- `examples/`
- `scripts/`
- `apps/`

## Current Inventory Counts

Initial tracked file count:

- `1488`

Initial seeded reviewed files:

- `9`

By top-level domain:

- `root`: `2`
- `docs`: `1191`
- `examples`: `57`
- `scripts`: `58`
- `src`: `57`
- `tests`: `119`
- `apps`: `4`

## Priority Model

The database encodes the review priority order:

- tier `1`: front page / release anchors
- tier `2`: tutorials
- tier `3`: docs
- tier `4`: examples
- tier `5`: code-facing surface
- tier `6`: tests / reports / lower-priority history

This allows later audit passes to query the system in the correct user-facing
order instead of auditing the repo flatly.

## Honest Boundary

This goal creates the audit system and seeds the inventory. It does not yet
mark all files as reviewed.

The first seeded reviewed layer covers the highest-priority release-facing
surface:

- `README.md`
- `docs/README.md`
- `docs/quick_tutorial.md`
- `docs/tutorials/README.md`
- `docs/release_facing_examples.md`
- `docs/v0_4_application_examples.md`
- `docs/release_reports/v0_4/README.md`
- `docs/release_reports/v0_4/release_statement.md`
- `docs/release_reports/v0_4/support_matrix.md`

That next work should happen as staged review passes writing into the database
rather than as disconnected prose reports.
