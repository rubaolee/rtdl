# V4 Goal4733 Triangle Counting V3-Regression Resolution

Date: 2026-06-26

Status: `focused_pod_rerun_complete_pending_external_review_debt`

Decision:
`classify_goal4669_triangle_v4_vs_v3_regression_as_low_repeat_sampling_artifact_after_high_repeat_focused_rerun`

## What Happened

The Goal4669 serious app-level matrix reported triangle counting as:

| comparison | hot speedup |
|---|---:|
| V4 / V2.14 | 4.055x |
| V4 / V3.0.2 | 0.948x |

The V4/V3 regression was on a very small hot metric: roughly `0.199 ms` versus
`0.189 ms`, measured with only `repeat=7`. Before changing generic runtime code,
Goal4733 reran the same triangle-counting serious fixture with a focused,
high-repeat protocol.

## Focused POD Rerun

Evidence:

- `future/v4/evidence/v4_goal4733_triangle_focused_20260626/summary.json`
- `future/v4/evidence/v4_goal4733_triangle_focused_20260626/summary.md`

Protocol:

- Same RT-hardware POD.
- Same `k4_32768` triangle fixture scale.
- V2.14 baseline: `rt_graph_2a1_generic_rt`.
- V3.0.2 baseline: `rt_graph_2a1_segmented_generic_rt`.
- V4 current: `rt_graph_2a1_segmented_generic_rt`.
- High-repeat query timing: `repeat=201`, `warmup=20`.
- Correctness parity required for every row.

Result:

| version | mode | hot sec | query median ms | parity | prepared reused |
|---|---|---:|---:|---|---|
| V2.14 | `rt_graph_2a1_generic_rt` | 0.0010402016341686249 | 1.0402016341686249 | true | n/a |
| V3.0.2 | `rt_graph_2a1_segmented_generic_rt` | 0.000170096755027771 | 0.170096755027771 | true | true |
| V4 current | `rt_graph_2a1_segmented_generic_rt` | 0.00016302242875099182 | 0.16302242875099182 | true | true |

Ratios:

| comparison | hot speedup |
|---|---:|
| V4 / V2.14 | 6.380727131464089x |
| V4 / V3.0.2 | 1.0433948035922396x |

The high-repeat rerun clears the V3-regression row. V4 is slightly faster than
V3.0.2 on the measured replay query median and substantially faster than the
V2.14 generic baseline on this route.

## Phase Evidence

V3.0.2 phase split:

- Build-once total: `316.64255261421204 ms`.
- Replay query median: `0.170096755027771 ms`.
- Replay queries/s: `5802.516825145005`.

V4 current phase split:

- Build-once total: `230.67712783813477 ms`.
- Replay query median: `0.16302242875099182 ms`.
- Replay queries/s: `6037.618359999454`.

V4 residency metadata passed:

- prepared scene reused: true
- prepared ray batch used: true
- ray columns partner-owned: true
- query rays uploaded each run: false
- ray weights uploaded each run: false

## Interpretation

Goal4733 did not require a code optimization after the focused rerun. The
reported Goal4669 V4/V3 triangle regression is best classified as a
low-repeat sampling artifact on a sub-millisecond hot metric.

This result can update the app-level matrix only as a new focused delta row. It
does not erase the old Goal4669 frozen row, and it does not authorize a final
V4 release tag by itself.

## Claim Boundary

Goal4733 supports the following bounded statement:

Triangle counting, on the serious `k4_32768` fixture and high-repeat focused
rerun, passed correctness parity and measured V4/V2.14 hot `6.381x` and
V4/V3.0.2 hot `1.043x`.

Goal4733 does not authorize:

- final V4 tag
- public all-benchmark speedup claim
- whole-project high-performance claim
- geomean headline
- arbitrary callback support
- app-specific native kernel claim
- true-zero-copy wording

## Goal-Level Decision Audit

1. Was I being foolish?
   No for this decision. It would have been foolish to optimize or reframe a
   0.2 ms hot-path regression before checking whether `repeat=7` was
   under-sampling noise.

2. If yes, what action made the decision foolish?
   The earlier weak action was accepting a low-repeat sub-millisecond matrix row
   as stable enough to decide route quality.

3. Was there another path?
   Yes: immediately change triangle code. That would risk app-level tuning
   before proving a real generic-runtime defect.

4. Can I now try a different path that actually solves the problem?
   Yes. Treat Goal4733 as a focused delta that clears the triangle V3 regression
   and move to the next unresolved blocker instead of staying on a cleared row.

## Non-Authorization

Goal4733 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
