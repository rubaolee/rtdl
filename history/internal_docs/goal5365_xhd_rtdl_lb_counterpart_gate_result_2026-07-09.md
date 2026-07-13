# Goal5365 - X-HD RTDL lb0/lb256 Counterpart Gate

Status: `implemented_review_pending`

Date: 2026-07-09

## Purpose

Goal5365 runs RTDL same-input counterparts for the Goal5364 author `lb=0` /
`lb=256` pair.

This is a behavior-level gate:

```text
lb0:   value match + zero offload
lb256: value match + positive offload
```

It is not row-count parity, byte-denominator parity, Figure 7 reproduction, or
explicit `-lb` support.

## POD / Build

POD preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight

POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Because the POD did not contain the current RTDL repo, a minimal package was
uploaded:

```text
src/
Makefile
pyproject.toml
requirements.txt
Paper-reproduction-apps/x-hd-paper/scripts/
```

Remote workspace:

```text
/tmp/rtdl_goal5364
```

Remote native build:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda
```

The built library loaded successfully through `rtdsl.optix_runtime`.

## Inputs

Same Level-B temporary-input pair as Goal5296:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
```

Important preprocessing:

```text
--translate-each-input-to-min-bound
```

Without this translation, the RTDL route produced `3.002748588731897` and did
not match the author raw diagnostic.  With translation, RTDL produced
`52.453491321261296`, matching author within the chosen behavior-gate tolerance.

## Author Contract

From Goal5364:

```text
author lb0 HDResult  = 52.453487396240234
author lb256 HDResult = 52.453487396240234
```

Author offload contrast:

```text
lb0:
  LargeCells = 0
  OffloadingSize = 0
  WL Heavy Peak = 0

lb256:
  LargeCells = 5060
  OffloadingSize = 27,133,990
  WL Heavy Peak = 217,071,920 bytes
```

## RTDL Runs

### RTDL disabled-offload counterpart

Command shape:

```text
run_xhd_cell_mbr_frontier_route_gate.py \
  --input1 /tmp/xhd_goal5234/data/dragon.ply \
  --input2 /tmp/xhd_goal5234/data/asian_dragon.ply \
  --n-dims 3 --input-type ply \
  --translate-each-input-to-min-bound \
  --backend optix --grid-shape 96,60,72 \
  --max-inline-points 4294967295 \
  --initial-state none \
  --grid-cell-builder native_cuda \
  --frontier-inline-nearest \
  --direction-mode directed-a-to-b \
  --validation-mode none \
  --collect-frontier-native-phase-timings
```

Result:

```text
RTDL HDResult = 52.453491321261296
abs diff vs author = 3.925021061945699e-06
heavy_offload_peak_rows = 0
heavy_offload_queue_peak_bytes = 0
rtdl_route_sec = 1.657000720500946
```

### RTDL `max_inline_points=256` counterpart

Command shape:

```text
run_xhd_cell_mbr_frontier_route_gate.py \
  --input1 /tmp/xhd_goal5234/data/dragon.ply \
  --input2 /tmp/xhd_goal5234/data/asian_dragon.ply \
  --n-dims 3 --input-type ply \
  --translate-each-input-to-min-bound \
  --backend optix --grid-shape 96,60,72 \
  --max-inline-points 256 \
  --initial-state none \
  --grid-cell-builder native_cuda \
  --frontier-inline-nearest \
  --direction-mode directed-a-to-b \
  --validation-mode none \
  --collect-frontier-native-phase-timings
```

Result:

```text
RTDL HDResult = 52.453491321261296
abs diff vs author = 3.925021061945699e-06
heavy_offload_peak_rows = 24,508,120
heavy_offload_queue_peak_bytes generic uint64 = 392,129,920
author-width uint32-equivalent candidate = 196,064,960
rtdl_route_sec = 38.40844701975584
nearest_continuation_sec = 21.47888918966055
```

## Comparison

Goal5365 output:

```text
status = rtdl_lb0_lb256_counterpart_behavior_gate_passed__row_count_denominator_not_parity
matched = true
tolerance = 5e-06
```

Behavior checks:

```text
input_match = true
preprocessing_match = true
value_match = true
lb0_behavior_zero_offload = true
lb256_behavior_positive_offload = true
```

Non-parity facts:

```text
author lb256 OffloadingSize = 27,133,990
RTDL lb256 heavy_offload_peak_rows = 24,508,120

author lb256 WL Heavy Peak bytes = 217,071,920
RTDL lb256 author-width candidate bytes = 196,064,960
```

Therefore:

```text
row_count_or_byte_parity_claimed = false
performance_ratio_claimed = false
explicit_lb_support_authorized_now = false
```

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5365_rtdl_lb_counterpart_gate.py
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5365_rtdl_lb_counterpart_gate.json
py -m unittest tests.goal5365_rtdl_lb_counterpart_gate_test tests.goal5364_lb_trace_gate_author_pair_contract_test tests.goal5363_lb_heavy_offload_semantics_audit_test tests.goal5362_tune_radius_option_surface_gate_test tests.goal5353_xhd_author_rt_option_surface_gate_test tests.goal5296_xhd_level_b_lb_diagnostic_test tests.goal5292_xhd_figure7_load_balance_audit_test
```

Result:

```text
Ran 24 tests OK
```

The local Python runtime printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
On the Level-B Dragon->Asian diagnostic pair, RTDL matches author HDResult
within 5e-6 for disabled-offload and max_inline_points=256 counterparts.
RTDL also reproduces the qualitative offload switch:
  disabled-offload -> zero heavy offload rows
  max_inline_points=256 -> positive heavy offload rows
```

Not authorized:

```text
explicit -lb support
author RT-core algorithm parity
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Exit Label

```text
rtdl_lb_counterpart_behavior_gate_passed__decide_narrow_lb_mapping_or_tighten
```
