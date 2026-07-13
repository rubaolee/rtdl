# Goal5281 - Native Heavy/Offload Telemetry ABI Spike

Status: `implemented_review_pending`

Date: 2026-07-09

## Purpose

Goal5279 and Goal5280 created a generic CPU/NumPy heavy/offload worklist
schema plus a non-X-HD consumer. Goal5281 moves the next required piece into the
native OptiX runtime: a status-bearing telemetry ABI that exposes heavy/offload
frontier row peak counts and bytes from a generic native route.

This goal does **not** reproduce X-HD Figure 11. It only proves that RTDL native
code can report generic offload-queue-shaped telemetry instead of relying only
on CPU reference estimates.

## Implementation

Native OptiX:

- Added a v2 telemetry symbol:

```text
rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v2
```

- Kept the existing v1 symbol unchanged for compatibility:

```text
rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry
```

- Added generic heavy/offload fields:

```text
in_queue_capacity
miss_queue_capacity
heavy_offload_row_capacity
heavy_offload_current_rows
heavy_offload_peak_rows
heavy_offload_queue_current_bytes
heavy_offload_queue_peak_bytes
```

- Current native semantics:
  - `in_queue_capacity` is the attempted raw frontier hit count.
  - `miss_queue_capacity` is `0` for the current generic cell-MBR route.
  - `heavy_offload_*rows` counts rows whose `frontier_kind_code == offload`.
  - queue bytes use the same two-id shape as Goal5279:

```text
heavy_offload_queue_bytes = offload_row_count * 2 * sizeof(uint64_t)
```

Python runtime:

- `src/rtdsl/optix_runtime.py` now prefers the v2 telemetry symbol when present
  and falls back to v1 when only v1 is available.
- v2 telemetry reports schema:

```text
rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v2
```

## POD Evidence

POD:

```text
213.173.108.24:13502
GPU: NVIDIA RTX 4000 Ada Generation
```

Wrapper preflight:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Focused POD tests:

```text
python -m unittest \
  tests.goal5281_native_heavy_offload_telemetry_contract_test \
  tests.goal5275_xhd_native_memory_telemetry_contract_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test \
  tests.goal5279_generic_heavy_offload_worklist_test

Ran 15 tests OK
```

Native build:

```text
make build-optix -j2
```

Exported symbols:

```text
00000000000c5260 T rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry
00000000000c5430 T rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v2
```

Runtime telemetry artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
```

Tiny 3-D generic cell-MBR probe:

```text
row_count = 6
attempted_count = 6
frontier_kind_codes = [2, 2, 2, 2, 2, 2]
offload_row_count_from_rows = 6
native_memory_telemetry_collected = true
telemetry schema = rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v2
heavy_offload_peak_rows = 6
heavy_offload_queue_peak_bytes = 96
matched = true
```

The byte count matches the generic two-id queue shape:

```text
6 rows * 2 ids * 8 bytes = 96 bytes
```

## Local Validation

Local structural and artifact tests:

```text
py -m unittest \
  tests.goal5281_native_heavy_offload_telemetry_contract_test \
  tests.goal5281_native_heavy_offload_telemetry_artifact_test \
  tests.goal5275_xhd_native_memory_telemetry_contract_test \
  tests.goal5275_xhd_native_memory_telemetry_artifact_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test \
  tests.goal5279_generic_heavy_offload_worklist_test
```

Additional validation:

```text
py -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/partner_continuations.py src/rtdsl/__init__.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
git diff --check
```

## Claim Boundary

Allowed claim:

```text
RTDL native OptiX can now expose v2 generic cell-MBR offload-frontier telemetry
with peak offload rows and queue bytes on POD.
```

Not authorized:

```text
X-HD Figure 11 reproduced
author memory parity
same-denominator author Figure 11 comparison
performance improvement
native backend completion for all heavy/offload routes
claiming current RTDL offload rows are identical to author WL Heavy Peak
```

## Interpretation

Goal5281 closes the immediate "native telemetry missing" gap from Goal5280. The
new evidence is still one level below Figure 11: it proves that native RTDL can
report a generic heavy/offload queue shape, but it does not yet prove that this
shape maps cleanly to the author's `WL` and `WL Heavy Peak` denominator.

## Next Recommended Goal

Goal5282 should perform the X-HD bounded mapping from this generic v2 telemetry
to the author memory fields:

```text
author WL
author WL Heavy Peak
author OffloadingSize
```

Exit labels:

```text
xhd_bounded_mapping_to_author_offload_fields_ready
xhd_figure11_denominator_still_not_aligned_after_native_telemetry
```
