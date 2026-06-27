# Call For Review: Phoenix V3 M40 Component-Union Focused POD Intake

Requested reviewer: external AI reviewer

Requested verdict labels:

- `accept_m40_positive_step1_continue_step2`
- `accept_with_caveats_fix_harness_before_step2`
- `block_m40_result_invalid`
- `block_release_not_step2`

## Context

M38 defined the focused component-union POD protocol. M39 implemented the local harness and received Claude authorization for one focused POD run only.

M40 executed that one run on RT hardware:

- GPU: NVIDIA RTX 4000 Ada Generation
- `--require-rt-hardware`: passed
- dataset: `clustered3d`
- point count: `262144`
- repeat: `5`
- variants: Embree same-contract control, legacy OptiX grouped-stream labels, productized prepared-execution runner

Evidence:

- Intake report: `docs/reports/phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md`
- Artifact directory: `docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/`
- Main machine-readable result: `docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/summary.json`
- Process log: `docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/run.log`

## Result To Review

Protocol outcome:

- exit code: `0`
- failed checks: `0`
- component signatures match: `true`
- same generated point set: `true`
- component-label contract: `true`
- signature-only substitution blocked: `true`
- material Set-A candidate: `true`

Performance:

| Variant | Prepare sec | Hot query sec | Inclusive wall sec |
|---|---:|---:|---:|
| Embree same-contract component-union control | 13.424363 | 2.098104 | 26.528360 |
| Legacy OptiX grouped-stream component labels | 2.026539 | 1.707487 | 13.741997 |
| Productized prepared-execution runner | 0.685083 | 1.718311 | 10.955770 |

Computed:

- runner vs Embree hot: `1.221027x`
- runner vs Embree wall: `2.421405x`
- runner vs legacy wall: `1.254316x`
- runner vs legacy hot: approximately `0.994x`, not an exposed summary metric yet

Productized runtime flags:

- `runtime_executed=true`
- `runtime_trunk_executes_end_to_end=true`
- `internal_device_residency_between_rtdl_phases=true`
- `hot_path_host_materialization=false`
- `component_union_phase_accounting_visible=true`
- `component_signature_substituted_for_labels=false`

## Questions

1. Does this satisfy the M38/M39 bar for one positive Step-1 Set-A probe?
2. Is `accept_m40_positive_step1_continue_step2` valid, or should the result be accepted only with caveats?
3. Does the legacy-hot parity/slight slowdown change the Step-2 authorization?
4. Must the `summary.status` label bug be fixed before any Step-2 local or POD run?
5. Must `runner_vs_legacy_hot_speedup` be added as a first-class summary metric before any future review?
6. Is there any hidden release/public-claim wording in the intake report that must be removed?
7. What exact next family should be preferred for Step 2 if this is accepted?

## Non-Authorization

This review request does not authorize release, all-app POD spend, public speedup wording, V4/embedding/C-ABI work, or broad V3-over-V2 claims.
