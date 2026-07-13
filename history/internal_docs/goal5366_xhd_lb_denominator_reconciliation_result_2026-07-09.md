# Goal5366 - X-HD lb / Heavy-Offload Denominator Reconciliation

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5365 proved a useful behavior gate for the temporary Level-B
Dragon -> AsianDragon input:

```text
lb0 / disabled-offload counterpart:
  author HDResult ~= RTDL HDResult
  RTDL heavy_offload_peak_rows = 0

lb256 / heavy-offload counterpart:
  author HDResult ~= RTDL HDResult
  RTDL heavy_offload_peak_rows > 0
```

However, Goal5365 also showed a denominator gap:

```text
author lb256 OffloadingSize = 27,133,990
RTDL lb256 heavy_offload_peak_rows = 24,508,120

author WL Heavy Peak = 217,071,920 bytes
RTDL author-width candidate bytes = 196,064,960 bytes
```

Goal5366 reconciles what these counters mean before accepting explicit `-lb`
support or making Figure 7 / Figure 11 claims.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5366_lb_denominator_reconciliation.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5366_lb_denominator_reconciliation.json
tests/goal5366_lb_denominator_reconciliation_test.py
```

## Result

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5366_lb_denominator_reconciliation.json
```

Status:

```text
lb_denominator_reconciliation_ready__row_count_parity_not_established
```

Exit label:

```text
lb_denominator_reconciled_shape_aligned__row_count_parity_not_established
```

## Key Findings

### 1. Byte Formula Is Shape-Aligned

Author:

```text
OffloadingSize * 2 * sizeof(uint32_t)
27,133,990 * 8 = 217,071,920 bytes
```

RTDL author-width candidate:

```text
heavy_offload_peak_rows * 2 * sizeof(uint32_t)
24,508,120 * 8 = 196,064,960 bytes
```

So the byte denominator formula is compatible under an author-width `uint32`
view.

### 2. Row Count Parity Is Not Established

Observed delta:

```text
author rows - RTDL rows = 2,625,870
RTDL / author row ratio = 0.9032258064516129
```

This prevents same-denominator memory parity and prevents Figure 11 claims.

### 3. The Current Mismatch Is Not Explained By RTDL Duplicate Collapse

The RTDL native path sorts and uniquifies frontier rows, but in the Goal5365
artifact:

```text
raw_attempted_count = 24,508,120
emitted_count_after_native_sort_unique = 24,508,120
heavy_offload_peak_rows = 24,508,120
```

Thus the observed 2.63M-row delta is not explained by a raw-vs-unique collapse
inside the existing RTDL artifact.

### 4. Route Regime Is Still Not Author-Iteration Aligned

Author `OffloadingSize` is an iteration field:

```text
iteration_3 Radius = 79.2156982421875
NumInputPoints = 437,645
OffloadingSize = 27,133,990
```

RTDL Goal5365 is a single-pass full-cover cell-MBR frontier route:

```text
radius = 266.9466183641096
initial_state = none
frontier_inline_nearest = true
```

Therefore the current RTDL counter is a generic heavy frontier counter, not an
author-iteration offload queue denominator.

## Source Evidence

Author source evidence:

```text
src/rt/shaders/shaders_nn_uniform_grid.cu
  offloading_point_ids.Append(in_q_idx)
  offloading_cell_ids[tail] = mbr_id

src/hd_impl/hausdorff_distance_rt.h
  auto offloading_size = offloading_point_ids_.size(stream);
  wl_heavy_peak_bytes = max(offloading_size * 2 * sizeof(uint32_t))
  total_offloading_size += offloading_size;
  json_iter["OffloadingSize"] = total_offloading_size;
  loadBalanceProcessing sorts / reduces rows by point after the queue count
```

RTDL source evidence:

```text
src/native/optix/rtdl_optix_workloads.cpp
  cell.point_count > params.max_inline_points
  frontier_kind_code == 2
  RtdlCellMbrFrontierRow sort / unique
  offload_row_count * 2 * sizeof(uint64_t)
```

## Validation

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5366_lb_denominator_reconciliation.py
py -m unittest tests.goal5366_lb_denominator_reconciliation_test tests.goal5365_rtdl_lb_counterpart_gate_test tests.goal5364_lb_trace_gate_author_pair_contract_test tests.goal5363_lb_heavy_offload_semantics_audit_test
Ran 13 tests OK
```

The local `py` invocation prints:

```text
Could not find platform independent libraries <prefix>
```

This is known noisy Windows Python output; tests passed.

## Decision

```text
explicit_lb_support_authorized_now = false
row_count_or_byte_parity_authorized_now = false
```

Goal5366 proves:

```text
1. The byte formula shape is compatible.
2. Goal5365 behavior evidence remains valid.
3. Row-count / byte parity is still not established.
4. The current RTDL route is not author-iteration denominator aligned.
```

## Claim Boundary

Not authorized:

```text
explicit -lb support
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core algorithm parity
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Next Gate

```text
author_iteration_aligned_lb_trace_or_raw_author_denominator_telemetry
```

Concretely, the next implementation should do one of:

```text
1. Build an author-iteration-aligned RTDL lb trace:
   - same radius;
   - same input queue / iteration scope;
   - same lb threshold;
   - comparable raw offload rows.

2. Add raw author-denominator telemetry to the generic native collector:
   - raw offload row count before any sort / unique / packing;
   - author-width byte view;
   - keep generic names and no X-HD core identity.
```

Only after that can we decide whether explicit `-lb` support is narrow-safe or
whether it remains behavior-level only.
