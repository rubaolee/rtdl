# V4 Section 8 Route D Hand-Written OptiX Ceiling Report

Date: 2026-06-24
Status: evidence report; not a release authorization

## Verdict

Route D was obtained: an independent hand-written OptiX reference binary now
builds and runs on the RTX pod for the fixed-radius count-threshold contract.

The result **does not** authorize "near hand-written OptiX" wording for the
current RTDL product path. It shows the opposite: the RT-core kernel itself can
run in milliseconds, while the current RTDL Python-facing prepared routes are
hundreds of times slower at the same sizes. V4's next blocker is the product
boundary: Python point objects, packing, FFI/result conversion, and app-level
summary materialization.

## Files

- Protocol: `future/v4/rtdl_v4_0_section8_route_d_handwritten_optix_protocol_2026-06-24.md`
- Reference source: `future/v4/reference/route_d_fixed_radius_count_threshold_optix.cpp`
- Harness: `scripts/v4_section8_route_d_reference_validation.py`
- Route D evidence: `future/v4/evidence/v4_section8_route_d_result_2026-06-24.json`
- Direct RTDL scalar evidence: `future/v4/evidence/v4_section8_rtdl_direct_prepared_scalar_hot_path_result_2026-06-24.json`
- Prior prepared summary evidence: `future/v4/evidence/v4_section8_prepared_hot_path_result_2026-06-24.json`

## Independence

The Route D reference is a standalone CUDA Driver + OptiX program:

- no `import rtdsl`
- no link to `librtdl_optix.so`
- no call to `rtdl_optix_*`
- no RTDL Python app route
- own OptiX context, GAS, pipeline, SBT, launch params, and device program
- same generated outlier fixture as the Section 8 test

Local source tests enforce that the reference source does not contain those
forbidden RTDL runtime tokens.

## Correctness

All serious sizes passed:

| copies | points | expected threshold reached | expected outliers | Route D correctness |
|---:|---:|---:|---:|:---:|
| 8,192 | 65,536 | 49,152 | 16,384 | pass |
| 32,768 | 262,144 | 196,608 | 65,536 | pass |
| 131,072 | 1,048,576 | 786,432 | 262,144 | pass |

## Timing Summary

Prepared-session hot-path boundary:

- included: host query upload, launch params upload, OptiX launch,
  synchronization, required result download
- excluded: fixture construction, OptiX context creation, module/pipeline build,
  search-point upload, and GAS build

| copies | points | Route D scalar median | RTDL direct prepared scalar median | RTDL / Route D scalar | Route D count-row median | RTDL prepared summary median | RTDL summary / Route D rows |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8,192 | 65,536 | 0.000522s | 0.100487s | 192.64x | 0.000629s | 0.284516s | 452.35x |
| 32,768 | 262,144 | 0.000716s | 0.486885s | 680.25x | 0.001542s | 1.193533s | 774.10x |
| 131,072 | 1,048,576 | 0.002090s | 1.989423s | 951.89x | 0.004641s | 5.290915s | 1140.11x |

Route D still allocates and frees per-call device buffers for query data, launch
params, and outputs inside the measured window. That makes this ceiling
slightly conservative rather than artificially inflated; a pooled/preallocated
hand-written implementation would be faster. The product-boundary gap above is
therefore a lower bound.

At the largest fixture, each scalar Route D repeat uploads roughly 16.7 MB of
query point data. The 2.09 ms scalar median is partly PCIe-upload-bound, not
pure RT-core traversal time. A V4 array/device-array front door that keeps query
columns resident can reduce this cost in addition to removing Python object
packing.

## Interpretation

The Tier-2 fused kernel idea remains technically valid: the independent
hand-written OptiX ceiling is extremely fast and correctness holds.

The current V4 product path is not near that ceiling. The dominant gap is no
longer "can RT cores perform this fused primitive?" It is:

- Python `Point` object boundary
- repeated host packing into native point buffers
- Python/ctypes call overhead
- result row materialization/conversion for summary mode
- lack of a productized array/device-array front door for this primitive

This is exactly the V4 reframing: RTDL must become a Python GPU ecosystem RT-core
operator that accepts array-like/device-array inputs and returns compact results
without forcing per-point Python object conversion on the hot path.

## Authorized Claim

After external review, the only claim this report can support is:

> An independent hand-written OptiX reference for the fixed-radius
> count-threshold contract runs correctly on the measured Section 8 fixture and
> establishes a native ceiling far faster than the current RTDL Python-facing
> prepared routes.

## Unauthorized Claims

This report does not authorize:

- V4 release
- broad V4 speedup wording
- "RTDL is near hand-written OptiX" wording
- Tier-3 callback claims
- app-specific native engine claims
- whole-call app-route claims

## Next Engineering Target

Do not add a second primitive yet. First close the product-boundary gap for this
primitive:

1. Add a V4 fixed-radius count-threshold array front door that accepts contiguous
   numeric columns or supported GPU-array columns instead of Python `Point`
   objects.
2. Reuse the existing prepared native scene and count-threshold continuation.
3. Return scalar and compact row outputs without app-level Python density-row
   conversion in the hot path.
4. Measure against both baselines:
   - separated RTDL row route
   - Route D independent hand-written OptiX ceiling
5. Only if the new product route moves materially toward Route D should the V4
   Tier-2 primitive library continue to the next primitive.

This is a Go/No-Go gate for V4 performance-release work.
