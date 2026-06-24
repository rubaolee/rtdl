# Goal1348 Current-State Full-Suite Sync

Date: 2026-05-06

This report records a local current-state test repair after the Goal1341-Goal1347 public-matrix sync batch.

## Scope

- Updated stale test expectations from `v0.9.8` to current released `v1.0` where tests inspect live public front-page docs.
- Updated active current-state RTX wording-count expectations to 13 reviewed rows and 1 blocked row after the Goal1263 polygon-pair promotion.
- Preserved historical baseline artifact JSON and release-candidate artifacts; tests now reflect that polygon pair and Jaccard baseline packages are pending when older metric-scope artifacts no longer match the tightened candidate-only plan.
- Appended v1.0 history catch-up entries to `history/COMPLETE_HISTORY.md` and `history/revision_dashboard.md` instead of rewriting old history.
- Aligned Vulkan compact-summary behavior with the standing frozen-before-v2.1 policy.
- Aligned polygon Jaccard CPU/native parity tests with generic-summary metadata now attached to native paths.

## Local Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
```

Result:

- Ran 2627 tests.
- Skipped 197 tests.
- Result: OK.

Additional checks:

```bash
git diff --check
```

Result: OK.

## Boundary

This is a local current-state test and documentation sync. It does not tag, release, move `v1.0`, authorize public v1.5 wording, or rewrite historical benchmark artifacts.
