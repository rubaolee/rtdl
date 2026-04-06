# Goal 118 Segment/Polygon Linux Large-Scale Performance

Date: 2026-04-06  
Status: accepted

## Summary

Goal 118 finishes the clean Linux large-scale performance report for
`segment_polygon_hitcount`.

The final result is:

- large deterministic PostGIS parity is clean through `x1024`
- OptiX is the best current RTDL backend on the audited large rows
- Embree tracks the native CPU oracle closely on this family
- Vulkan is parity-clean on the audited rows, but the current public runtime
  path for this family still follows the accepted correctness-first fallback
  boundary rather than a native optimized traversal path

So this goal gives the feature one reproducible Linux performance package with
real large-data numbers, real PostGIS checks, and a direct backend-by-backend
reading of what is strong today and what is still incomplete.

## Clean Linux Execution

Executed on:

- host: `lx1`
- platform: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Python: `3.12.3`
- machine: `x86_64`
- versions:
  - oracle: `(0, 1, 0)`
  - Embree: `(4, 3, 0)`
  - OptiX: `(9, 0, 0)`
  - Vulkan: `(0, 1, 0)`

Scripted run:

```bash
cd /home/lestat/work/rtdl_goal118_clean
PYTHONPATH=src:. python3 scripts/goal118_segment_polygon_linux_large_perf.py \
  --db-name rtdl_postgis \
  --perf-iterations 3 \
  --output-dir build/goal118
```

Clean-host regression pass:

```bash
cd /home/lestat/work/rtdl_goal118_clean
PYTHONPATH=src:. python3 -m unittest \
  tests.goal110_segment_polygon_hitcount_closure_test \
  tests.goal112_segment_polygon_perf_test \
  tests.goal114_segment_polygon_postgis_test \
  tests.goal116_segment_polygon_backend_audit_test \
  tests.goal118_segment_polygon_linux_large_perf_test \
  tests.rtdsl_vulkan_test
```

Accepted result:

- `32` tests
- `OK`

## Large PostGIS-Backed Results

### `x64`

- dataset:
  - `derived/br_county_subset_segment_polygon_tiled_x64`
- scale:
  - `640` segments
  - `128` polygons
- PostGIS:
  - `0.008486 s`
  - SHA256 `bdfe3c868dbae0278436b1451dd5760564f57359096986e0bf95951dc57f507b`
- parity:
  - `cpu`: true
  - `embree`: true
  - `optix`: true
  - `vulkan`: true
- timings:
  - `cpu`: `0.047770 s`
  - `embree`: `0.047068 s`
  - `optix`: `0.029512 s`
  - `vulkan`: `0.037252 s`

### `x256`

- dataset:
  - `derived/br_county_subset_segment_polygon_tiled_x256`
- scale:
  - `2560` segments
  - `512` polygons
- PostGIS:
  - `0.050030 s`
  - SHA256 `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099`
- parity:
  - `cpu`: true
  - `embree`: true
  - `optix`: true
  - `vulkan`: true
- timings:
  - `cpu`: `0.573057 s`
  - `embree`: `0.578506 s`
  - `optix`: `0.382547 s`
  - `vulkan`: `0.571698 s`

### `x512`

- dataset:
  - `derived/br_county_subset_segment_polygon_tiled_x512`
- scale:
  - `5120` segments
  - `1024` polygons
- PostGIS:
  - `0.098951 s`
  - SHA256 `02af7f915d6d5ca84af5919a67dbc9422f57e56b0445120484a548d20df899d0`
- parity:
  - `cpu`: true
  - `embree`: true
  - `optix`: true
  - `vulkan`: true
- timings:
  - `cpu`: `2.277086 s`
  - `embree`: `2.308199 s`
  - `optix`: `1.510382 s`
  - `vulkan`: `2.275099 s`

### `x1024`

- dataset:
  - `derived/br_county_subset_segment_polygon_tiled_x1024`
- scale:
  - `10240` segments
  - `2048` polygons
- PostGIS:
  - `0.310521 s`
  - SHA256 `4eccacb646271fce71617c45fc61f9688cbd2b8687be5db21106e98be5a7d741`
- parity:
  - `cpu`: true
  - `embree`: true
  - `optix`: true
  - `vulkan`: true
- timings:
  - `cpu`: `9.034734 s`
  - `embree`: `9.173001 s`
  - `optix`: `6.001617 s`
  - `vulkan`: `9.049110 s`

## Current And Prepared Timing View

Current-run means from the clean Linux timing loop:

| Dataset | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) |
| --- | ---: | ---: | ---: | ---: |
| `x64` | `0.037086` | `0.036607` | `0.024139` | `0.037033` |
| `x256` | `0.570057` | `0.575253` | `0.376711` | `0.570595` |

Prepared-path means:

| Dataset | Backend | Bind+Run Mean (s) | Reuse Mean (s) |
| --- | --- | ---: | ---: |
| `x64` | `embree` | `0.036083` | `0.036070` |
| `x64` | `optix` | `0.023923` | `0.023827` |
| `x256` | `embree` | `0.573124` | `0.572878` |
| `x256` | `optix` | `0.375377` | `0.374774` |

Interpretation:

- OptiX remains the best current RTDL backend for this family on Linux
- Embree stays very close to the native CPU oracle
- prepared reuse is measurable but not transformative on the audited large rows
- Vulkan currently tracks CPU because the accepted runtime path for this family
  is correctness-first fallback, not native Vulkan traversal

## Backend Reading

### Python and native CPU oracles

- still the main correctness anchors
- clean against PostGIS on the large deterministic rows

### Embree

- parity-clean on all audited large rows
- performance is stable and very close to native CPU
- prepared execution is useful, but not a major step-change on this workload

### OptiX

- parity-clean on all audited large rows
- fastest RTDL backend on every audited large row
- still slower than PostGIS on these large deterministic cases
- prepared execution helps slightly and remains the best current RTDL story for
  this family

### Vulkan

- parity-clean on all audited large rows
- the current accepted runtime path for this family is still the
  correctness-first fallback boundary
- therefore the current Vulkan numbers are useful for product reporting, but not
  as evidence of native optimized parallel traversal maturity

## Final Conclusion

Goal 118 closes with this honest Linux large-scale performance result for
`segment_polygon_hitcount`:

- correctness vs PostGIS:
  - strong through `x1024`
- best current RTDL backend:
  - OptiX
- Embree status:
  - accepted and stable
- Vulkan status:
  - accepted for correctness
  - still not accepted as a native optimized traversal story for this family
- PostGIS comparison:
  - RTDL is still slower on the audited large rows

So the feature is now strong in this sense:

- it is implemented
- it is documented
- it is user-facing
- it is backend-audited
- it is large-scale validated against PostGIS
- and it now has a reproducible Linux performance report

The remaining gap is no longer correctness. It is backend-native optimization,
especially for Vulkan and, more broadly, for making this family competitive
against PostGIS at larger scales.

## Artifacts

- machine-readable summary:
  - [goal118 artifact JSON](goal118_segment_polygon_linux_large_perf_artifacts_2026-04-06/summary.json)
- rendered summary:
  - [goal118 artifact Markdown](goal118_segment_polygon_linux_large_perf_artifacts_2026-04-06/summary.md)
