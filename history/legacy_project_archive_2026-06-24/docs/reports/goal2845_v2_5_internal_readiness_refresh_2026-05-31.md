# Goal2845: v2.5 Internal Readiness Refresh

Date: 2026-05-31

Status: implemented, externally reviewed, consensus accepted with boundary

## Purpose

Goal2806 created the v2.5 internal readiness packet after the first clean pod gate. Since then, Goal2835 through Goal2844 added a new hardening chain:

- primitive-payload partner-continuation entrypoint metadata;
- fixed-radius graph entrypoint metadata;
- app-facing RTNN same-stream runner mode;
- a 65K same-stream cost-boundary probe;
- an explicit execution-path policy that keeps direct graph replay preferred when no partner continuation is needed.

Goal2845 refreshes the internal readiness index so that this post-2808 hardening chain is machine-visible instead of living only in reports.

## Implementation

Updated:

- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2811_rtnn_direct_aggregate_kernel_test.py`

The readiness packet now indexes:

- Goal2835, Goal2837, Goal2839, Goal2841, and Goal2843 reports;
- Goal2836, Goal2838, Goal2840, Goal2842, and Goal2844 consensus reports;
- the five matching Gemini review files;
- `execution_path_policy` as a core validation.

The exact v2.4/v2.5 module-band pod run also exposed one stale test in Goal2811. The native code had moved from the old `&d_aggregate.ptr` source spelling to a cleaner `CUdeviceptr d_aggregate = prepared->d_ranked_aggregate->ptr` plus `&d_aggregate` kernel argument. Goal2845 updates only that source-shape assertion; it does not change native runtime behavior.

## Validation

Local focused validation:

```text
py -3 -m unittest \
  tests.goal2811_rtnn_direct_aggregate_kernel_test \
  tests.goal2806_v2_5_internal_readiness_packet_test \
  tests.goal2843_v2_5_execution_path_policy_test

Ran 16 tests in 0.051s
OK
```

Pod broad signal before the Goal2811 assertion repair:

```text
commit: 1141393dc6691cc2f61b01fc33dbbdfbd8a442a1
default broad run: Ran 239 tests in 105.259s, OK
exact Goal2621-Goal2843 module band: Ran 694 tests in 16.854s, FAILED
only failure: Goal2811 stale source-shape assertion
```

Exact module-band rerun after committing this repair:

```text
commit: 6ebb0bce50efa30c262fdf526f3db055879072a3
module_count: 144
scope: tests.goal2621_* through tests.goal2845_*
elapsed_sec: 12.593
Ran 697 tests in 10.506s
OK (skipped=1)
```

## Boundary

Goal2845 does not authorize release, public speedup wording, broad RT-core wording, whole-app speedup wording, true zero-copy wording, package-install wording, Triton preview auto-selection, or app-specific native engine logic.

It is an internal evidence-index refresh and stale-test repair.

Independent review:

- `docs/reviews/goal2846_gemini_review_goal2845_v2_5_internal_readiness_refresh_2026-05-31.md`

Consensus:

- `docs/reports/goal2846_goal2845_v2_5_internal_readiness_refresh_consensus_2026-05-31.md`

## Codex Verdict

`accept-with-boundary`

The readiness index is now more current and the one stale broad-band assertion is corrected. No public claims change.
