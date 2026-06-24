# Goal1020 Public Docs RTX Boundary Refresh

Date: 2026-04-26

## Problem

The latest RTX wording work made `rtdsl.rtx_public_wording_matrix()` the
release-facing source of truth, but public docs still needed a focused audit
covering the front page, example index, app catalog, feature guide, RTX status
page, support matrix, and quick tutorial.

The highest-risk wording was `robot_collision_screening`: it is a real bounded
RT-core path, but public RTX speedup wording remains blocked because larger
repeats stayed below the 100 ms public-review timing floor.

## Changes

Updated public docs:

- `docs/release_facing_examples.md`
- `docs/application_catalog.md`
- `docs/rtdl_feature_guide.md`

Added audit:

- `scripts/goal1020_public_docs_rtx_boundary_audit.py`
- `tests/goal1020_public_docs_rtx_boundary_audit_test.py`

Generated artifacts:

- `docs/reports/goal1020_public_docs_rtx_boundary_audit_2026-04-26.json`
- `docs/reports/goal1020_public_docs_rtx_boundary_audit_2026-04-26.md`

## Invariants

- Public docs distinguish `--backend optix` from an NVIDIA RT-core claim.
- Public docs point RTX wording back to `rtdsl.rtx_public_wording_matrix()`
  where release-facing wording is involved.
- Public docs state that bounded RTX paths are not broad or whole-app speedup
  claims.
- Public docs state that `robot_collision_screening / prepared_pose_flags`
  remains blocked for public RTX speedup wording under the 100 ms evidence
  gate.
- This goal authorizes no public speedup claim.

## Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1020_public_docs_rtx_boundary_audit_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal512_public_doc_smoke_audit_test \
  tests.goal655_tutorial_example_current_main_consistency_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal1011_rtx_public_wording_matrix_test -v
```

Result: 23 tests OK.

## Boundary

This is a public documentation consistency refresh only. It does not collect new
RTX evidence and does not authorize public speedup wording.
