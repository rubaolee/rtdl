# Goal993 RTX Manifest Scalar Command Sync

Date: 2026-04-26

## Scope

Synchronize the next paid RTX cloud-run contract with the Goal992 public scalar
fixed-radius app modes:

- Outlier detection claim-facing path: `density_count`
- DBSCAN claim-facing path: `core_count`
- Shared cloud profiler mode: `scripts/goal757_optix_fixed_radius_prepared_perf.py --result-mode threshold_count`

Historical manifest path identifiers remain unchanged:

- `prepared_fixed_radius_density_summary`
- `prepared_fixed_radius_core_flags`

Those identifiers are retained because older cloud artifacts, copyback scripts,
and review packets use them as stable row IDs. The semantics under those row IDs
are now documented as scalar count paths, not per-point summaries.

## Changes

- `scripts/goal759_rtx_cloud_benchmark_manifest.py` now describes outlier as
  `prepared fixed-radius scalar threshold-count traversal only`.
- `scripts/goal759_rtx_cloud_benchmark_manifest.py` now describes DBSCAN as
  `prepared fixed-radius scalar core-count traversal only`.
- `scripts/goal757_optix_fixed_radius_prepared_perf.py` now emits matching
  cloud claim contract text.
- `docs/rtx_cloud_single_session_runbook.md` now names Group B
  `Fixed-Radius Scalar Counts` and explicitly maps the shared profiler to
  public `density_count` and `core_count` app modes.
- `docs/reports/goal962_next_rtx_pod_execution_packet_2026-04-25.md` received
  the same Group B scalar wording so the next pod instruction packet is not
  stale.
- Contract tests were updated to reject the old per-point summary wording in
  current manifest/runbook surfaces.
- The generated manifest JSON was refreshed:
  `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`.
- A dry-run Group B packet was generated:
  `docs/reports/goal993_group_b_fixed_radius_scalar_dry_run_2026-04-26.json`.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal827_cloud_artifact_contract_audit_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal962_next_rtx_pod_execution_packet_test \
  tests.goal757_prepared_optix_fixed_radius_count_test
```

Result: `Ran 68 tests in 2.976s`, `OK (skipped=2)`.

Additional checks:

```bash
python3 -m py_compile \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal757_optix_fixed_radius_prepared_perf.py \
  scripts/goal761_rtx_cloud_run_all.py

git diff --check

rg -n "Group B: Fixed-Radius Summaries|prepared fixed-radius threshold summary|prepared fixed-radius core-flag traversal only|core-flag summary traversal|threshold summary traversal" \
  scripts tests docs/rtx_cloud_single_session_runbook.md \
  docs/reports/goal962_next_rtx_pod_execution_packet_2026-04-25.md \
  docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json \
  docs/reports/goal993_group_b_fixed_radius_scalar_dry_run_2026-04-26.json
```

Results: compile passed, `git diff --check` passed, stale-current-surface grep
returned no matches.

## Boundary

This goal updates local run contracts and documentation. It does not authorize a
public RTX speedup claim, does not claim per-point outlier/core-flag output is
the fast scalar path, and does not change backend kernels.
