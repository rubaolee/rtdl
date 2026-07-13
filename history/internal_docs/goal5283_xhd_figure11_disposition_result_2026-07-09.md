# Goal5283 - X-HD Figure 11 Disposition After Native Offload Mapping

Status: `implemented_review_pending`

Date: 2026-07-09

## Purpose

Goal5283 consolidates the Figure 11 memory line after:

- Goal5272 extracted the author Figure 11 memory matrix,
- Goal5273-5277 defined RTDL memory accounting and denominator mismatch,
- Goal5279-5280 added a generic heavy/offload worklist reference and non-X-HD
  consumer,
- Goal5281 added native v2 offload telemetry,
- Goal5282 mapped generic offload telemetry to author-shaped fields.

The purpose is to decide whether the current RTDL route is now sufficient for a
Figure 11 reproduction claim.

## Result

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5283_figure11_disposition_2026-07-09.json
```

Status:

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

## What Is Now Known

Goal5282 established a useful shape mapping:

```text
native offload rows = 6
author-shaped OffloadingSize = 6
author-width WL Heavy Peak candidate = 48 bytes
RTDL measured generic queue peak = 96 bytes
```

This proves the row-count shape is usable, but it also proves the byte
denominator remains different:

```text
Author WL Heavy Peak = OffloadingSize * 2 * sizeof(uint32_t)
RTDL measured queue  = offload_rows   * 2 * sizeof(uint64_t)
```

RTDL `WL` also remains different:

```text
Author WL = in_queue + miss_queue over source points.
RTDL v2 in_queue_capacity = attempted generic frontier hits.
```

## Shape-Only Candidate

The disposition artifact includes one shape-only candidate:

```text
label = Goal5282 shape-only offload candidate
paper_dataset_identity = false
figure11_row = false
same_denominator_author_figure11 = false
```

Reasons it is not a Figure 11 row:

```text
1. The source is a generic tiny native telemetry probe, not a Figure 11 paper input.
2. RTDL measured queue bytes use 64-bit id pairs; author WL Heavy Peak uses uint32 id pairs.
3. RTDL WL remains unaligned because native in_queue_capacity is attempted frontier hits.
4. No author-vs-RTDL Figure 11 memory ratio has a same-denominator basis.
```

## Validation

Focused tests:

```text
py -m unittest \
  tests.goal5283_xhd_figure11_disposition_test \
  tests.goal5282_xhd_offload_author_mapping_test \
  tests.goal5281_native_heavy_offload_telemetry_artifact_test \
  tests.goal5277_xhd_memory_denominator_alignment_decision_test \
  tests.goal5276_xhd_rtdl_bounded_memory_matrix_test \
  tests.goal5272_xhd_figure11_author_memory_log_matrix_test

Ran 17 tests OK
```

## Claim Boundary

Allowed:

```text
The current RTDL route has a shape-only author offload mapping, but Figure 11
is closed as not reproduced under the current denominator.
```

Not authorized:

```text
Figure 11 reproduced
author memory parity
same-denominator author Figure 11 comparison
memory ratio
full X-HD paper reproduction
using the shape-only candidate as a paper Figure 11 row
```

## Next If Reopened

To reopen Figure 11, RTDL needs a new denominator-aligned generic native
worklist, not more JSON reshaping:

```text
1. author-compatible queue id width, or reviewed conversion to author width;
2. an author-like in_queue + miss_queue denominator;
3. heavy-offload peak telemetry measured in that same denominator;
4. exact or externally accepted Figure 11 input provenance.
```

Until then, Figure 11 remains:

```text
not_reproduced__denominator_not_aligned
```
