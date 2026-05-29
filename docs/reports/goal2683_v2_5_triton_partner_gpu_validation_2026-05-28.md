# Goal2683: Validate v2.5 Triton Partner Path On GPU

Status: GPU validated for generic continuation and public adapter front door; not performance-promoted.

Date: 2026-05-28

## Purpose

Goal2683 turns the local v2.5 Triton preview into GPU evidence while preserving
the RTDL boundary:

- RT traversal remains RTDL/Embree/OptiX work.
- Triton owns only generic post-RT continuation, reduction, compaction, and
  finalization.
- App semantics stay outside the engine.

## Pod And Commit

Pod command supplied by the user:

```bash
ssh root@66.92.198.154 -p 11253 -i ~/.ssh/id_ed25519
```

Actual working key on this Mac:

```bash
/Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Validated Git revision on the pod:

```text
74d7ecc36fa5008b8e7336988cd2fc9242a59093
```

Environment:

| Field | Value |
| --- | --- |
| GPU | NVIDIA L4 |
| Driver | 570.195.03 |
| Python | 3.12.3 |
| Torch | 2.8.0+cu128 |
| CUDA via Torch | 12.8 |
| Triton | 3.4.0 |
| Numba | unavailable on this pod |

## Evidence Artifacts

| Artifact | Scope | Status |
| --- | --- | --- |
| `docs/reports/artifacts/goal2683_goal2665_low_level_triton_l4.json` | Low-level Triton dispatcher validation | `accept` |
| `docs/reports/artifacts/goal2683_goal2682_adapter_front_door_triton_l4.json` | Public `partner="triton"` adapter validation | `ok`, all correct |
| `docs/reports/artifacts/goal2683_raydb_triton_front_door_l4.json` | RayDB app-level public front-door validation | `ok`, all correct |

## Commands Run On Pod

```bash
cd /workspace/rtdl_python_only
git fetch origin main
git reset --hard origin/main

PYTHONPATH=src:. python3 scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py \
  --row-counts 1024,65536,1048576 \
  --group-count 4096 \
  --repeats 5 \
  --include-numba \
  --output docs/reports/artifacts/goal2683_goal2665_low_level_triton_l4.json

PYTHONPATH=src:. python3 scripts/goal2682_v2_5_triton_adapter_front_door_pod_runner.py \
  --row-counts 1024,65536,1048576 \
  --group-count 4096 \
  --repeats 5 \
  --output docs/reports/artifacts/goal2683_goal2682_adapter_front_door_triton_l4.json

PYTHONPATH=src:. python3 scripts/goal2683_raydb_triton_front_door_pod_runner.py \
  --row-counts 1024,65536,1048576 \
  --group-count 4096 \
  --repeats 5 \
  --output docs/reports/artifacts/goal2683_raydb_triton_front_door_l4.json
```

CUDA-focused unit tests also passed on the same pod:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test \
  tests.goal2683_v2_5_triton_partner_gpu_validation_test
```

Result:

```text
Ran 19 tests
OK (skipped=1)
```

## Low-Level Triton Continuation Validation

All generic low-level operations were correct against Torch CUDA baselines at
`1024`, `65536`, and `1048576` rows:

| Operation | Correct |
| --- | --- |
| `segmented_count_i64` | yes |
| `segmented_sum_f64` | yes |
| `segmented_min_f64` | yes |
| `segmented_max_f64` | yes |
| `compact_mask_i64` | yes |
| `grouped_argmin_f64` | yes |
| `bounded_collect_finalize_i64` | yes |

Median times at `1048576` rows:

| Operation | Triton preview | Torch CUDA baseline |
| --- | ---: | ---: |
| Count | 0.002638 s | 0.000121 s |
| Sum | 0.002805 s | 0.000071 s |
| Min | 0.003193 s | 0.000173 s |
| Max | 0.003151 s | 0.000174 s |
| Compact | 0.008322 s | 0.000124 s |
| Grouped argmin | 0.006086 s | 0.000608 s |
| Bounded collect/finalize | 0.006050 s | 0.000659 s |

Interpretation: correctness is validated. Performance promotion is not
validated; the preview kernels are slower than Torch CUDA baselines on this L4
for these synthetic continuation-only cases.

## Public Adapter Front Door Validation

The public `partner="triton"` adapter APIs were correct at all tested scales:

| Front-door API behavior | Correct |
| --- | --- |
| Grouped count | yes |
| Grouped sum | yes |
| Grouped min | yes |
| Grouped max | yes |
| Mask compaction | yes |
| Columnar predicate count | yes |
| Columnar predicate sum | yes |

Median times at `1048576` rows:

| Adapter operation | Triton front door | Torch CUDA baseline |
| --- | ---: | ---: |
| Count | 0.002737 s | 0.000119 s |
| Sum | 0.002905 s | 0.000074 s |
| Min | 0.003654 s | 0.000153 s |
| Max | 0.003380 s | 0.000179 s |
| Compact | 0.005390 s | 0.000062 s |
| Predicate count | 0.010981 s | n/a |
| Predicate sum | 0.003759 s | n/a |

The adapter layer is now GPU-correct, but still `preview_not_promoted`.

## Benchmark-App Triton Readiness

Classification uses `v2_5_triton_front_door_coverage()`.

| Benchmark app | Readiness | Required operations | Adapter front-door operations | Dispatcher-only operations | Missing operations |
| --- | --- | --- | --- | --- | --- |
| RayDB-style grouped aggregates | `adapter_front_door_ready` | `segmented_count_i64`, `segmented_sum_f64`, `segmented_min_f64`, `segmented_max_f64` | `segmented_count_i64`, `segmented_sum_f64`, `segmented_min_f64`, `segmented_max_f64` | none | none |
| Spatial RayJoin | `adapter_front_door_ready` | `segmented_count_i64`, `compact_mask_i64` | `segmented_count_i64`, `compact_mask_i64` | none | none |
| LibRTS-style AABB index query | `adapter_front_door_ready` | `segmented_count_i64` | `segmented_count_i64` | none | none |
| Hausdorff/X-HD | `dispatcher_ready_app_wiring_required` | `grouped_argmin_f64`, `segmented_max_f64` | `segmented_max_f64` | `grouped_argmin_f64` | none |
| RT-DBSCAN | `dispatcher_ready_app_wiring_required` | `compact_mask_i64`, `bounded_collect_finalize_i64` | `compact_mask_i64` | `bounded_collect_finalize_i64` | none |
| RTNN neighbor search | `dispatcher_ready_app_wiring_required` | `grouped_argmin_f64`, `bounded_collect_finalize_i64` | none | `grouped_argmin_f64`, `bounded_collect_finalize_i64` | none |
| RT-Graph triangle counting | `adapter_front_door_ready` | `segmented_count_i64`, `compact_mask_i64` | `segmented_count_i64`, `compact_mask_i64` | none | none |
| Barnes-Hut / aggregate frontier | `dispatcher_ready_app_wiring_required` | `bounded_collect_finalize_i64`, `segmented_sum_f64` | `segmented_sum_f64` | `bounded_collect_finalize_i64` | none |
| Robot collision screening | `dispatcher_ready_app_wiring_required` | `compact_mask_i64`, `bounded_collect_finalize_i64` | `compact_mask_i64` | `bounded_collect_finalize_i64` | none |
| Bounded contact-manifold witness | `dispatcher_ready_app_wiring_required` | `bounded_collect_finalize_i64` | none | `bounded_collect_finalize_i64` | none |

## First App Integration: RayDB

RayDB is now wired through the public Triton adapter front door for app-lowered
post-RT grouped continuation:

- `count` uses `partner_group_count_by_key(..., partner="triton")`.
- `sum` uses `partner_group_sum_by_key(..., partner="triton")`.
- `min` uses `partner_group_min_by_key(..., partner="triton")`.
- `max` uses `partner_group_max_by_key(..., partner="triton")`.
- `avg_as_sum_count` uses generic `sum` plus `count`.

The app-level runner validates `count`, `sum`, `min`, `max`, and
`avg_as_sum_count` against Torch CUDA baselines at all tested scales.

Median RayDB app-level continuation times at `1048576` rows:

| Mode | RayDB Triton public front door | Torch CUDA baseline |
| --- | ---: | ---: |
| Count | 0.002772 s | 0.000120 s |
| Sum | 0.002828 s | 0.000074 s |
| Min | 0.006701 s | 0.000160 s |
| Max | 0.007289 s | 0.000203 s |
| Avg as sum+count | 0.006651 s | 0.000240 s |

## RT+Triton Boundary

This goal validates the partner continuation half of the future
RT+Triton path. It does not yet validate a full same-contract
RT traversal plus Triton continuation total path.

Reason: the existing RayDB paper-shaped native RT path currently performs
grouped reduction inside the generic RTDL native primitive. It does not expose
a raw generic hit stream of `(group_id, value)` rows for a partner continuation
to consume. Without that stream, a full RT+Triton total comparison would either
duplicate work or silently compare different contracts.

Required next step for full RT+Triton timing:

1. Add or expose a generic raw hit-stream/primitive-id stream from the RT path
   without app semantics.
2. Route that generic stream to the same public Triton front door validated
   here.
3. Compare `RT traversal + Triton continuation` against the existing
   `RT traversal + native grouped reduction` and Embree baseline.

No public speedup wording is authorized by Goal2683.

## Conclusion

Goal2683 establishes that the v2.5 Triton partner path is GPU-correct at two
levels: low-level dispatcher and public adapter front door. RayDB is the first
benchmark app with app-level public Triton front-door continuation wiring.

The path remains preview-only. The current Triton kernels are correctness
vehicles and API boundary evidence, not performance winners against Torch CUDA
baselines. Performance promotion requires optimized Triton kernels, a generic
RT hit-stream handoff, and same-contract full-path benchmark evidence.
