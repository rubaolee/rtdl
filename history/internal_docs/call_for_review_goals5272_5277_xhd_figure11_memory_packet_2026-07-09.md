# Call For Review - Goals5272-5277 X-HD Figure 11 Memory Packet

Please strictly review the X-HD Figure 11 memory work from Goals5272-5277.

## Scope

This packet is **not** a Figure 11 reproduction claim.  It asks whether the
project has honestly established:

```text
1. the author-side Figure 11 memory matrix,
2. the RTDL-side bounded/status-bearing memory evidence,
3. the denominator mismatch that prevents an author-vs-RTDL memory ratio today,
4. the next required system gap if Figure 11 remains a target.
```

## Files Under Review

Goal reports and calls:

```text
history/internal_docs/goal5272_xhd_figure11_author_memory_log_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5272_xhd_figure11_author_memory_log_matrix_2026-07-09.md
history/internal_docs/goal5273_xhd_rtdl_memory_accounting_boundary_result_2026-07-09.md
history/internal_docs/call_for_review_goal5273_xhd_rtdl_memory_accounting_boundary_2026-07-09.md
history/internal_docs/goal5274_xhd_hd_exec_memory_accounting_integration_result_2026-07-09.md
history/internal_docs/call_for_review_goal5274_xhd_hd_exec_memory_accounting_integration_2026-07-09.md
history/internal_docs/goal5275_xhd_native_memory_telemetry_result_2026-07-09.md
history/internal_docs/call_for_review_goal5275_xhd_native_memory_telemetry_2026-07-09.md
history/internal_docs/goal5276_xhd_rtdl_bounded_memory_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5276_xhd_rtdl_bounded_memory_matrix_2026-07-09.md
history/internal_docs/goal5277_xhd_memory_denominator_alignment_decision_result_2026-07-09.md
history/internal_docs/call_for_review_goal5277_xhd_memory_denominator_alignment_decision_2026-07-09.md
```

Primary artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5272_figure11_author_memory_log_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5273_rtdl_memory_accounting_boundary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5274_hd_exec_memory_accounting_attached_example_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_tiny3d_native_memory_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_stanford_sample256_native_memory_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5277_memory_denominator_alignment_decision_2026-07-09.json
```

Implementation/tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/xhd_rtdl_memory_matrix.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
src/native/optix/rtdl_optix_core.cpp
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
tests/goal5272_xhd_figure11_author_memory_log_matrix_test.py
tests/goal5273_xhd_rtdl_memory_accounting_test.py
tests/goal5273_xhd_rtdl_memory_accounting_boundary_artifact_test.py
tests/goal5274_xhd_hd_exec_memory_accounting_integration_test.py
tests/goal5274_xhd_hd_exec_memory_accounting_artifact_test.py
tests/goal5275_xhd_native_memory_telemetry_contract_test.py
tests/goal5275_xhd_native_memory_telemetry_artifact_test.py
tests/goal5276_xhd_rtdl_bounded_memory_matrix_test.py
tests/goal5277_xhd_memory_denominator_alignment_decision_test.py
```

## Expected Evidence Chain

### Goal5272

Extracts the author Figure 11 memory matrix from the author repository's
`draw_mem.py` and `expr/logs/mem` contract.  It records NN-KD / NN-Clover /
X-HD totals and X-HD breakdown fields:

```text
BVH
Grid
MBRs B
WL
WL Heavy Peak
```

This is author-log evidence only.

### Goal5273

Defines a status-bearing RTDL memory accounting boundary.  The important
historical point: Goal5273 predates the later author-source audit, so Goal5277
must be read as a semantic tightening of the `WL` field, not as proof that
Goal5273 already had the final denominator interpretation.

### Goal5274

Adds opt-in `--include-memory-accounting` to the app-owned RTDL
hd_exec-compatible entrypoint.  The output is status-bearing RTDL accounting,
not the author's raw Figure 11 Memory schema.

### Goal5275

Adds native OptiX memory telemetry for the generic 3-D cell-MBR frontier route.
It maps measured GAS output-buffer bytes to a status-bearing RTDL BVH field
when available, while keeping transient build workspace and route buffers as
RTDL-only fields.

### Goal5276

Builds a bounded RTDL memory matrix from the Goal5275 telemetry artifacts.  The
matrix is reviewable evidence but keeps:

```text
same_denominator_author_figure11 = false
figure11_reproduced = false
```

### Goal5277

Audits the author source and makes the final denominator decision:

```text
Author WL = in_queue + miss_queue
          = 2 * n_points_a * sizeof(uint32_t)

Author WL Heavy Peak = peak heavy-cell offload queue
                     = offloading_size * 2 * sizeof(uint32_t)
```

Current RTDL:

```text
RTDL WL = generic frontier row-table capacity
RTDL WL Heavy Peak = unavailable; no author-like heavy offload queue
```

Therefore:

```text
same_denominator_author_figure11 = false
Figure 11 remains not_reproduced
```

## Validation Reported By Team

Latest focused validation:

```text
py -m unittest \
  tests.goal5277_xhd_memory_denominator_alignment_decision_test \
  tests.goal5276_xhd_rtdl_bounded_memory_matrix_test \
  tests.goal5275_xhd_native_memory_telemetry_artifact_test \
  tests.goal5275_xhd_native_memory_telemetry_contract_test \
  tests.goal5274_xhd_hd_exec_memory_accounting_integration_test \
  tests.goal5273_xhd_rtdl_memory_accounting_test \
  tests.goal5273_xhd_rtdl_memory_accounting_boundary_artifact_test

Ran 20 tests OK
```

Other checks:

```text
py_compile OK for xhd_memory_accounting.py and xhd_rtdl_memory_matrix.py
manifest / Goal5276 / Goal5277 JSON parse OK
git diff --check OK for touched files
```

## Review Questions

1. Does Goal5272 correctly reproduce the author-side Figure 11 memory-log matrix
   extraction, without overclaiming RTDL reproduction?
2. Is Goal5273's status-bearing RTDL memory accounting boundary useful and
   honest, given that Goal5277 later tightens the `WL` denominator semantics?
3. Is Goal5274's opt-in hd_exec-compatible memory output clearly marked as RTDL
   status-bearing accounting, not author Figure 11 raw memory?
4. Does Goal5275's native telemetry honestly map GAS output bytes to a bounded
   RTDL BVH-like field without claiming author memory parity or allocator peak
   parity?
5. Does Goal5276 build a useful bounded RTDL memory matrix while correctly
   refusing author-vs-RTDL memory ratios?
6. Does Goal5277 correctly establish that author `WL` and RTDL current `WL` are
   not the same denominator?
7. Does Goal5277 correctly establish that current RTDL has no author-like
   `WL Heavy Peak` denominator?
8. Is it correct to close the current Figure 11 route as
   `not_reproduced / denominator_not_aligned`, rather than forcing a fake memory
   ratio?
9. Is the next real system gap correctly identified as a generic heavy-cell /
   offload worklist API plus native peak queue telemetry, if Figure 11 remains
   a target?
10. Are there any claims in this packet that should be weakened before the X-HD
    full-reproduction status is summarized?

## Expected Answer Shape

```text
Verdict: approve_goals5272_5277_xhd_figure11_memory_packet |
         approve_with_required_amendments |
         reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Review question answers:
1. ...
2. ...
...
10. ...
```

Requested approval label:

```text
approve_goals5272_5277_xhd_figure11_memory_packet__figure11_not_reproduced_denominator_not_aligned
```
