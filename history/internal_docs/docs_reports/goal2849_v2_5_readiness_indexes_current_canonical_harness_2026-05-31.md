# Goal2849 v2.5 Readiness Indexes Current Canonical Harness

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2847 produced a clean current-head RTX pod refresh of the seven canonical
v2.5 harness artifacts, and Goal2848 added independent Gemini review plus
Codex+Gemini consensus. Goal2849 folds that evidence into
`rt.v2_5_internal_readiness_packet(...)` so the latest canonical harness packet
is machine-visible instead of existing only as reports.

## Implementation

Updated:

- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2849_v2_5_readiness_indexes_current_canonical_harness_test.py`

The internal readiness packet now indexes:

- `docs/reports/goal2847_current_head_canonical_harness_refresh_2026-05-31.md`
- `docs/reports/goal2848_goal2847_current_head_canonical_harness_consensus_2026-05-31.md`
- `docs/reviews/goal2848_gemini_review_goal2847_current_head_canonical_harness_2026-05-31.md`
- the Goal2847 summary JSON
- the seven canonical v2.5 harness artifacts

The new `current_canonical_harness` metadata validates that all seven artifacts
carry:

- `status: pass`,
- source commit `23b047e5d44bfda7e535ca7ba78d94f195e2be86`,
- `source_dirty: []`,
- RTX pod identity `NVIDIA RTX A5000`.

## Boundary

This is not a v2.5 release authorization and not a public speedup claim. It
updates the internal readiness index only. The Goal2847 boundaries remain in
force: RTNN remains distribution-dependent, Hausdorff remains slower than the
optimized CuPy grouped-grid baseline, Barnes-Hut does not promote Triton vector
sum auto-selection, and the Barnes-Hut long CPU-heavy comparison window still
needs better progress logging.

## Validation

Local focused validation:

```text
py -3 -m unittest \
  tests.goal2849_v2_5_readiness_indexes_current_canonical_harness_test \
  tests.goal2847_current_head_canonical_harness_refresh_test \
  tests.goal2845_v2_5_internal_readiness_refresh_test \
  tests.goal2843_v2_5_execution_path_policy_test \
  tests.goal2841_rtnn_same_stream_scale_probe_test

Ran 20 tests in 0.103s
OK
```

Expanded local readiness validation:

```text
py -3 -m unittest \
  tests.goal2849_v2_5_readiness_indexes_current_canonical_harness_test \
  tests.goal2847_current_head_canonical_harness_refresh_test \
  tests.goal2845_v2_5_internal_readiness_refresh_test \
  tests.goal2843_v2_5_execution_path_policy_test \
  tests.goal2841_rtnn_same_stream_scale_probe_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 26 tests in 0.162s
OK
```

Pod validation from pushed `main`:

```text
commit: 3b229b4e
scope:
  tests.goal2849_v2_5_readiness_indexes_current_canonical_harness_test
  tests.goal2847_current_head_canonical_harness_refresh_test
  tests.goal2845_v2_5_internal_readiness_refresh_test
  tests.goal2843_v2_5_execution_path_policy_test
  tests.goal2841_rtnn_same_stream_scale_probe_test
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 26 tests in 0.028s
OK
```

Pod recent v2.5 module-band validation:

```text
commit: 3b229b4e
module_count: 146
scope: tests.goal2621_* through tests.goal2849_*

Ran 706 tests in 9.183s
OK (skipped=1)
```

## Codex Verdict

`accept-with-boundary`

Goal2849 makes the latest pod health evidence part of the v2.5 readiness index
without changing public claim authorization.
