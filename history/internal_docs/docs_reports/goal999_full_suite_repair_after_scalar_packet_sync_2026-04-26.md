# Goal999 Full-Suite Repair After Scalar Packet Sync

Date: 2026-04-26

## Scope

Repair stale local tests revealed by full `unittest` discovery after the
Goal992-Goal998 scalar fixed-radius wording and packet refresh work.

## Initial Failure

Full local discovery initially ran `1927` tests with `196` skips and failed in
four stale expectations:

- `tests/goal825_tier1_profiler_contract_test.py`
  - expected old fixed-radius threshold/core-flag wording.
- `tests/goal858_segment_polygon_docs_optix_boundary_test.py`
  - expected old Goal941 wording where current docs correctly cite Goal969.
- `tests/goal973_deferred_decision_baselines_test.py`
  - expected older post-Goal969 baseline counts of `7 / 4 / 6` instead of the
    current `17 / 0 / 0` complete-baseline state.

## Changes

- Updated Goal825 test expectations to require scalar threshold-count and
  scalar core-count claim scopes.
- Updated Goal858 test expectations to match the current Goal969 segment/polygon
  evidence wording.
- Updated Goal973 test expectations to match the current Goal971 package:
  - `same_semantics_baselines_complete_count`: `17`
  - `active_gate_limited_count`: `0`
  - `baseline_pending_count`: `0`
  - `public_speedup_claim_authorized_count`: `0`

## Verification

Focused repair gate:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal825_tier1_profiler_contract_test \
  tests.goal858_segment_polygon_docs_optix_boundary_test \
  tests.goal973_deferred_decision_baselines_test
python3 -m py_compile \
  scripts/goal757_optix_fixed_radius_prepared_perf.py \
  scripts/goal971_post_goal969_baseline_speedup_review_package.py
git diff --check
```

Result: `Ran 7 tests`, `OK`.

Full local discovery:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
```

Result: `Ran 1927 tests in 142.112s`, `OK (skipped=196)`.

## Boundary

This goal repairs stale tests and verifies the full local suite. It does not
change backend kernels, does not run cloud/GPU workloads, and does not authorize
public RTX speedup claims.
