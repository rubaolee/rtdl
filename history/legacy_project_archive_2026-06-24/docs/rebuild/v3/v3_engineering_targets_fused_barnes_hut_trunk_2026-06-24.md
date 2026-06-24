# V3 Engineering Targets: The Fused Barnes-Hut Trunk Path

Date: 2026-06-24
Author: Claude (independent reviewer) — concrete design + implementation targets, **not a release/POD authorization**
For: Main AI / next primary agent on Phoenix V3
Companion to: `phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`, `STOP_THE_CHURN_PHOENIX_V3_HIT_THE_BLOCKER_2026-06-24.md`

This document turns "build the high-performance V3" into a concrete, ordered,
measurable engineering sequence on real code. Each target ends in a
**measurement**, not a green test. Do them in order. Do not open process,
audit, or external-review milestones between them.

---

## 0. Goal (one sentence)

Make `barnes_hut_force_app` (Set-A blocker, ~0.844x vs V2.14) run end to end
through one productized prepared-session runner, with the RT tree-traversal
output kept **device-resident** straight into the fused weighted-vector-sum
continuation, no host materialization in the hot path — and measure whether that
moves 0.844x to parity or better.

If it does, V3 has a real performance source and you generalize it. If it does
not, V3 is not a broad-speedup release and the claim changes. Either is a result.

---

## 1. The design — the fused Barnes-Hut trunk path

### Existing pieces to reuse (do not rebuild these)

- Native RT path: `src/rtdsl/aggregate_tree_reference.py`
  - `rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d`
  - `rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d`
  - `rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d`
  - contract `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`
- Partner accumulator reference: `src/rtdsl/app_reference/aggregate_force_math.py`
  - `prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda`
  - `sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda`
- Productized fused accumulator (M43 win): `src/rtdsl/prepared_execution.py`
  - `run_grouped_vector_sum_2d_prepared_session` (CuPy warp-per-group, 3.45x)
- Front door: `src/rtdsl/app_adapters/barnes_hut.py`
  - `pairwise_inverse_square_force_2d_partner_columns`
- Benchmark row: `barnes_hut_force_app` in `src/rtdsl/app_support_matrix.py`

### Target data flow (the trunk)

```text
PREPARE (once, outside hot loop)
  build bucketized aggregate tree + OptiX prepared handle
  -> hold prepared handle + device buffers in a prepared-session object

PHASE 1  (hot) RT tree-opening / traversal
  rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d
  -> produces the per-body interaction frontier / partial weighted terms
  -> OUTPUT STAYS ON DEVICE (no host copy)

PHASE 2  (hot) fused weighted-vector-sum continuation
  run_grouped_vector_sum_2d_prepared_session  (CuPy warp-per-group)  OR
  sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda
  -> consumes the Phase-1 device buffer directly
  -> OUTPUT device-resident force vectors

BOUNDARY (once)
  copy final force vectors to host only if the contract requires it
```

### Residency contract (the V3 lever)

- The frontier / interaction stream between Phase 1 and Phase 2 **never touches
  host memory.**
- The only host crossings are: inputs at PREPARE (once) and the final force
  result (once).
- Anything else is a leak and is the thing to delete.

### Required phase/telemetry schema (emit on every run)

```text
phase_seconds: { prepare, traverse, accumulate, boundary }
runtime_executed: true|false
internal_residency_measured: true|false
host_materialization_in_hot_path: true|false        # must be false to count
win_source: residency_wall | partner_continuation | kernel
same_contract_incumbent: <legacy barnes_hut path id that produced 0.844x>
result_vs_incumbent: <ratio>
```

---

## 2. Implementation targets (in order)

### T1 — Instrument the current path; locate the 0.844x cause
**Do not optimize yet. Measure first.** Add the telemetry schema to the existing
`barnes_hut_force_app` path and run it locally same-contract.

- Deliverable: per-phase timing + host-crossing count for the current path.
- Exit gate (measurement): you can state, in one sentence, *where* the 0.844x
  goes — host frontier materialization, repeated prepare/pack, or a slow kernel.
- Why: do not fix a cause you have not measured. T1 decides whether T2 is a
  residency fix (most likely) or a kernel problem (changes the plan).

### T2 — Route the front door through the fused device-resident trunk
Based on T1, make `barnes_hut_force_app` call the prepared-session trunk path
(Section 1), keeping the Phase-1 output device-resident into Phase-2.

- Touch points: `app_adapters/barnes_hut.py`, `prepared_execution.py`,
  `aggregate_tree_reference.py` glue.
- Deliverable: the front-door probe runs through the runner (not a bypass) with
  `runtime_executed: true`, `host_materialization_in_hot_path: false`.
- Exit gate (measurement): same-contract, same-hardware ratio vs the 0.844x
  incumbent, with `win_source` recorded.
- **Decision:** moves toward/above parity → success, go to T3. Does not move and
  T1 said the cost is the kernel itself → record it, and trigger the
  capability-vs-speed reframe (Section 4); do not paper over it.

### T3 — Second blocker through the same runner (generality + Set-B)
Route `librts_spatial_index` (Set-B, ~0.937x) — or whichever blocker T1/T2
methodology shows is overhead-caused — through the **same** prepared-session
discipline. No new bypass, no app-specific knob.

- Exit gate: librts ≥ 0.98x (Set-B parity target) or an accepted explanation;
  `win_source` recorded; ≥2 families now share the runner.

### T4 — Make residency + phase accounting enforced runtime outputs
Turn the telemetry schema from "emitted by these probes" into "required by the
runner; fail closed if missing." Flip the dormant trunk status to match reality.

- Touch points: `src/rtdsl/v3_0_execution_graph.py`
  (`V3_EXECUTION_GRAPH_STATUS` off `m2_no_execution_skeleton`),
  `src/rtdsl/v3_0_prepared_graph_chunk_executor.py`
  (`runtime_executed: true` on the live paths).
- Exit gate: every Set-A probe routed through the runner reports measured
  residency; missing telemetry fails closed.

### T5 — Promote the two continuations into runner-callable core nodes
Generalize fused weighted-vector-sum and fixed-radius component-union into named
nodes the execution graph calls, so a third family reuses them with no new code
path.

- Exit gate: a third Set-A family runs through the same nodes; continuation is a
  layer, not app-mode code.

### T6 — Focused scorecard re-read, then request all-app authorization
Re-measure **only** the Set-A/Set-B rows now routed through the runner
(barnes_hut, librts, + the third family), same-contract, and build the
two-number scorecard from those.

- Precondition to request the all-app run: ≥3 families through the runner with
  `runtime_executed: true`, ≥2 with material runtime-sourced wins **that move
  named blockers**, Set-B at parity, classification frozen.
- This is the only point an external-review packet is warranted.

---

## 3. The only definition of progress

A **named scorecard blocker moving on same-contract, same-hardware
measurement**, with `host_materialization_in_hot_path: false` and a recorded
`win_source`. Green tests, new milestone numbers, audit surfaces, promotion
ledgers, and blocked external reviews are **not progress** and are not reported
as progress. No external review is needed for T1–T5; only T6 warrants one.

## 4. The fork this sequence forces

- **0.844x moves through the runner (T2), and a second blocker moves (T3):**
  V3 has a genuine performance source (internal residency + fused continuation).
  Proceed; this is the V3 high-performance release path.
- **The runner executes cleanly but the blockers do not move (kernels are at
  ceiling):** V3's broad-speedup premise is false. Reframe V3 as a
  capability/quality release (productized residency-aware execution runtime),
  drop the broad-speedup wording, and stop chasing a number with no source. Do
  not fake it; do not open another process thread to defer the conclusion.

## 5. Non-authorization

Authorizes no release, no POD spend, no all-app run, no public/broad V3-over-V2
wording, no V4/embedding/C-ABI. Gate stays `redo_required`.
