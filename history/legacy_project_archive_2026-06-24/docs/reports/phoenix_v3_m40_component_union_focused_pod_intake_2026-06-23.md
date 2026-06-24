# Phoenix V3 M40 Focused Component-Union POD Intake

Status: `m40_positive_intake_not_release`
Date: 2026-06-23

## Scope

This records the single focused POD run authorized by the M39 Codex+Claude consensus. It is not an all-app run, not a V3 release authorization, and not a public performance claim.

The run tests one residency-rich Set-A family:

- fixed-radius self-query
- grouped-stream component-label continuation
- productized prepared-execution runner
- same generated point set across all variants
- full component-label output contract, not signature-only substitution

## Hardware And Gate

POD: `root@213.173.108.14:11592`

GPU gate:

```json
{"name": "NVIDIA RTX 4000 Ada Generation", "driver_version": "550.127.05", "compute_cap": "8.9"}
```

`scripts/v3_optix_hardware_gate.py --require-rt-hardware` passed before the run.

## Command

```bash
PYTHONPATH=src:. ../.venv/bin/python scripts/v3_phoenix_component_union_m38_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706 \
  --variant all \
  --dataset clustered3d \
  --point-count 262144 \
  --radius 3.0 \
  --min-neighbors 4 \
  --seed 20260623 \
  --warmup 1 \
  --repeat 5 \
  --heartbeat-sec 30 \
  --hard-cap-sec 7200 \
  --require-rt-hardware
```

Local evidence directory:

`docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/`

Exit code: `0`

## Result Summary

All protocol checks passed.

- `failed_check_count`: `0`
- `all_variant_canonical_component_signatures_match`: `true`
- `legacy_no_regression`: `true`
- `material_set_a_candidate`: `true`
- `same_generated_point_set_enforced`: `true`
- `component_signature_shortcut_blocked`: `true`
- `release_authorized`: `false`
- `public_speedup_claim_authorized`: `false`
- `broad_v3_faster_than_v2_claim_authorized`: `false`

Timing medians:

| Variant | Prepare sec | Hot query sec | Inclusive wall sec |
|---|---:|---:|---:|
| Embree same-contract component-union control | 13.424363 | 2.098104 | 26.528360 |
| Legacy OptiX grouped-stream component labels | 2.026539 | 1.707487 | 13.741997 |
| Productized prepared-execution runner | 0.685083 | 1.718311 | 10.955770 |

Computed comparisons:

| Comparison | Speedup |
|---|---:|
| Productized runner vs Embree, hot query | 1.221027x |
| Productized runner vs Embree, inclusive wall | 2.421405x |
| Productized runner vs legacy, inclusive wall | 1.254316x |

Important caveat: productized runner hot query vs legacy OptiX is effectively parity/slightly slower on this run, approximately `0.994x`. The positive legacy comparison is inclusive wall, apparently driven by lower prepare/integration cost rather than a faster hot kernel than the existing legacy OptiX route.

## Runtime-Trunk Evidence

The productized runner row records:

- `runtime_executed`: `true`
- `runtime_trunk_executes_end_to_end`: `true`
- `productized_execution_path`: `prepared_execution_session_runner`
- `primitive_family`: `fixed_radius_graph_component_union`
- `continuation_contract`: `generic_prepared_optix_numba_grouped_stream_component_labels_3d`
- `component_union_phase_accounting_visible`: `true`
- `internal_device_residency_between_rtdl_phases`: `true`
- `hot_path_host_materialization`: `false`
- `component_label_pass_accounted`: `true`
- `component_signature_substituted_for_labels`: `false`

This is the first positive Step-1-shaped evidence that the Phoenix runtime trunk is not merely a skeleton for this family.

## Interpretation

This run supports continuing Phoenix V3 Step 2: attach at least two more Set-A families to the same runner before any all-app POD spend or release decision.

It does not support any of these claims:

- V3 is release-ready.
- V3 is broadly faster than V2.x.
- All benchmark apps are solved.
- External zero-copy, embedding, C ABI, or V4 work is authorized.

## Harness Caveats To Fix Before Another POD Run

The JSON `summary.status` still says `component_union_m39_harness_ready_not_pod_run` even when `dry_run=false` and real POD artifacts exist. The result is still interpretable because `dry_run=false`, `exit_code=0`, and all variant JSONs are present, but the status label must be fixed before any next run.

The summary should also add `runner_vs_legacy_hot_speedup` explicitly, because the current comparison table only exposes runner-vs-legacy inclusive wall.

Post-intake fix status:

- `scripts/v3_phoenix_component_union_m38_pod_ab.py` now emits separate dry-run,
  failed real-run, and completed real-run statuses.
- `comparison_payload()` now emits `runner_vs_legacy_hot_speedup`.
- Focused local validation ran 9 tests OK.
- Full `v3_rebuild` after the caveat fixes ran 119 modules / 620 tests OK.

## Goal-Level Decision Audit

1. Was I foolish? Not in choosing to run M40; the run had M39 Claude authorization and a passing RT hardware gate.
2. If yes, what actions made the decision foolish? The earlier launch command held SSH descriptors and timed out locally; that was a process-control mistake, not a benchmark validity failure.
3. Was there another path that avoided locking onto a bad idea? Yes: verify process state immediately, poll logs, and preserve artifacts instead of restarting or rerunning.
4. Can I now try a different path that solves the real problem? Yes: use this as one positive Step 1 probe, fix the harness label/metric caveats, then move to Step 2 families under the same runner.

## Non-Authorization Block

This document does not authorize release, all-app POD spend, public speedup wording, V4/embedding/C-ABI work, or broad V3-over-V2 claims.
