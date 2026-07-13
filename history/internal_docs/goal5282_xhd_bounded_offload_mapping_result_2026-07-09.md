# Goal5282 - X-HD Bounded Offload Mapping From Generic Telemetry

Status: `implemented_review_pending`

Date: 2026-07-09

## Purpose

Goal5281 proved that the generic native OptiX cell-MBR frontier route can expose
v2 telemetry for offload frontier rows:

```text
heavy_offload_peak_rows
heavy_offload_queue_peak_bytes
```

Goal5282 maps that generic telemetry into X-HD author-shaped fields:

```text
OffloadingSize
WL
WL Heavy Peak
```

The goal is a bounded mapping/denominator decision, not Figure 11 reproduction.

## Implementation

App-owned helper changes:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
```

New helper:

```python
author_offload_mapping_from_native_telemetry(native_memory)
```

New artifact builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_offload_mapping.py
```

Input artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5282_author_offload_mapping_2026-07-09.json
```

## Result

The bounded mapping result is:

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

Why 48 vs 96:

```text
Author formula:
  WL Heavy Peak = OffloadingSize * 2 * sizeof(uint32_t)
                = 6 * 2 * 4
                = 48 bytes

RTDL current generic telemetry:
  heavy_offload_queue_peak_bytes = offload_rows * 2 * sizeof(uint64_t)
                                 = 6 * 2 * 8
                                 = 96 bytes
```

## Decision

Goal5282 closes one gap:

```text
The offload row-count shape is now mappable to author OffloadingSize.
```

But Figure 11 is still not reproduced:

```text
RTDL measured queue bytes use 64-bit id pairs, while author Figure 11 uses
uint32 id pairs.

RTDL native v2 in_queue_capacity is attempted frontier hits, not the author's
in_queue + miss_queue over source points.

Therefore same_denominator_author_figure11 remains false.
```

## Validation

Focused tests:

```text
py -m unittest \
  tests.goal5282_xhd_offload_author_mapping_test \
  tests.goal5281_native_heavy_offload_telemetry_artifact_test \
  tests.goal5281_native_heavy_offload_telemetry_contract_test \
  tests.goal5277_xhd_memory_denominator_alignment_decision_test \
  tests.goal5273_xhd_rtdl_memory_accounting_test

Ran 15 tests OK
```

## Claim Boundary

Allowed:

```text
Goal5282 maps generic native v2 offload row telemetry to author-shaped
OffloadingSize and author-width WL Heavy Peak candidate bytes.
```

Not authorized:

```text
Figure 11 reproduced
author memory parity
same-denominator author Figure 11 comparison
memory ratio
performance claim
claiming RTDL measured queue bytes equal author WL Heavy Peak bytes
claiming RTDL WL equals author in_queue + miss_queue
```

## Next Recommended Goal

Goal5283 should decide whether to:

```text
1. build a Figure 11 candidate row with explicit "shape-only / byte-denominator
   not aligned" status, or
2. close Figure 11 under current RTDL as not_reproduced because same
   denominator is still not aligned.
```

Recommended exit labels:

```text
figure11_candidate_row_shape_only_not_same_denominator
figure11_closed_denominator_not_aligned_after_native_mapping
```
