# Goal 116 Segment/Polygon Full Backend Audit

Date: 2026-04-06  
Status: accepted

## Summary

Goal 116 finishes the full backend audit for `segment_polygon_hitcount`.

The current accepted result is:

- Python oracle remains the top correctness reference
- the native CPU oracle matches the Python oracle on the accepted audit cases
- Embree and OptiX are parity-clean on the accepted audit cases
- Vulkan is now parity-clean on the accepted audit cases and the accepted
  current implementation path for this family is correctness-first, not
  Vulkan-native traversal maturity
- large deterministic PostGIS validation is clean

So the feature is now in a stronger state than the earlier family-closure step:

- family closure
- performance characterization
- large PostGIS validation
- user-facing productization
- full backend audit

## What Was Checked

### Oracle parity matrix

The following datasets were checked against `cpu_python_reference`:

- `authored_segment_polygon_minimal`
- `tests/fixtures/rayjoin/br_county_subset.cdb`
- `derived/br_county_subset_segment_polygon_tiled_x4`
- `derived/br_county_subset_segment_polygon_tiled_x16`

The following backends were checked:

- `cpu`
- `embree`
- `optix`
- `vulkan`

Accepted result:

- every checked backend matched the Python oracle on every checked dataset

### PostGIS validation

Current-scale deterministic validation:

- dataset:
  - `derived/br_county_subset_segment_polygon_tiled_x64`
- scale:
  - `640` segments
  - `128` polygons
- PostGIS SHA256:
  - `bdfe3c868dbae0278436b1451dd5760564f57359096986e0bf95951dc57f507b`

Accepted parity result:

- `cpu`: true
- `embree`: true
- `optix`: true
- `vulkan`: true

Large deterministic validation:

- dataset:
  - `derived/br_county_subset_segment_polygon_tiled_x256`
- scale:
  - `2560` segments
  - `512` polygons
- PostGIS SHA256:
  - `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099`

Accepted parity result:

- `cpu`: true
- `embree`: true
- `optix`: true

The large `x256` row was not used to claim Vulkan maturity. The accepted Vulkan
cross-check remains the current-scale `x64` PostGIS row plus the oracle parity
matrix.

## Performance And Parallelization Status

The current measured backend story is:

- `cpu`
  - correctness oracle baseline
  - no prepared-path story
- `embree`
  - parity-clean
  - prepared reuse is materially useful on the audited cases
- `optix`
  - parity-clean
  - prepared reuse is materially useful on the audited cases
  - fastest backend on the accepted large PostGIS `x256` row:
    - `0.428418 s`
- `vulkan`
  - parity-clean
  - not accepted here as a native parallel traversal maturity story for this
    family
  - current accepted implementation path for correctness uses the Vulkan runtime
    fallback to the native CPU oracle for this workload family
  - therefore no accepted prepared-path or native parallel-performance claim is
    made for Vulkan here

On the accepted large deterministic PostGIS row (`x256`):

- PostGIS:
  - `0.055276 s`
- CPU oracle:
  - `0.632044 s`
- Embree:
  - `0.633632 s`
- OptiX:
  - `0.428418 s`

This means:

- correctness is strong
- OptiX is currently the best measured RTDL backend for this workload family
  among the audited large deterministic rows
- the feature is still not a strong performance story against PostGIS
- Vulkan still needs real backend work before any native-acceleration claim is
  justified

## Important Repair During This Goal

The audit uncovered a real correctness problem:

- the direct Vulkan path returned all-zero hit counts on fixture-backed and
  derived county cases

The accepted repair was:

- add a stronger fixture-backed Vulkan parity test
- keep the native-side exact helper in the Vulkan code
- make the public Vulkan runtime path for `segment_polygon_hitcount` use the
  accepted native CPU oracle fallback instead of silently returning incorrect
  Vulkan-native results

That repair improves the product surface because:

- the feature no longer silently lies on the Vulkan path
- the current runtime behavior now matches the documented honesty boundary

## Final Conclusion

Goal 116 closes with this final backend status for `segment_polygon_hitcount`:

- correctness:
  - strong
- external validation:
  - strong
- Embree support:
  - accepted
- OptiX support:
  - accepted
- Vulkan support:
  - accepted for correctness under the current fallback boundary
  - not accepted as native traversal/parallel maturity

So the feature is now fully in the codebase as a real RTDL feature, with:

- oracle closure
- backend closure
- PostGIS-backed external validation
- user-facing example/docs

but still with one clear remaining technical gap:

- a true Vulkan-native optimized/parallel implementation for this workload
  family has not been closed yet

## Artifacts

- machine-readable summary:
  - [goal116 artifact JSON](goal116_segment_polygon_backend_audit_artifacts_2026-04-06/summary.json)
- rendered summary:
  - [goal116 artifact Markdown](goal116_segment_polygon_backend_audit_artifacts_2026-04-06/summary.md)
