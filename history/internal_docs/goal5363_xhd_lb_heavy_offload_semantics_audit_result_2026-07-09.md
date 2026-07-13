# Goal5363 - X-HD lb / Heavy-Cell Offload Semantics Audit

Status: `implemented_review_pending`

Date: 2026-07-09

## Purpose

Goal5363 audits the author X-HD `-lb` option and heavy-cell offload semantics
before RTDL accepts any explicit `-lb` flag.

This is a semantics / denominator audit, not a performance goal.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5363_lb_heavy_offload_semantics_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5363_lb_heavy_offload_semantics_audit.json
tests/goal5363_lb_heavy_offload_semantics_audit_test.py
```

## Author Semantics Identified

The author source was read from:

```text
C:\Users\Lestat\AppData\Local\Temp\xhd-author-src
```

Goal5363 pins these author facts:

```text
FLAGS_lb -> config.lb -> processing_threshold

lb = 0:
  processing_threshold is rewritten to UINT32_MAX
  heavy-cell offload is effectively disabled

lb = N:
  a cell is offloaded when point_count > N

offload row shape:
  (in_queue index, cell id)

offload stage:
  RT shader appends offload rows
  CUDA loadBalanceProcessing sorts/reduces by point and processes offloaded cells
```

Author iteration / memory fields involved:

```text
RTTime
CUDATime
OffloadingSize
WL = 2 * n_points_a * sizeof(uint32_t)
WL Heavy Peak = max(OffloadingSize * 2 * sizeof(uint32_t))
```

## RTDL Assets Already Present

Goal5363 confirms prior RTDL assets:

```text
generic heavy_offload_worklist shape exists
native heavy-offload telemetry exists
bounded author-shaped OffloadingSize mapping exists
nearest frontier threshold rule exists:
  cell_point_count > max_inline_points
```

This threshold rule is shape-aligned with author:

```text
author: cell_point_count > lb
RTDL:   cell_point_count > max_inline_points
```

But this is only a candidate mapping.  It is not yet explicit author `-lb`
support.

## Decision

Goal5363 result:

```text
status = lb_heavy_offload_semantics_audit_ready__lb_option_still_unsupported
matched = true
lb_option_supported_now = false
```

Reason:

```text
RTDL has generic offload shape and telemetry, and the threshold-rule shape
aligns with author lb.  But explicit -lb changes author RT execution and
author fields.  No bounded author lb=0/lb=N route trace gate has proven
behavior, and Figure 7 / Figure 11 denominators remain non-aligned.
```

## Next Gate

The next real implementation gate should be:

```text
bounded_lb_processing_threshold_route_trace_gate
```

Minimum requirements:

```text
1. Run or reconstruct an author trace with lb=0 and a matching lb=N trace on
   the same bounded input.
2. Show lb=0 disables heavy offload and lb=N creates OffloadingSize rows when
   heavy cells exist.
3. Map author processing_threshold to a generic RTDL threshold only when the
   RTDL route emits equivalent offload row semantics.
4. Report RTTime, CUDATime, OffloadingSize, WL, and WL Heavy Peak with explicit
   denominator status.
5. Keep unsupported author RT options fail-closed; do not claim Figure 7/11 or
   performance parity.
```

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5363_lb_heavy_offload_semantics_audit.py
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5363_lb_heavy_offload_semantics_audit.json
py -m unittest tests.goal5363_lb_heavy_offload_semantics_audit_test tests.goal5362_tune_radius_option_surface_gate_test tests.goal5352_xhd_rt_core_feature_parity_matrix_test tests.goal5353_xhd_author_rt_option_surface_gate_test tests.goal5282_xhd_offload_author_mapping_test tests.goal5292_xhd_figure7_load_balance_audit_test
```

Result:

```text
Ran 23 tests OK
```

The local Python runtime printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
RTDL has a shape-aligned generic offload threshold candidate for author lb.
The author lb / heavy-cell offload semantics have been pinned from source.
Goal5363 identifies the next bounded trace gate needed before accepting -lb.
```

Not authorized:

```text
explicit -lb support
author RT option-surface completion
author RT-core algorithm parity
Figure 7 reproduction
Figure 11 reproduction
same-denominator memory claim
performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Exit Label

```text
lb_heavy_offload_semantics_audit_ready__next_gate_bounded_lb_trace
```
