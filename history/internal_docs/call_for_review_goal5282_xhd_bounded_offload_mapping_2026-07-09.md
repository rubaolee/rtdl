# Call For Review - Goal5282 X-HD Bounded Offload Mapping

Please strictly review Goal5282.

Files:

```text
history/internal_docs/goal5282_xhd_bounded_offload_mapping_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5282_author_offload_mapping_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_offload_mapping.py
tests/goal5282_xhd_offload_author_mapping_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
```

Context:

```text
Goal5277 established Figure 11 denominator mismatch.
Goal5279 added generic heavy/offload worklist reference telemetry.
Goal5280 added a non-X-HD consumer.
Goal5281 added native/POD v2 telemetry for generic offload frontier rows.
Goal5282 maps that generic telemetry to author-shaped OffloadingSize / WL /
WL Heavy Peak fields.
```

Requested verdict labels:

```text
approve_goal5282_xhd_bounded_offload_mapping
revise_goal5282_xhd_bounded_offload_mapping
block_goal5282_xhd_bounded_offload_mapping
```

Review questions:

1. Does Goal5282 correctly map generic `heavy_offload_peak_rows` to an
   author-shaped `OffloadingSize` row-count candidate?
2. Does it correctly compute author-width `WL Heavy Peak` as
   `OffloadingSize * 2 * sizeof(uint32_t)`?
3. Does it clearly distinguish that author-width candidate from RTDL's measured
   native queue bytes, which currently use 64-bit id pairs?
4. Does it correctly leave `WL` not aligned because RTDL v2 `in_queue_capacity`
   is attempted frontier hits, not author `in_queue + miss_queue` over source
   points?
5. Is `same_denominator_author_figure11=false` the right decision after this
   mapping?
6. Is the helper app-owned and free of RTDL core / native X-HD-specific
   semantics?
7. Do the tests protect against misreading the mapping as Figure 11
   reproduction or author memory parity?
8. Should the next step be a shape-only Figure 11 candidate row, or should
   Figure 11 be closed as denominator-not-aligned under the current RTDL route?
9. Are there any required amendments before Goal5282 can be marked externally
   reviewed and approved?

Expected answer shape:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to review questions:
1. ...
```

Claim boundary to enforce:

```text
Goal5282 may claim an author-shaped offload mapping exists.
Goal5282 may not claim Figure 11 reproduction, author memory parity,
same-denominator comparison, or memory/performance ratios.
```
