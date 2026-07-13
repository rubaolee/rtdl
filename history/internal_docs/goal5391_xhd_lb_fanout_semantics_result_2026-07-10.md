# Goal5391 X-HD `-lb` Fanout Semantics Diagnostic

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5391 converts the Goal5390 full-source row/hash mismatch into a precise
fanout / transition-semantics requirement for the next implementation.

It does not run a new POD job. It uses the already-produced Goal5387 author
trace v2 oracle and the Goal5390 full-source RTDL trace-summary gate.

Key result:

```text
active_query_count parity = true

author rows per active query, aggregate = 62
RTDL rows per active query, aggregate   = 5

row_count_parity = false
hash_parity      = false
```

This proves the remaining `-lb` problem is not source-limited plumbing and not
primarily bridge runtime. The current RTDL stream has a different
status/offload denominator from the author status-machine stream.

## Artifacts

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5391_lb_fanout_semantics.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5391_lb_fanout_semantics.py
```

Tests:

```text
tests/goal5391_lb_fanout_semantics_test.py
```

Inputs:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_gate.json
```

## Evidence

Author trace v2:

```text
active_in_queue_size                = 437645
raw_offload_rows_before_sort_reduce = 27133990
raw_offload_row_hash                = 4333109858711462591
```

RTDL full trace summary:

```text
active_query_count   = 437645
raw_offload_rows     = 2188225
raw_offload_row_hash = 10510374331443640811
```

Derived aggregate fanout:

```text
27133990 / 437645 = 62, remainder 0
2188225  / 437645 = 5,  remainder 0
```

Delta:

```text
author rows - RTDL rows = 24945765
author aggregate rows per active - RTDL aggregate rows per active = 57
RTDL / author row ratio = 0.08064516129032258
```

## Interpretation

The active-query denominator is aligned:

```text
active_query_count_parity = true
```

But the emitted row stream denominator is not:

```text
row_count_parity = false
hash_parity = false
```

The cleanest classification is:

```text
status_stream_fanout_or_transition_semantics
```

This means the next implementation must change how the native status stream
emits active/offload transitions. It must not merely speed up the Python bridge,
repeat source-limited smoke, or format existing rows differently.

## Important Caveat

The aggregate divisions prove exact integer multiples at the total-row level:

```text
author total rows = 62 * active count
RTDL total rows   = 5  * active count
```

They do **not** prove per-query uniform fanout distribution. Goal5391 therefore
does not claim "every active query emits exactly 62 author rows." It claims the
aggregate denominator is wrong and exactly classifies the scale of that wrong
denominator.

## Requirements For The Next Native Stream

The next native implementation, if attempted, must be a generic RTDL status
stream:

```text
generic_native_multi_round_active_query_status_stream
```

Minimum comparison fields:

```text
active_query_count;
raw_offload_row_count;
raw_offload_row_hash;
sampled query/source ids;
sampled cell ids;
status_count_offloading;
miss/completed/aborted counters or explicit not-applicable evidence;
load-balance feedback count or explicit not-applicable evidence.
```

Forbidden shortcuts:

```text
hard-code 62 rows per active query;
use X-HD-specific native primitive names or paper semantics in RTDL core;
optimize bridge runtime as the main fix while row/hash parity is false;
use source-limited smoke as a substitute for full-source parity.
```

## Verification

Built artifact:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5391_lb_fanout_semantics.py
```

Focused tests:

```text
py -m unittest \
  tests.goal5391_lb_fanout_semantics_test \
  tests.goal5390_full_trace_summary_gate_test \
  tests.goal5388_active_query_trace_summary_test
```

Observed:

```text
Ran 10 tests in 1.480s
OK
```

The local Python warning:

```text
Could not find platform independent libraries <prefix>
```

is the known Windows Python environment noise and did not indicate test
failure.

## Claim Boundary

Allowed:

```text
Goal5391 is a fanout / transition-semantics diagnostic.
The aggregate row denominator is 62 rows per active for the author trace and
5 rows per active for the current RTDL trace.
The next implementation must change generic native status-stream semantics or
fail-close explicit -lb.
```

Forbidden:

```text
Do not claim explicit -lb support.
Do not claim row-count parity.
Do not claim hash/sample parity.
Do not claim per-query uniform fanout distribution.
Do not claim Figure 7 or Figure 11 reproduction.
Do not claim same-denominator memory.
Do not claim author RT-core algorithm parity.
Do not claim author-vs-RTDL performance ratio.
Do not claim exact paper dataset reproduction.
Do not claim full X-HD paper reproduction.
```

## Decision

Goal5391 rules out the next easy wrong path:

```text
bridge runtime optimization
```

as the main fix. A faster bridge would still emit the wrong row stream.

The next real decision remains:

```text
1. implement a genuine generic native multi-round active-query status stream
   that can change the row denominator and pass row/hash comparison; or
2. close explicit -lb as unsupported under the current RTDL route.
```

## Exit Label

```text
lb_fanout_semantics_mismatch__bridge_runtime_not_next_target
```
