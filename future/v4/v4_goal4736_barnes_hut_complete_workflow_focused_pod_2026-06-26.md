# V4 Goal4736 Barnes-Hut Complete Workflow Focused POD

Date: 2026-06-26

Status: `focused_pod_complete_pending_external_review_debt`

Decision:
`barnes_hut_complete_aggregate_weighted_workflow_candidate_row_passes_frozen_gates`

## Purpose

Goal4735 selected Barnes-Hut for the next fresh generic-operator target and
froze the gates before measurement. Goal4736 ran that protocol on the same RT
hardware POD.

The question was narrow:

Can Barnes-Hut move from `deferred/subprobe` to a complete app-level V4
candidate row using a generic aggregate-frontier device-column route plus
explicit partner weighted-vector continuation, without adding a Barnes-Hut
native kernel?

Answer: yes, as a bounded complete workflow candidate row.

## Evidence

Evidence directory:

- `future/v4/evidence/v4_goal4735_barnes_hut_focused_20260626/`

Primary summary:

- `future/v4/evidence/v4_goal4735_barnes_hut_focused_20260626/summary.json`

Raw rows:

- `v2_14_serious.json`
- `v3_0_2_serious.json`
- `v4_current_serious.json`
- `v2_14_correctness.json`
- `v3_0_2_correctness.json`
- `v4_current_correctness.json`

## Frozen Routes

| version | route |
|---|---|
| V2.14 | `v2_14_optix_host_frontier_numba_cpu_continuation` |
| V3.0.2 | `v3_0_2_device_columns_explicit_partner_continuation` |
| V4 current | `v4_candidate_runner_explicit_partner_continuation` |

## Serious Result

Scale:

- body count: `32768`
- partner: `cupy`
- repeat/warmup: `7/2`
- serious rows skip CPU validation because correctness is checked separately at
  `2048` bodies.

| version | hot sec | wall sec | route note |
|---|---:|---:|---|
| V2.14 | 31.579627890139818 | 31.579627890139818 | host frontier materialization plus Numba CPU continuation |
| V3.0.2 | 0.11210632546680069 | 0.17708975076675415 | device columns plus explicit partner continuation |
| V4 current | 0.11179901493283843 | 0.15427596494555473 | V4 runner plus explicit partner continuation |

Ratios:

| gate | result | pass |
|---|---:|---|
| V4/V2.14 full hot >= 1.20x | 282.46785456124815x | true |
| V4/V2.14 full wall >= 1.10x | 204.69570811814097x | true |
| V4/V3.0.2 full hot >= 0.98x | 1.00274877675932x | true |

Additional V4 properties:

- V4 host frontier materialization in hot path: false
- partner migration counted as speed: false
- frontier rows materialized on host: false
- row offsets materialized on host: false

## Correctness Companion

Scale:

- body count: `2048`
- compared against:
  `sum_aggregate_frontier_weighted_vectors_2d_cpu_reference`
- tolerance: `1e-7`

| version | validation |
|---|---|
| V2.14 | pass |
| V3.0.2 | pass |
| V4 current | pass |

V4 max absolute differences:

- force_x: `1.9326762412674725e-12`
- force_y: `2.5011104298755527e-12`

## Interpretation

Barnes-Hut can now be represented as a complete app-level V4 candidate row:

`generic aggregate-frontier device columns plus explicit partner weighted-vector continuation`

This is a real app-level result against V2.14 because V2.14 spends the hot path
materializing host frontier rows and running CPU continuation, while V4 keeps
the frontier columns device-resident and feeds the partner continuation.

This is not a broad new V4-over-V3 speedup. V4 is only near parity/slightly
faster than V3.0.2 (`1.003x`) on the same current device-column workflow. The
claim is therefore:

- strong V4/V2.14 app-level improvement;
- V3 no-regression;
- complete workflow candidate row;
- no RT-core force-law claim;
- no app-specific Barnes-Hut native kernel claim.

## Matrix Effect

Goal4729 previously classified Barnes-Hut as:

`closed_deferred_subprobe_not_complete_app_route`

Goal4736 may update the next matrix as:

`complete_app_candidate_win_vs_v2_14__v3_no_regression__not_rt_core_force_law`

The old Goal4729 row is not erased; it is superseded for Barnes-Hut complete
workflow purposes by this focused POD run.

## Claim Boundary

Goal4736 authorizes the bounded internal evidence statement above. It does not
authorize:

- final V4 tag;
- public all-benchmark speedup claim;
- RT-core force-law speedup claim;
- native Barnes-Hut kernel claim;
- app-specific engine logic;
- automatic partner selection;
- true-zero-copy wording;
- broad V4-over-V3 speedup wording.

## Goal-Level Decision Audit

1. Was I being foolish?
   No. The gates were frozen in Goal4735 before this run, and the run measured
   complete V2/V3/V4 routes plus correctness companion rows.

2. If yes, what action made the decision foolish?
   The foolish action would be calling the older aggregate-frontier subprobe a
   complete app row without running the weighted-vector workflow under frozen
   gates.

3. Was there another path?
   Yes. Keep Barnes-Hut deferred and open Spatial RayJoin. That path is
   higher-risk and ignores an already runnable complete aggregate workflow.

4. Can I now try a different path that actually solves the problem?
   Yes. Update the next app matrix with this Barnes-Hut candidate row and then
   decide whether the remaining blockers still prevent a formal V4 tag.

## Non-Authorization

Goal4736 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
