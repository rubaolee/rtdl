# Phoenix V3 Barnes-Hut Step-1 Replacement Pre-Audit

Date: 2026-06-22

Status: `conditional_go_for_step1_replacement_implementation_with_required_gates_pod_not_authorized`

## Decision

Barnes-Hut is a valid next Phoenix V3 material-probe candidate, but it is not yet Step 2 generalization.

RTDBSCAN and RayJoin both proved structural runner execution without material gain. That means the Step 1 material-exit requirement is still unsatisfied. Barnes-Hut should therefore be treated as a Step 1 replacement attempt: can the productized runtime trunk carry a real material performance source?

The next action is implementation, not pod. Route the existing generic aggregate-tree fused weighted-vector Numba CUDA partner through the productized `prepared_execution_session_runner`. Only after that wiring exists should pod time be spent.

## Gate Status

| Gate | Status |
| --- | --- |
| Step 1 material completion | `false` |
| Barnes-Hut Set-A classification | `true`, frozen as Set A in `docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json` |
| M7 row amendments from Claude | `true`, applied in `scripts/v3_phoenix_m7_row_classification_packet.py` |
| Pod now authorized | `false` |
| Runtime implementation authorized | `true`, as Step 1 replacement only |
| All-app pod authorized | `false` |

## What The Audit Found

The current prepared RTDL/OptiX frontier-emission shape is a historical no-go reference, not the primary claim:

| Bodies | Prepared OptiX+Numba wall | Fused Numba CUDA wall | Prepared OptiX / fused |
| ---: | ---: | ---: | ---: |
| 32,768 | `82.434527 ms` | `11.738643 ms` | `7.022x` |
| 65,536 | `177.858080 ms` | `35.643227 ms` | `4.990x` |
| 131,072 | `618.301734 ms` | `45.492701 ms` | `13.591x` |

The performance source is real: the fused partner avoids aggregate-frontier row emission, host frontier materialization, and host contribution materialization. It accumulates directly into vector/count columns.

But the fastest route already exists as an app front-door / partner API: `fused_frontier_force_sum_bucketized_numba_cuda`, backed by `generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1`. Therefore a runner wrapper alone may not be faster than the existing fused partner. The honest V3 task is to productize that generic capability through the runtime trunk and preserve its speed.

## Required Comparison Design

After implementation, the focused pod A/B must report two comparisons:

- Historical no-go reference: productized runner-wrapped fused partner versus the old prepared OptiX frontier-emission / V2.x-style frontier route.
- Primary parity control: productized runner-wrapped fused partner versus the existing app-front-door fused Numba CUDA partner.

The material claim can only say: the productized Phoenix V3 path exposes the fused aggregate-tree vector-accumulation capability and displaces the old frontier-emission path. It must not claim that the runner wrapper itself is faster than the already-fused partner unless the parity control actually shows that.

Parity rule:

- runner / existing fused partner must be at least `0.95x` at every serious size;
- target geomean is at least `0.98x`;
- if the productized runner is more than 5% slower at any serious size, the packet is no-go for claim use and a runner-overhead bug must be logged before promotion.

## Why Pod Is Not Authorized Yet

Running pod now would likely reproduce the known fused-partner result, but it would not prove the productized runtime path exists. That repeats the earlier failure pattern: impressive app-route evidence without the trunk actually carrying the capability.

Pod becomes useful only after:

- the generic helper is in runtime code, not only in the Barnes-Hut app;
- the app adapter calls the helper;
- runner metadata records `runtime_executed = true`;
- the partner is explicit: `numba_cuda`;
- no frontier/contribution row host materialization is present;
- release, broad speedup, RT-core, true-zero-copy, all-app, and automatic-partner flags remain false.

## Forbidden Shortcuts

- Do not compare only against the slow OptiX frontier route and call it a pure runner win.
- Do not label the slow OptiX route as the primary material baseline; it is historical no-go reference / predecessor displacement evidence.
- Do not claim RT-core acceleration: this route uses Numba CUDA, not RT cores.
- Do not claim whole-app Barnes-Hut or paper reproduction.
- Do not authorize all-app runs from this audit.
- Do not add app-specific native Barnes-Hut semantics to the engine.

## Next Implementation Target

Add an app-agnostic helper for:

`aggregate_tree_fused_weighted_vector_sum_2d`

It should live in runtime/prepared-execution code, call an explicit partner-prepared session, and annotate:

- `primitive_family = aggregate_tree_fused_weighted_vector_sum_2d`
- `productized_execution_path = prepared_execution_session_runner`
- `runtime_trunk_executes_end_to_end = true`
- `explicit_partner = numba_cuda`
- `frontier_rows_materialized_on_host = false`
- `contribution_rows_materialized_on_host = false`
- `rt_core_speedup_claim_authorized = false`
- `full_all_app_rerun_authorized_by_this_packet = false`

## Goal-Level Decision Audit

1. Was I foolish?
   No after amendment. This audit no longer pretends Step 1 is complete, and it separates a real performance source from a runner-wrapper parity control.

2. If yes, what actions made the decision foolish?
   Not applicable after amendment. The foolish action would be to run against the slow OptiX frontier route only, hide that the fast fused partner already exists, and call that a pure runner win.

3. Was there another path?
   Yes. We could run pod immediately against the old OptiX route. That would likely produce a large number, but it would not prove the productized runtime path exists.

4. Can I now try a different path that actually solves the problem?
   Yes. First wire the generic fused partner through `prepared_execution_session_runner`; then run pod with both the historical no-go reference and the primary parity control.

## Non-Authorization

This audit authorizes no release, no public speedup claim, no broad V3-over-V2 claim, no RT-core claim, no true-zero-copy claim, no automatic partner selection, and no all-app benchmark run.
