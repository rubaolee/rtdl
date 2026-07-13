# Call For Review - Goal5374 X-HD Author `-lb` Status-Trace Oracle

Please strictly review Goal5374.

## Files To Review

Primary report:

```text
history/internal_docs/goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md
```

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
```

Raw POD evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_instrument_patch_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb256_status_trace_pod.json
```

Implementation / builders:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5374_author_lb_status_trace_oracle.py
```

Tests:

```text
tests/goal5374_author_lb_status_trace_instrumentation_test.py
tests/goal5374_author_lb_status_trace_oracle_test.py
```

Context artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5364_lb_trace_gate_author_pair_contract.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_inline_global_bound_lb_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5373_rtdl_status_machine_telemetry_surface.json
history/internal_docs/goal5372_xhd_author_shader_status_machine_gap_result_2026-07-09.md
history/internal_docs/goal5373_xhd_rtdl_status_machine_telemetry_surface_result_2026-07-09.md
```

## Review Context

Goals5363-5373 narrowed the X-HD `-lb` gap. The important prior conclusions are:

- explicit `-lb` is not supported by RTDL yet;
- scalar radius alignment is insufficient;
- raw RTDL kind2 rows do not equal author `OffloadingSize`;
- existing RTDL global-bound early break is not the author `cmax2` abort status;
- the current RTDL telemetry surface lacks author status-machine fields.

Goal5374 chooses the author-oracle path. It instruments the author source on a
POD and records author-side raw status fields for the Dragon -> AsianDragon
`lb=256` diagnostic.

## Key Claims To Verify

Goal5374 claims only:

```text
author_oracle_ready = true
explicit_lb_support_authorized = false
rtdl_counterpart_row_parity = false
```

The key numeric result is:

```text
Author OffloadingSize = 27133990
RawOffloadRowsBeforeSortReduce = 27133990
StatusOffloadingAppendCount = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
ActiveInQueueSize = StatusInitCount = 437645
```

The author-width byte formula should be:

```text
27133990 * 2 * sizeof(uint32_t) = 217071920
```

The report also keeps the existing RTDL mismatch visible:

```text
RTDL author-radius inline kind2 rows        = 21006960
RTDL author-radius no-inline raw kind2 rows = 304981889
```

## Questions For Reviewer

1. Does the patcher modify only app-owned / external author source, not RTDL
   core?
2. Is the instrumentation credible for the author `-lb` status-machine fields
   it claims to expose?
3. Does the POD patch summary prove all intended author files were patched?
4. Does the author trace artifact prove
   `RawOffloadRowsBeforeSortReduce == OffloadingSize == 27133990`?
5. Does the author trace artifact prove author-width bytes equal
   `OffloadingSize * 2 * sizeof(uint32_t)`?
6. Does the report correctly preserve the fact that RTDL still lacks row-count
   parity and that the current RTDL telemetry surface is insufficient?
7. Does the test suite check both the patcher structure and the oracle artifact
   invariants?
8. Does the report avoid claiming explicit `-lb` support, Figure 7/11
   reproduction, same-denominator memory parity, author RT-core parity,
   performance ratio, exact paper dataset reproduction, or full X-HD paper
   reproduction?
9. Is the next-goal recommendation correct: build an RTDL status-machine
   counterpart against this author oracle?
10. Are there any hidden denominator or instrumentation risks that should block
    Goal5375?

## Expected Answer Shape

Please answer in this format:

```text
Verdict:
  approve_goal5374_author_lb_status_trace_oracle
  OR approve_with_required_amendments
  OR block_goal5374_author_lb_status_trace_oracle

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  ...
  10. ...
```

## Requested Verdict Label If Approved

```text
approve_goal5374_author_lb_status_trace_oracle__rtdl_counterpart_next
```
