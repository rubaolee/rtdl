# Goal2857 v2.5 Readiness Indexes Packet Runner

Date: 2026-05-31

Verdict: **accept-with-boundary**

Goal2857 refreshes the v2.5 internal readiness index so the new Goal2855
canonical packet runner is part of the readiness surface rather than a side
artifact.

This is a metadata-only readiness update. It does not change benchmark logic,
partner logic, native RTDL behavior, or any public claim boundary.

It also indexes the Goal2856 Gemini review and consensus record for Goal2855.

## What Changed

`src/rtdsl/v2_5_internal_readiness.py` now indexes:

- `docs/reports/goal2855_v2_5_current_canonical_harness_packet_runner_2026-05-31.md`
- `docs/reports/goal2856_goal2855_v2_5_canonical_packet_runner_consensus_2026-05-31.md`
- `docs/reviews/goal2856_gemini_review_goal2855_v2_5_canonical_packet_runner_2026-05-31.md`
- `docs/reports/goal2855_current_canonical_harness_runner_pod/goal2855_summary.json`

The readiness packet adds a `current_canonical_runner` block that records:

- summary path,
- status,
- `all_pass`,
- artifact count,
- expected artifact count,
- source commit,
- dirty artifact map,
- claim-boundary violation map,
- runner metadata.

Validation now rejects the packet if the runner summary is missing, not passing,
does not cover seven artifacts, records dirty artifacts, records claim-boundary
violations, or lacks a real source commit.

## Allowed Next Action

The first allowed next action changed from:

`keep_current_canonical_harness_and_observability_guards_green`

to:

`keep_goal2855_current_canonical_packet_runner_green`

That points future operators at the actual one-command packet runner rather than
the older manual harness packet wording.

## Boundary

This is **not a release authorization**. The readiness packet still blocks:

- v2.5 release,
- release tag action,
- public speedup wording,
- broad RT-core speedup wording,
- whole-app speedup wording,
- true-zero-copy wording,
- package-install wording,
- Triton preview auto-selection,
- app-specific native engine logic.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2857_v2_5_readiness_indexes_packet_runner_test \
  tests.goal2855_v2_5_current_canonical_harness_packet_runner_test \
  tests.goal2853_v2_5_readiness_next_actions_refresh_test \
  tests.goal2849_v2_5_readiness_indexes_current_canonical_harness_test \
  tests.goal2806_v2_5_internal_readiness_packet_test
```

Expected result:

```text
OK
```

## Conclusion

Goal2857 accepts the packet-runner readiness index update. Future v2.5 health
checks should use the Goal2855 runner as the current canonical packet command,
while final release consensus remains a separate user-requested 3-AI gate.
