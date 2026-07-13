# Goal5389 X-HD Bridge Trace Summary Smoke Result

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5389 wires the Goal5388 generic status-trace summary into the current X-HD
active-query bridge probe and runs a source-limited POD smoke.

The smoke proves that current RTDL bridge rows can now emit a generic
hash/sample summary from actual RTDL offload rows:

```text
contract = generic_active_query_status_trace_summary_v1
source_limit = 64
rtdl active_query_count = 64
rtdl offload row_count = 320
rtdl raw_offload_row_hash = 6439553744306743619
rtdl sample source_ids = [0, 32, 63]
rtdl sample cell_ids = [6279, 6286, 6145]
```

This is still **not** `-lb` parity:

```text
author active_in_queue_size = 437645
author raw_offload_rows_before_sort_reduce = 27133990
source-limited RTDL offload rows = 320
row_count_parity = false
hash_parity = false
```

## Artifacts

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_bridge_trace_summary_smoke.json
```

Raw POD smoke:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_source64_trace_summary_smoke_pod.json
```

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5389_bridge_trace_summary_smoke.py
tests/goal5381_active_query_frontier_bridge_probe_test.py
tests/goal5389_bridge_trace_summary_smoke_test.py
```

## What Changed

`run_xhd_active_query_frontier_bridge_probe.py` now calls:

```text
active_query_status_trace_summary_numpy_columns
```

on the bridge's actual `offload_rows`.  The bridge summary now includes:

```text
trace_summary.row_count
trace_summary.status_count_offloading
trace_summary.active_query_count
trace_summary.raw_offload_row_hash
trace_summary.sample_indices
trace_summary.samples
comparison_to_author.hash_comparable_to_author
comparison_to_author.hash_parity
comparison_to_author.sample_comparable_to_author
```

The probe can read either the old Goal5374 count-only oracle or the new Goal5387
author trace v2 oracle.

## POD Smoke

The source-limited smoke used the current POD wrapper and the remote
`/tmp/rtdl_goal5364` workspace after syncing the modified RTDL files and bridge
script.

Command shape:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py \
  --input1 /tmp/xhd_goal5234/data/dragon.ply \
  --input2 /tmp/xhd_goal5234/data/asian_dragon.ply \
  --input-type ply \
  --n-dims 3 \
  --source-limit 64 \
  --grid-shape 96,60,72 \
  --grid-cell-builder native_cuda \
  --grid-cell-point-order input-stable \
  --initial-state local-grid-cell \
  --local-grid-seed-executor native_cuda \
  --radius 79.2156982421875 \
  --max-inline-points 256 \
  --frontier-row-capacity 1000000 \
  --inline-nearest \
  --frontier-status-probe-mode active-initial-best-prune \
  --author-oracle xhd_goal5387_author_trace_v2_execution.json
```

The follow-up shell one-liner used to print the summary had a quoting error, but
the bridge probe itself completed and wrote the summary JSON.  The artifact was
downloaded and validated locally.

## Verification

Focused tests:

```text
py -m unittest \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5388_active_query_trace_summary_test \
  tests.goal5388_status_trace_summary_contract_test \
  tests.goal5389_bridge_trace_summary_smoke_test
```

Result:

```text
Ran 13 tests in 3.097s
OK
```

Additional bridge/API focused tests after wiring:

```text
py -m unittest \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5388_active_query_trace_summary_test \
  tests.goal5388_status_trace_summary_contract_test \
  tests.goal5383_active_initial_best_status_probe_test

Ran 13 tests in 2.659s
OK
```

## Claim Boundary

Allowed:

```text
The current RTDL bridge probe can emit a generic status-trace summary from
actual RTDL offload rows.
The source-limited POD smoke is comparable in shape to the Goal5387 author v2
trace fields.
The source-limited smoke does not match the author full denominator.
```

Forbidden:

```text
Do not claim explicit -lb support.
Do not claim full-row parity.
Do not claim hash/sample parity.
Do not claim Figure 7 or Figure 11 reproduction.
Do not claim same-denominator memory.
Do not claim author RT-core algorithm parity.
Do not claim author-vs-RTDL performance ratio.
Do not claim exact paper dataset reproduction.
Do not claim full X-HD paper reproduction.
```

## Next Work

Goal5389 proves trace-summary plumbing, not semantic parity.  The next work is
still a full or bounded native status-stream parity gate against Goal5387:

```text
active_query_count = 437645
raw offload row count = 27133990
row hash / samples comparable to Goal5387
status miss/completed/aborted counts
feedback update counts
```

If the full native status stream cannot match those fields generically, the
correct closeout is fail-closed `-lb` support, not a partial claim.
