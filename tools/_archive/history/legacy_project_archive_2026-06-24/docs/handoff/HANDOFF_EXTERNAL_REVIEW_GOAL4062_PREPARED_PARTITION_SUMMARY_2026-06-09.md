# External Review Handoff: Goal4062 Prepared Partition Summary Preview

Please independently review Goal4062 on current `main`.

## Context

Goal4062 adds an explicit CuPy prepared preview handle for the generic
fixed-radius partition-convergence summary:

- `V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D`
- `prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(...)`
- `run_v2_8_fixed_radius_partition_convergence_component_labels_cupy_prepared_preview_3d(...)`
- `run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(...)`

Purpose: make repeated component-label/signature probes reuse one prepared
partition-summary stream instead of rebuilding it implicitly. This is intended
as a generic runtime/reuse pattern, not an app-specific DBSCAN primitive and not
a promoted default route.

## Files To Inspect

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/__init__.py`
- `tests/goal4062_prepared_partition_convergence_summary_preview_test.py`
- `tests/goal4044_partition_candidate_runtime_status_metadata_test.py`
- `docs/reports/goal4062_prepared_partition_convergence_summary_preview_2026-06-09.md`
- `docs/reports/goal4062_prepared_partition_summary_timing_pod.json`
- `scripts/goal4062_prepared_partition_summary_timing.py`

## Verification Already Run

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4062_prepared_partition_convergence_summary_preview_test tests.goal4044_partition_candidate_runtime_status_metadata_test tests.goal4045_partition_component_signature_preview_test tests.goal4047_rt_dbscan_partition_signature_app_mode_test
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4005_partition_convergence_candidate_front_door_contract_test tests.goal4012_partition_convergence_contract_after_factor_sweep_test tests.goal4015_partition_guidance_immutability_test tests.goal4016_partition_convergence_typed_stream_contract_test tests.goal4017_partition_summary_reference_builder_test tests.goal4019_partition_summary_same_contract_validator_test tests.goal4021_partition_convergence_component_reference_test tests.goal4023_partition_summary_status_invariants_test tests.goal4024_partition_summary_edge_case_strengthening_test tests.goal4027_partition_summary_cupy_preview_test tests.goal4028_partition_convergence_preview_metadata_test tests.goal4029_partition_summary_numba_preview_test tests.goal4030_partition_preview_partner_metadata_test tests.goal4031_partition_convergence_preview_chain_packet_test tests.goal4033_partition_device_pair_preview_metadata_refresh_test tests.goal4035_partition_component_labels_cupy_preview_test tests.goal4040_partition_device_ambiguous_union_test tests.goal4044_partition_candidate_runtime_status_metadata_test tests.goal4045_partition_component_signature_preview_test tests.goal4046_partition_component_signature_timing_test tests.goal4047_rt_dbscan_partition_signature_app_mode_test tests.goal4049_rt_dbscan_route_metadata_after_signature_mode_test tests.goal4062_prepared_partition_convergence_summary_preview_test
```

Pod:

- RTX 4000 Ada, source commit `ddcc0680`
- Goal4062 timing rows: replay-only speedup 5.576x-8.826x; three-run amortized speedup 2.172x-2.437x.

## Review Questions

1. Is the prepared-summary handle app-agnostic, or does it reintroduce DBSCAN/app logic into the runtime surface?
2. Are the candidate-route boundaries honest: no default promotion, no native ABI addition, no hidden dispatch, no automatic partner choice, no release/public-speedup/broad-RT-core/whole-app/true-zero-copy claim?
3. Is the timing artifact interpreted correctly as prepared-replay evidence, not a broad whole-app performance claim?
4. Is changing the old blocker from `no_prepared_native_or_partner_partition_handle` to `no_promoted_prepared_native_partition_handle` accurate after Goal4062?
5. What must happen next before this partition-convergence candidate could become a promoted/default v2.x route?

## Required Output

Please write a review file using one of these paths:

- Claude: `docs/reviews/goal4063_claude_review_goal4062_prepared_partition_summary_2026-06-09.md`
- Gemini: `docs/reviews/goal4064_gemini_review_goal4062_prepared_partition_summary_2026-06-09.md`

Use one of the established verdict values: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

State explicitly that your review is independent from Codex authoring and that
Codex+Codex is not valid consensus.

