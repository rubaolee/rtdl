# Goal5387 X-HD Author Trace V2 Execution Result

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5387 executes the app-owned author trace v2 instrumentation on the current
POD for the Dragon -> AsianDragon `lb=256` Level-B diagnostic.

The result is a stronger author-side oracle for the `-lb` / heavy-offload status
machine:

```text
schema                                    = rtdl.goal5385.author.lb_status_trace.v2
HDResult                                  = 52.453487396240234
active_in_queue_size                      = 437645
raw_offload_rows_before_sort_reduce        = 27133990
status_count_offloading_append             = 27133990
status_count_init                          = 437645
load_balance_input_row_count               = 27133990
load_balance_group_count                   = 437645
load_balance_feedback_update_count          = 294
```

The v2 trace preserves Goal5374's core row-count oracle while adding state
evidence that Goal5374 did not expose:

```text
cmin2_initial_hash
cmin2_after_ray_hash
cmin2_after_load_balance_hash
cmin2 sample indices and sample values
raw_offload_row_hash
raw offload row point-id and cell-id samples
status miss/completed/aborted counters
loadBalanceProcessing input/group/feedback counts
```

This is author-side instrumentation only.  It does **not** implement RTDL
explicit `-lb` support.

## Artifacts

Primary result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
```

Raw POD evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_lb256_status_trace_v2_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_patch_summary_pod.json
```

Implementation and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace_v2.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5387_author_trace_v2_execution.py
tests/goal5387_author_trace_v2_instrumentation_test.py
tests/goal5387_author_trace_v2_execution_test.py
```

## POD Execution

The current POD wrapper was used:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Preflight result:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

The author v2 trace was executed from an isolated author source copy:

```text
/tmp/xhd-goal5387/author
```

The build artifact was:

```text
/tmp/xhd-goal5387/build-gcc11-optix77-fast/bin/hd_exec
```

The author tree copy was patched only in the external author source:

```text
src/hd_impl/hausdorff_distance_rt.h
src/rt/launch_parameters.h
src/rt/shaders/shaders_nn_uniform_grid.cu
```

No RTDL core file is modified by the author instrumentation.

## Input Scope

The diagnostic pair is the current Level-B public Dragon -> AsianDragon route:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
input1_num_points = 437645
input2_num_points = 3609600
lb = 256
num_points_per_cell = 15
variant = rt
execution = gpu
```

This is not exact paper dataset identity.  It remains a Level-B public /
same-source diagnostic.

## Comparison To Goal5374

Goal5374 provided the first author-side raw status trace.  Goal5387 preserves
the same core counts:

| Field | Goal5374 | Goal5387 |
|---|---:|---:|
| active in-queue size | 437645 | 437645 |
| iteration 3 OffloadingSize | 27133990 | 27133990 |
| raw offload rows before sort/reduce | 27133990 | 27133990 |
| status offloading append count | 27133990 | 27133990 |
| status init count | 437645 | 437645 |

The result artifact records:

```text
comparison_to_goal5374.all_core_counts_match_goal5374 = true
decision.author_trace_v2_oracle_ready = true
```

## Why This Matters

Goal5381 and Goal5383 showed that current RTDL bridge probes produce only:

```text
2188225 rows
```

against the author oracle:

```text
27133990 rows
```

That mismatch means the remaining `-lb` gap is not a local performance issue or
a simple bridge vectorization issue.  It is a status-machine semantics issue.

Goal5387 gives the next RTDL counterpart enough author-side evidence to compare
more than counts:

```text
per-round cmin2/current-best state;
raw offload row identity hashes and samples;
miss/completed/offload/aborted status counters;
loadBalanceProcessing feedback counts.
```

The next meaningful goal should compare an RTDL native/generic multi-round
status stream against this stronger oracle.

## Verification

Focused local tests:

```text
py -m unittest \
  tests.goal5387_author_trace_v2_execution_test \
  tests.goal5387_author_trace_v2_instrumentation_test \
  tests.goal5386_author_trace_v2_patch_plan_test \
  tests.goal5385_author_trace_v2_spec_test \
  tests.goal5384_multiround_status_requirements_test \
  tests.goal5384_multiround_active_query_status_test
```

Result:

```text
Ran 24 tests in 3.187s
OK
```

The local Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

is noisy environment output.  The tests pass.

## Claim Boundary

Allowed:

```text
Author trace v2 instrumentation was implemented and executed on POD.
The author v2 trace preserves Goal5374 core counts.
The author v2 trace adds hashes, samples, status counters, and feedback counts.
This creates a stronger oracle for the next RTDL status-machine counterpart.
```

Forbidden:

```text
RTDL explicit -lb support is not implemented.
RTDL row-count parity is not claimed.
Figure 7 reproduction is not claimed.
Figure 11 reproduction is not claimed.
Same-denominator memory parity is not claimed.
Author RT-core algorithm parity is not claimed.
Author-vs-RTDL performance ratio is not claimed.
Exact paper dataset reproduction is not claimed.
Full X-HD paper reproduction is not claimed.
```

The artifact claim boundary records:

```text
author_v2_trace_implemented = true
author_v2_trace_executed_on_pod = true
author_v2_trace_oracle_claimed = true
explicit_lb_support_claimed = false
rtdl_row_count_parity_claimed = false
figure7_reproduction_claimed = false
figure11_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
```

## Next Work

The next goal should be an RTDL counterpart against the Goal5387 oracle:

```text
rtdl_native_multi_round_status_stream_against_author_trace_v2
```

That counterpart should not start from bridge vectorization.  It should first
match the author denominator and status transitions:

```text
active in-queue size;
raw offload rows before sort/reduce;
status offload/miss/completed/aborted counts;
cmin2/current-best state hashes or samples;
loadBalanceProcessing feedback counts.
```

If that cannot be matched generically, the correct outcome is a fail-closed
`-lb` limitation, not a fake row-count or memory parity claim.
