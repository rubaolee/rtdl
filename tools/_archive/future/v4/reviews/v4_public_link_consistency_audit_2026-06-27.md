# V4 Public Link Consistency Audit

Date: 2026-06-27

Scope: the current user-facing Markdown surface:

- `README.md`
- `docs/**/*.md`
- `tutorials/**/*.md`
- `examples/**/*.md`

The audit excludes `history/` and `future/` as public reading surfaces. They are
repository memory and maintainer provenance, not links a new V4 user should
follow from the front door.

## Link Policy

- Public Markdown may link only to current V4 docs, tutorials, examples, or
  portable external URLs.
- Public Markdown must not link users into `history/` or `future/`.
- Relative Markdown links must resolve inside the repository.
- Absolute local links and `file:///` links are not allowed in public Markdown.
- The first-time path is:
  `README.md -> docs/README.md -> tutorials/current/README.md -> examples/README.md`.

## Files Changed

| File | Action |
| --- | --- |
| `README.md` | Removed the `history/` repository-layout row from the public front page. |
| `docs/README.md` | Removed the active link to `../history`; kept the docs index focused on current V4. |
| `docs/public_documentation_map.md` | Removed the archive section and `../history` link from the first-time user map. |
| `docs/v4_engineering_summary.md` | Corrected the front-door link from local `README.md` to the project `../README.md`. |
| `examples/README.md` | Removed the old examples archive pointer so examples expose only `simple/`, `benchmark_apps/`, and `paper_reproduction/`. |
| `scripts/v4_universe_audit.py` | Added a public Markdown link audit: missing local targets, links escaping the repo, absolute local paths, and links to `history/` or `future/` now fail the public surface gate. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Strengthened the public-doc relative link test so links to `history/` or `future/` are rejected. |

## Files Verified Without Content Changes

| File | Link action |
| --- | --- |
| `docs/app_level_benchmark_summary.md` | Local links resolve to current operator catalog, benchmark examples, and tutorial path. |
| `docs/current_v4_status.md` | Local links resolve to current operator catalog and benchmark summary. |
| `docs/v4_release_notes.md` | Local links resolve to current status, catalog, partner choice, tutorials, examples, and benchmark summary. |
| `docs/learn/README.md` | Local links resolve to current tutorial path and learn reference files. |
| `docs/learn/operator_catalog.md` | No broken public Markdown links found. |
| `docs/learn/partner_choice.md` | No broken public Markdown links found. |
| `docs/learn/performance_wording.md` | No broken public Markdown links found. |
| `docs/learn/source_tree_doctor.md` | No broken public Markdown links found. |
| `tutorials/README.md` | Local link resolves to `tutorials/current/README.md`. |
| `tutorials/current/README.md` | Lesson links resolve within the current tutorial path. |
| `tutorials/current/01_first_run.md` | Next-link resolves to lesson 02. |
| `tutorials/current/02_hello_world.md` | Next-link resolves to lesson 03. |
| `tutorials/current/03_backend_choice.md` | Next-link resolves to lesson 04. |
| `tutorials/current/04_prepared_runtime.md` | Next-link resolves to lesson 05. |
| `tutorials/current/05_measurement_boundaries.md` | Links resolve to current performance wording and lesson 06. |
| `tutorials/current/06_benchmark_apps.md` | Next-link resolves to lesson 07. |
| `tutorials/current/07_partner_choice.md` | Link resolves back to the benchmark-app lesson. |
| `examples/benchmark_apps/README.md` | Local link resolves to the benchmark-app tutorial. |
| `examples/paper_reproduction/README.md` | No broken public Markdown links found. |
| `examples/simple/README.md` | No broken public Markdown links found. |

## Verification

Commands run from the repository root:

```powershell
py -3 scripts\v4_universe_audit.py
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test
```

Results:

- `scripts\v4_universe_audit.py`: `status: pass`
- `public_findings`: `[]`
- `public_link_findings`: `[]`
- `tests.v4_goal4640_public_docs_cleanup_test`: `Ran 13 tests ... OK`

## Release Meaning

The public V4 docs/examples/tutorials now form one consistent current V4 path.
Old material remains in archival/provenance directories but is not actively
linked from the current user path.
