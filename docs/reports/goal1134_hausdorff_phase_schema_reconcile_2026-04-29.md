# Goal1134 Hausdorff Phase-Schema Reconciliation

Date: 2026-04-29

## Scope

Goal1134 resolves the non-blocking follow-up from the Goal1132 and Goal1133
Claude reviews: Goal887's cloud profiler phase names are not the same as the
Goal1132 app-level `run_phases` names.

This goal clarifies the schema relationship. It does not change public RTX
wording and does not promote Hausdorff speedup claims.

## Implementation

- `scripts/goal887_prepared_decision_phase_profiler.py` now marks every prepared
  decision contract with `schema_scope: goal887_profiler_payload`.
- For `hausdorff_threshold`, the cloud claim contract now includes
  `app_level_phase_aliases` mapping Goal887 profiler fields to Goal1132
  app-level fields.
- `point_pack_sec` and `optix_close_sec` are explicitly labeled
  profiler-only phases that are not emitted by `run_app`.
- A `phase_schema_note` states that Goal887 required phase groups describe the
  profiler payload, not the app payload.

## Evidence

- Probe artifact:
  `docs/reports/goal1134_hausdorff_goal887_schema_probe_2026-04-29.json`
- Test:
  `tests/goal1134_hausdorff_phase_schema_reconcile_test.py`

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1134_hausdorff_phase_schema_reconcile_test \
  tests.goal887_prepared_decision_phase_profiler_test -v

Ran 9 tests in 2.363s
OK
```

## Boundary

This is a schema clarification only. Hausdorff public RTX speedup remains
blocked until meaningful same-semantics baseline evidence and 2-AI review exist.
