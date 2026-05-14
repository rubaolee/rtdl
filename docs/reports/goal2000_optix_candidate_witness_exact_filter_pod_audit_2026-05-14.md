# Goal2000 - OptiX Candidate Witness Exact-Filter Pod Audit

Status: pass-with-boundary

Date: 2026-05-14

## Scope

Goal2000 revalidated the segment/polygon v2.0 partner path on a fresh NVIDIA
pod after the CUDA/OptiX environment was repaired.

Pod:

- SSH: `root@69.30.85.251 -p 22085`
- GPU: `NVIDIA RTX A5000`
- Driver: `570.211.01`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA user space used for partner validation: `/usr/local/cuda-12.8`
- Native library: `/root/rtdl_goal2000/build/librtdl_optix.so`

## Findings

Two correctness problems were found and fixed before treating performance
numbers as evidence.

First, the bounded all-witness OptiX path consumes ray coordinate columns as
native `float`. The perf runner was building those columns as `float64`, which
made the native kernel read the wrong values. The runtime now rejects
all-witness ray columns whose `ox`, `oy`, `dx`, `dy`, or `tmax` dtypes are not
`float32`, and the perf runner now builds those columns as `float32`.

Second, `write_device_any_hit_all_witnesses` is a generic
ray/primitive-candidate witness contract, not an exact segment/polygon row
contract. The app adapter must filter candidate witnesses against the original
segment and triangle geometry before claiming exact app rows. The adapter now
does that exact filter explicitly and records:

- `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`
- `app_exact_filter: host_segment_triangle_filter_from_generic_witness_candidates`
- `native_exact_row_semantics_authorized: false`
- `app_exact_row_semantics_authorized: true`
- `whole_app_true_zero_copy_authorized: false`

This preserves the app-agnostic engine boundary. It also exposes the next real
v2.0 optimization target: move the exact candidate filter from host Python into
partner-side GPU code, likely CuPy RawKernel first, while keeping the native
engine generic.

## Pod Evidence

Artifacts:

- `docs/reports/goal2000_pod_smoke/goal1856_segment_polygon_count256_exact_filter.json`
- `docs/reports/goal2000_pod_smoke/goal1856_segment_polygon_count2048_exact_filter.json`
- `docs/reports/goal2000_pod_smoke/goal1856_segment_polygon_count8192_cupy_exact_filter.json`

All three artifacts were regenerated after the JSON claim boundary added
`whole_app_true_zero_copy_authorized: false`. They preserve strict row parity:

- count 256: `strict_rows_match: true`, CuPy and Torch
- count 2048: `strict_rows_match: true`, CuPy and Torch
- count 8192: `strict_rows_match: true`, CuPy

The timing picture is scale-sensitive:

| count | partner | v1.8 median (s) | v2.0 median (s) | ratio |
| ---: | --- | ---: | ---: | ---: |
| 256 | CuPy | `0.0014603622257709503` | `0.008382847532629967` | `5.740252236532972x` |
| 256 | Torch | `0.0014603622257709503` | `0.008379112929105759` | `5.737694923382643x` |
| 2048 | CuPy | `0.025320738554000854` | `0.047347038984298706` | `1.8698917049091186x` |
| 2048 | Torch | `0.025320738554000854` | `0.05182529240846634` | `2.046752795063222x` |
| 8192 | CuPy | `0.3172904010862112` | `0.11018174886703491` | `0.3472583743152613x` |

The count-8192 CuPy row is useful positive evidence for the segment/polygon
path at larger scale. The count-256 and count-2048 rows are negative evidence:
the host exact filter and bounded witness management dominate enough that v2.0
is slower than warmed v1.8. Therefore this goal does not authorize a positive
whole-app performance claim. It narrows the next required optimization.

## Boundary

Accepted:

- the A5000 pod can build and run the OptiX library with CUDA 12.8 partner
  stacks;
- the segment/polygon v2.0 partner path now fails closed on incorrect float64
  ray-column inputs;
- generic native candidate witnesses are no longer overclaimed as exact app
  rows;
- same-contract strict-row parity holds for the collected pod artifacts.

Still blocked:

- v2.0 release authorization;
- broad RT-core speedup wording;
- whole-app acceleration wording;
- true whole-app zero-copy wording for exact segment/polygon rows;
- positive segment/polygon performance wording at small/intermediate scale;
- final all-app v2.0 versus v1.8 performance comparison.

## Next Work

The design problem is now precise. RTDL native should keep emitting generic
candidate witness tables. The v2.0 partner layer needs reusable partner-side
exact-filter and reduction mechanisms so app-specific filtering does not fall
back to host Python. For this lane, the next implementation target is a CuPy
RawKernel exact segment/triangle candidate filter that consumes the native
witness columns, ray columns, and triangle columns on device and emits exact
rows or counts without host materialization.
