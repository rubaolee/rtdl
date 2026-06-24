# Phoenix V3 M15 Third Strict Set-A Probe Audit

Date: 2026-06-22

Status: `m15_triangle_selected_for_m16_by_2ai_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
external_embedding_or_zero_copy_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
```

## Bottom Line

M15 selects Triangle Counting as the best next candidate for the third strict
Set-A material probe, but it does **not** count Triangle as that third probe
yet.

The reason is narrow and important: the existing Triangle row is strong
row-scoped evidence, but it is not yet a current Phoenix
`prepared_execution_session_runner` path with `runtime_executed: true`. The next
responsible step is M16 local runner wiring and a reviewed focused-POD
protocol, not an all-app run.

## 2-AI Status

Codex + Bernoulli consensus:

```text
verdict: accept_m15_triangle_m16_local_runner_wiring_no_pod
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
triangle_counts_as_third_strict_set_a_material_probe_now: false
triangle_next_local_implementation_target: true
```

Consensus path:
`docs/reviews/codex_bernoulli_phoenix_v3_m15_third_strict_set_a_probe_2ai_consensus_2026-06-22.md`

The reviewer found no blockers or P1 fixes for recording M15.

## Why Triangle Is The Best Candidate

Triangle is Set-A because it is a residency-rich, multi-phase route:

- graph lowering and segment planning;
- prepared ray batches;
- weighted ray-triangle any-hit summary;
- device-output stream continuation;
- explicit CuPy/Numba partner construction.

The existing exact row is:

```text
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
```

Existing row evidence:

| Metric | Value |
| --- | ---: |
| Workload | generated K4 clique ladder, 80,000 cliques |
| Oracle triangles | 320,000 |
| Hot OptiX / Embree | `347.232x` |
| Wall OptiX / Embree | `6.342x` |
| Oracle match | true |
| Row status | row-scoped M7-qualified, non-graph stream only |

This is not a toy summary. It has same-contract OptiX/Embree evidence on the
RTX 4000 Ada pod and a visible wall-time signal. But it still cannot be used as
a broad V3 claim.

## Why It Does Not Count Yet

The current Phoenix redo bar requires material Set-A wins to be sourced from
the productized execution path, not scattered app routes or old row packets.
For Triangle, the old row has these remaining blockers:

- not yet a current `prepared_execution_session_runner` path;
- old comparison is row-scoped OptiX vs Embree, not a current V2.14 vs Phoenix
  V3 runtime-runner comparison;
- M113 CUDA graph capture remains blocked;
- not full Triangle app speedup;
- not RT-Graph paper reproduction;
- not graph database acceleration.

Goal4531 and Goal4540 matter because they define the V3-legal boundary:
internal RTDL device-output stream continuation is V3 work; exposing device
buffers to external hosts remains out of V3.

## Alternatives Rejected For M15

| Candidate | Current Classification | Reason |
| --- | --- | --- |
| Hausdorff | positive focused evidence, not strict third | M14 rejected it as too small: runner vs legacy wrapper wall `1.054105x`. |
| RTDBSCAN | structural only | Runner vs legacy `0.994858x`; incumbent already had the physical advantage. |
| RayJoin / Spatial | coverage or structural only | LSI M13 runner/old hot `0.785772x`; PIP Step-2 total-repeat `0.973754x`. |
| RayDB/grouped reduction | retained evidence | Useful, but Triangle has the clearer unresolved residency/continuation source for the third strict probe. |

## Recommended M16

M16 should be local only:

1. Add or reuse a Phoenix prepared-execution helper for generic ray-triangle
   weighted-summary device-output stream continuation.
2. Wire the selected Triangle route through the productized runner metadata.
3. Require these metadata fields before any POD:

```text
runtime_executed: true
productized_execution_path: prepared_execution_session_runner
explicit_backend: optix
explicit_partner: cupy_or_numba_as_user_chosen
hot_path_host_materialization: false where supported
m113_graph_capture_claim_authorized: false
release_authorized: false
public_speedup_claim_authorized: false
```

Only after that local work and 2-AI review should a focused POD A/B be run.
The focused run should compare the old Triangle route against the
runner-backed Triangle route on the same RTX 4000 Ada pod, with Embree kept as
a control and hot-query versus runner-inclusive wall metrics reported
separately.

## Goal-Level Decision Audit

Decision: select Triangle as the best local M16 candidate for the third strict
Set-A probe, while refusing to count the old Triangle row as the third probe
yet.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to use the old `347.232x` hot-query or `6.342x` wall row
   as automatic Phoenix runtime-trunk proof before the current productized
   runner path executes it.
3. Was there another path?
   Yes: count Hausdorff as the third probe, rerun Spatial/RayJoin, or jump to
   all-app. Those repeat the earlier pattern of over-counting weak or blended
   evidence.
4. Can I now try a different path?
   Yes. Build the Triangle runner-backed path locally, get 2-AI review, then
   spend focused POD only if the review authorizes it.

## Non-Authorization

This report authorizes no V3 release, no public speedup claim, no broad
V3-over-V2 claim, no true-zero-copy claim, no V4/embedding work, no focused POD,
and no all-app POD.
