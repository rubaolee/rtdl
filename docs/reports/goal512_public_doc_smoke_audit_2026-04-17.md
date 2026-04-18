# Goal 512: Public Documentation Smoke Audit

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

Goal512 adds a lightweight public-documentation smoke audit after Goals 510 and
511. The purpose is to catch broad public-surface drift across the docs a new
user is most likely to read.

## Public Docs Covered

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/v0_8_app_building.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

## Changes Made

- Standardized `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
  from "in-progress `v0.8` app-building line" to "accepted `v0.8`
  app-building line on `main`" so it matches the rest of the public docs.
- Added `/Users/rl2025/rtdl_python_only/tests/goal512_public_doc_smoke_audit_test.py`.

## Test Coverage Added

The new test checks:

- the main public docs do not call v0.8 a released line
- the main public docs do not use stale "in-progress `v0.8`" wording
- the combined public surface preserves the required Goal507/Goal509 boundaries
- local Markdown links in the public docs resolve

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal512_public_doc_smoke_audit_test tests.goal511_feature_guide_v08_refresh_test tests.goal510_app_perf_doc_refresh_test -v
```

Result: `Ran 9 tests`, `OK`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile tests/goal512_public_doc_smoke_audit_test.py && git diff --check
```

Result: passed.

## Current Verdict

Goal512 is accepted. The public-doc smoke audit is now in place and the only
detected wording inconsistency has been fixed.

## AI Review Consensus

- Claude review: `PASS`; the audit correctly guards v0.8 status wording,
  Goal507/Goal509 boundaries, and local Markdown link resolution without
  overclaiming release status.
- Gemini Flash review: `ACCEPT`.
- Codex conclusion: `ACCEPT`; Goal512 adds a useful broad public-doc smoke gate
  after the focused Goal510 and Goal511 refreshes.
