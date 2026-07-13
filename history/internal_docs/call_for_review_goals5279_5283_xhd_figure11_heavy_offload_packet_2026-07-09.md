# Consolidated Call For Review - Goals5279-5283 X-HD Figure 11 Heavy/Offload Packet

Date: 2026-07-09

## Review Scope

Please strictly review the X-HD Figure 11 heavy/offload worklist packet,
Goals5279 through 5283.

This packet is the current review entry point for the Figure 11 memory line
after the denominator-alignment decision in Goal5277.  It asks whether the
project correctly:

1. introduced a generic RTDL heavy/offload worklist instead of an X-HD-specific
   queue clone;
2. proved that helper with a non-X-HD consumer;
3. exposed real native/POD v2 telemetry for generic offload frontier rows;
4. mapped that telemetry to X-HD author-shaped fields only as a bounded app
   mapping; and
5. closed the current Figure 11 line as not reproduced because the same
   denominator is still not aligned.

## Status Under Review

```text
Goals5279-5283: implemented; external review pending
```

Do not treat these goals as externally approved unless this consolidated review
approves them.

Requested status if approved:

```text
xhd_figure11_heavy_offload_line_closed__generic_worklist_ready__same_denominator_not_aligned
```

Meaning:

- RTDL has a generic heavy/offload worklist reference helper;
- that helper has non-X-HD consumer evidence;
- RTDL native OptiX can expose v2 generic offload-frontier telemetry;
- X-HD can map the generic offload row-count shape to author-shaped
  `OffloadingSize` and an author-width `WL Heavy Peak` candidate;
- the current RTDL route still does not share the author Figure 11 memory
  denominator;
- Figure 11 remains not reproduced;
- no author-vs-RTDL memory ratio is authorized.

## Prior Context

Goal5277 audited the author source and established the relevant denominator
gap:

```text
author WL = in_queue + miss_queue
author WL Heavy Peak = peak heavy-cell offload queue
current RTDL WL = generic frontier row-table capacity / attempted frontier hits
current RTDL route before this packet = no author-like heavy-offload peak
same_denominator_author_figure11 = false
```

Goal5278 then proposed the only coherent route forward if Figure 11 remained a
priority:

```text
generic heavy/offload worklist
non-X-HD consumer gate
native/POD telemetry ABI
bounded X-HD mapping
explicit Figure 11 disposition
```

This packet implements that sequence.

## Files To Review

### Goal Reports

```text
history/internal_docs/goal5279_generic_heavy_offload_worklist_reference_result_2026-07-09.md
history/internal_docs/goal5280_heavy_offload_non_xhd_consumer_gate_result_2026-07-09.md
history/internal_docs/goal5281_native_heavy_offload_telemetry_result_2026-07-09.md
history/internal_docs/goal5282_xhd_bounded_offload_mapping_result_2026-07-09.md
history/internal_docs/goal5283_xhd_figure11_disposition_result_2026-07-09.md
```

### Existing Per-Goal Call-For-Review Files

```text
history/internal_docs/call_for_review_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.md
history/internal_docs/call_for_review_goal5280_heavy_offload_non_xhd_consumer_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5281_native_heavy_offload_telemetry_2026-07-09.md
history/internal_docs/call_for_review_goal5282_xhd_bounded_offload_mapping_2026-07-09.md
history/internal_docs/call_for_review_goal5283_xhd_figure11_disposition_2026-07-09.md
```

### Primary Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5280_heavy_offload_non_xhd_consumer_gate_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5282_author_offload_mapping_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5283_figure11_disposition_2026-07-09.json
```

### Primary Implementation Files

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
src/rtdsl/optix_runtime.py
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_offload_mapping.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure11_disposition.py
```

### Primary Tests

```text
tests/goal5279_generic_heavy_offload_worklist_test.py
tests/goal5280_heavy_offload_non_xhd_consumer_gate_test.py
tests/goal5281_native_heavy_offload_telemetry_contract_test.py
tests/goal5281_native_heavy_offload_telemetry_artifact_test.py
tests/goal5282_xhd_offload_author_mapping_test.py
tests/goal5283_xhd_figure11_disposition_test.py
```

## Evidence Summary

### Goal5279 - Generic Heavy/Offload Worklist Reference

New public app-neutral helper:

```text
heavy_offload_worklist_numpy_columns(...)
```

New app-neutral constants:

```text
HEAVY_OFFLOAD_WORKLIST_CONTRACT = "generic_heavy_offload_worklist_v1"
HEAVY_OFFLOAD_WORKLIST_KIND_CODES = {"active": 1, "miss": 2, "deferred": 3}
HEAVY_OFFLOAD_WORKLIST_ROW_SCHEMA = (
  "work_source_id",
  "work_primitive_id",
  "work_begin_offset",
  "work_count",
  "work_kind_code",
  "work_cost_estimate",
  "lower_bound",
  "upper_bound",
)
```

Reference fixture:

```text
selected rows = 3
work_kind_codes = [active, miss, active] = [1, 2, 1]
in_queue_capacity = 4
miss_queue_capacity = 1
heavy_offload_peak_rows = 3
heavy_offload_queue_peak_bytes = 48
overflow behavior = fail-closed with zero partial rows
```

Claim boundary:

```text
not Figure 11 reproduction
not author memory parity
not native backend completion
not performance evidence
```

### Goal5280 - Non-X-HD Consumer

Adds a separate retry/backlog scheduler consumer:

```text
selected rows = 4
work_kind_codes = [deferred, active, miss, active] = [3, 1, 2, 1]
in_queue_capacity = 5
miss_queue_capacity = 1
deferred_queue_capacity = 1
heavy_offload_peak_rows = 4
heavy_offload_queue_peak_bytes = 64
overflow behavior = fail-closed
```

This consumer is not a geometry, Hausdorff, paper, or X-HD workload.  It exists
to test whether the helper is genuinely generic rather than merely
X-HD-shaped.

### Goal5281 - Native/POD v2 Telemetry ABI

Native OptiX keeps the existing v1 memory telemetry symbol and adds:

```text
rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v2
```

POD evidence:

```text
POD = 213.173.108.24:13502
GPU = NVIDIA RTX 4000 Ada Generation
native build = succeeded
exported symbols include v1 and v2 telemetry symbols
```

Runtime artifact:

```text
matched = true
telemetry schema = rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v2
frontier_kind_codes = [2, 2, 2, 2, 2, 2]
offload_row_count_from_rows = 6
heavy_offload_peak_rows = 6
heavy_offload_queue_peak_bytes = 96
```

Byte shape:

```text
6 rows * 2 ids * sizeof(uint64_t) = 96 bytes
```

This proves native/POD generic offload telemetry exists.  It does not prove
that these bytes are the author Figure 11 denominator.

### Goal5282 - X-HD Bounded Author-Shaped Mapping

App-owned mapping:

```text
author_offload_mapping_from_native_telemetry(native_memory)
```

Output artifact status:

```text
status = xhd_bounded_offload_mapping_ready__figure11_same_denominator_not_met
matched = true
```

Mapped fields:

```text
native offload rows = 6
author-shaped OffloadingSize = 6
author-width WL Heavy Peak candidate = 48 bytes
RTDL measured generic queue peak = 96 bytes
WL = not aligned
same_denominator_author_figure11 = false
figure11_reproduced = false
```

Why `48` vs `96`:

```text
author candidate WL Heavy Peak = 6 * 2 * sizeof(uint32_t) = 48 bytes
RTDL measured generic queue    = 6 * 2 * sizeof(uint64_t) = 96 bytes
```

This closes the row-count shape gap but keeps the byte denominator gap open.

### Goal5283 - Figure 11 Disposition

Disposition status:

```text
figure11_closed_denominator_not_aligned_after_native_mapping
```

Decision:

```text
offloading_size_shape_mapped = true
wl_heavy_peak_author_width_candidate_available = true
same_byte_denominator_author_figure11 = false
same_denominator_author_figure11 = false
figure11_reproduced = false
close_current_figure11_line = true
```

The artifact includes one shape-only candidate, explicitly not a Figure 11 row:

```text
paper_dataset_identity = false
figure11_row = false
same_denominator_author_figure11 = false
```

Reasons:

```text
1. It comes from a tiny generic native telemetry probe, not a Figure 11 paper input.
2. RTDL measured queue bytes use 64-bit id pairs; author WL Heavy Peak uses uint32 id pairs.
3. RTDL WL is attempted frontier hits, not author in_queue + miss_queue.
4. No author-vs-RTDL Figure 11 memory ratio has a same-denominator basis.
```

## What Must Not Be Claimed

The packet must not be read as claiming:

```text
Figure 11 reproduced
author memory parity
same-denominator author Figure 11 comparison
author-vs-RTDL memory ratio
full X-HD paper reproduction
performance improvement
native backend completion for all heavy/offload routes
using the shape-only Goal5282 candidate as a paper Figure 11 row
```

## Review Questions

1. Is `heavy_offload_worklist_numpy_columns` app-neutral in naming, schema,
   semantics, metadata, and tests?
2. Does Goal5279 correctly fail closed on overflow without emitting partial
   rows?
3. Does Goal5280's retry/backlog scheduler count as a real non-X-HD consumer,
   sufficient to prevent reading the worklist as an X-HD-only workaround?
4. Should the worklist helper remain public after Goals5279-5280, or should it
   be marked provisional until additional native consumers exist?
5. Does Goal5281 preserve ABI compatibility by keeping the v1 telemetry symbol
   while adding v2, and does the Python runtime correctly prefer v2 with v1
   fallback?
6. Is the Goal5281 POD evidence sufficient to prove native generic offload
   telemetry exists?
7. Are the v2 telemetry semantics correctly stated as generic RTDL semantics,
   especially `heavy_offload_queue_peak_bytes = rows * 2 * sizeof(uint64_t)`?
8. Does Goal5282 correctly map row-count shape into author-shaped
   `OffloadingSize` and a candidate author-width `WL Heavy Peak`, without
   claiming measured RTDL bytes equal author bytes?
9. Is the `48 bytes` author-width candidate vs `96 bytes` RTDL measured queue
   distinction correct and sufficiently prominent?
10. Does Goal5282 correctly keep `WL` not aligned because RTDL
    `in_queue_capacity` is attempted frontier hits rather than author
    `in_queue + miss_queue`?
11. Does Goal5283 correctly close the current Figure 11 line as
    denominator-not-aligned, rather than producing a fake memory ratio?
12. Is the shape-only candidate useful evidence while still correctly excluded
    from Figure 11 reproduction?
13. Is the stated "next if reopened" condition correct: a denominator-aligned
    generic native worklist, not another JSON mapping/reporting goal?
14. Are there any hidden app-specific semantics in `src/rtdsl` or `src/native`
    that would violate the RTDL generic-system principle?
15. Can Goals5279-5283 be marked externally reviewed and approved, or are
    amendments required?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-15:
Requested verdict label:
```

If approving, please use or adapt:

```text
approve_goals5279_5283_xhd_figure11_heavy_offload_packet__figure11_closed_denominator_not_aligned
```
