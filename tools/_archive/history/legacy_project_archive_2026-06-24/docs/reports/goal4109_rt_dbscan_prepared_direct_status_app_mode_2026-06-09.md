# Goal4109 - RT-DBSCAN Prepared Direct Status App Mode

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4108 proved that the prepared direct-status union handle is the right reuse path for the RT-DBSCAN partition-convergence candidate. Goal4109 exposes that path through the benchmark app so users can run it as an explicit mode instead of only through a timing script.

New app mode:

`partner_cupy_prepared_direct_status_union_component_signature_3d`

The mode is still graph-component-signature only. It is not full DBSCAN core/border/noise semantics, not the current default route, and not an automatic dispatcher choice.

## Implementation

The new mode calls:

- `prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(...)`
- `run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(...)`

It records:

- `prepared_direct_status_union_app_mode: true`
- `prepared_direct_status_union_reused: true`
- `materializes_partition_pair_rows: false`
- `materializes_near_pair_columns: false`
- `pair_materialization_avoided: true`
- `graph_component_contract_only: true`
- `full_dbscan_semantics: false`
- `partition_convergence_hybrid_promoted: false`

## Pod Smoke

Artifacts:

- `docs/reports/goal4109_prepared_direct_status_app_mode_tiny_pod.json`
- `docs/reports/goal4109_prepared_direct_status_app_mode_clustered65536_pod.json`

Pod setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `19dc8376`

Smoke rows:

| Dataset | Point count | Validate | Elapsed (s) | Prepare (s) | Signature (s) | Pair materialization avoided |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| tiny | 9 | yes | 0.531371 | 0.446152 | 0.067556 | yes |
| clustered3d | 65,536 | no | 0.560136 | 0.503871 | 0.056235 | yes |

The large app-mode smoke confirms the explicit mode works at benchmark scale. It does not replace Goal4108's prepared replay timing, because this one-shot app CLI still includes the one-time prepare phase.

## Boundary

This report does not promote `partition_convergence_hybrid` as a default route. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, or true-zero-copy claims.
