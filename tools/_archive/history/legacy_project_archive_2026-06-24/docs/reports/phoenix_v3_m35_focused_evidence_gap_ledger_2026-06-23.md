# Phoenix V3 M35 Focused Evidence Gap Ledger

Date: 2026-06-23

Status: `m35_focused_gap_ledger_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
```

## Purpose

M35 records the gap that Claude explicitly called out after M30-M34:
`Step-4 ready by local audit` is a metadata and contract status, not a material
performance result. A prepared-session helper can be structurally ready and
still fail the Phoenix V3 performance bar.

The goal is to keep the next work pointed at the V3 language/runtime trunk:
runner-callable generic continuation nodes, internal device residency between
RTDL phases, and focused same-contract evidence. It is not app development and
it is not a release packet.

## Controlling Rule

```text
Structural ready:
  productized prepared_execution_session_runner path executes;
  Step-3 residency/no-host-materialization audit passes;
  Step-4 continuation contract audit passes.

Material ready:
  the productized runtime path beats the relevant incumbent on the same
  contract by the frozen Set-A bar, with the win sourced from the runtime path,
  not from cache hygiene or an easier baseline.
```

All broad all-app POD work remains blocked until focused Set-A material
evidence exists across multiple runner-backed families, Set-B controls have
parity classification, and the packet receives external review.

## Focused Gap Table

| Family | Current status | Evidence | Gap | Next action |
| --- | --- | --- | --- | --- |
| RTDBSCAN component signature | Structural ready, not material | M3.4 runner vs legacy OptiX grouped-stream geomean `0.997557675600175`; Step-1 runner vs legacy `0.994858x`; runner vs Embree `2.927729x` is control context, not the incumbent comparison | Runner wraps an already strong grouped-stream OptiX route; it preserves parity but does not reduce the dominant grouped-union pass | Stop RTDBSCAN wrapper micro-tuning. Revisit only through a generic component-union core-node change that reduces the grouped-union pass itself |
| RayJoin point-location topology stream | Structural ready, not material | Total-repeat legacy/runner `0.973754x`; hot-query legacy/runner `0.973465x`; runner executes with internal residency and no hot-path host materialization | Current runner wraps the same relation-status scalar-count executor; no new physical work is removed | Do not rerun the PIP scalar-count wrapper. Revisit only if RayJoin becomes a multi-phase topology pipeline where the runner removes materialization or repeated planning |
| Grouped reduction device-column | Strong row-scoped evidence, not yet a generic prepared-session core node in M33/M34 | Claude verified `3.5985x` and `73.586x` host-packed/device-column cold+repeat100 rows; accepted only as exact row-scoped grouped_reduction evidence | Evidence is real, but current M33 public prepared-session ledger has no generic `run_grouped_vector_sum_2d_prepared_session` helper; too much remains packet/app-route shaped | Promote grouped vector sum/reduction into a runner-callable prepared-session core node with Step-3/Step-4 audit fields |
| Component union / component signature | Generic pieces exist, but the dominant union pass is still the likely bottleneck | Goal4059 direct signature was externally accepted with boundary and about `1.077x` diagnostic speedup; M3.4 parity shows signature savings alone do not create a V3 material win | Direct signature avoids label materialization, but grouped-union parent-workspace construction remains dominant | Split component-union and signature as auditable core nodes; target grouped-union atomic pressure and phase accounting before another RTDBSCAN material claim |

## Positive Evidence That Must Stay Scoped

| Family | Scoped reading |
| --- | --- |
| Triangle weighted summary device-output stream | Focused strict Set-A probe accepted; runner vs legacy wall `2.1167x`; scoped to the K4 clique workload, not broad Triangle or V3 speedup |
| RTNN repeat50 prepared runner | Scoped second Set-A candidate under M30; not release evidence and not a single-shot/hot-path speedup claim |
| Hausdorff threshold runner | Weak positive focused evidence; runner vs legacy wrapper wall `1.0541x`, runner vs Embree wrapper wall `1.5378x`; not broad app evidence |
| Barnes-Hut aggregate-tree fused vector sum | Capability/parity evidence with M29 same-contract boundary; do not rewrite as a V2.14 speedup |

## M35 Work Queue

1. M36: add a generic grouped vector-sum/reduction prepared-session helper.
   - It must call the productized runner.
   - It must use generic grouped-reduction vocabulary only.
   - It must report Step-3 and Step-4 audit facts.
   - It must not import RayDB or any benchmark-app semantics.
   - M3.4 recommended AABB runner generalization immediately after RTDBSCAN
     parity. The M30-M34 bundle review supersedes that sub-milestone direction
     for the next trunk step because grouped reduction has stronger existing
     row-scoped evidence but lacks a runner-callable core node.

2. M37: split component-union and component-signature accounting.
   - Component signature already has a clean generic front door.
   - The missing performance source is the grouped-union pass.
   - The next node should expose union-pass timing/residency instead of hiding
     it inside an RTDBSCAN route packet.

3. M38: decide whether RayJoin can become a real multi-phase topology pipeline.
   - If the only available route is the current scalar-count wrapper, keep it
     structural-only and do not spend POD on it.

4. M39: focused evidence gate before all-app.
   - No all-app run until the runner-backed families meet the frozen focused
     evidence preconditions and receive external review.

## Validation

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 114
Ran 593 tests in 74.220s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m35_consensus_20260623_131415.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m35_consensus_20260623_131415.stderr.txt
```

The M35 ledger gate is included in this matrix.

## Sources

- `docs/reviews/claude_phoenix_v3_m30_m34_bundle_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m30_m34_2ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_step1_rtdbscan_runtime_trunk_probe_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_step2_rayjoin_point_location_runner_pod_ab_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md`
- `docs/reviews/goal4060_claude_review_goal4059_direct_numba_component_signature_2026-06-09.md`
- `docs/reviews/goal4061_gemini_review_goal4059_direct_numba_component_signature_2026-06-09.md`

## Goal-Level Decision Audit

Decision: freeze RTDBSCAN and RayJoin as structurally ready but not material,
and redirect M36/M37 toward generic grouped-reduction and component-union core
nodes.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be claiming the RTDBSCAN `2.9x` control comparison
   or the RayJoin runner execution as V3 performance proof while hiding the
   incumbent comparisons.

3. Was there another path?

   Yes. Continue route micro-tuning or run all-app again. Both paths are
   rejected because they would spend POD before the runtime trunk has enough
   material focused evidence.

4. Can I now try a different path that actually solves the problem?

   Yes. Promote reusable grouped-reduction and component-union work into
   runner-callable core nodes, then measure focused same-contract evidence.

## Non-Authorization

This report authorizes no V3 release, no all-app POD spend, no public speedup
claims, no broad V3-over-V2.x claims, no true-zero-copy wording, no automatic
partner selection, no V4 work, no C ABI work, and no embedding work.
