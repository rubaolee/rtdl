# Goal 122 Report: Segment-Polygon Candidate-Index Redesign

Date: 2026-04-06
Status: pending external Claude review

## Summary

Goal 122 replaced the “scan every polygon, then bbox-test” approach with a
simple 1D bucket index over polygon bbox x-ranges in the exact
`segment_polygon_hitcount` paths.

This changed the algorithm from:

- all-polygons scan per segment

to:

- nearby-polygon candidate enumeration per segment
- then exact refine on that reduced candidate set

The accepted semantics did not change.

## Code touched

- [reference.py](/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py)
- [rtdl_oracle.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp)
- [rtdl_embree.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp)
- [rtdl_vulkan.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp)

Linux artifacts:

- [summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal122_segment_polygon_candidate_index_artifacts_2026-04-06/summary.json)
- [summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal122_segment_polygon_candidate_index_artifacts_2026-04-06/summary.md)

## Correctness result

Local focused regression:

- `PYTHONPATH=src:. python3 -m unittest tests.goal110_segment_polygon_hitcount_closure_test tests.goal114_segment_polygon_postgis_test tests.goal116_segment_polygon_backend_audit_test tests.goal118_segment_polygon_linux_large_perf_test`
- result:
  - `12` tests
  - `OK`
  - `5` skipped on the Mac because the existing `geos_c` native dependency is
    absent there

Clean Linux host:

- the same `12` tests
- result:
  - `OK`

Large deterministic PostGIS parity remained clean on Linux for:

- `x64`
- `x256`
- `x512`
- `x1024`

## Performance result on Linux

### Current-run means

- `x64`
  - CPU: `0.001969 s`
  - Embree: `0.000907 s`
  - OptiX: `0.024286 s`
  - Vulkan: `0.001948 s`
- `x256`
  - CPU: `0.007606 s`
  - Embree: `0.003525 s`
  - OptiX: `0.377668 s`
  - Vulkan: `0.007631 s`

### Large PostGIS-backed rows

- `x256`
  - PostGIS: `0.049609 s`
  - CPU: `0.008589 s`
  - Embree: `0.007502 s`
  - OptiX: `0.381387 s`
  - Vulkan: `0.007845 s`
- `x512`
  - PostGIS: `0.098995 s`
  - CPU: `0.021371 s`
  - Embree: `0.014694 s`
  - OptiX: `1.510656 s`
  - Vulkan: `0.020961 s`
- `x1024`
  - PostGIS: `0.313028 s`
  - CPU: `0.032431 s`
  - Embree: `0.028554 s`
  - OptiX: `6.020820 s`
  - Vulkan: `0.038705 s`

## Interpretation

This is the first redesign for `segment_polygon_hitcount` that materially
changed the large deterministic performance story.

What improved:

- CPU improved drastically
- Embree improved drastically
- Vulkan improved drastically
- on the accepted larger deterministic rows (`x256`, `x512`, `x1024`), all
  three now beat PostGIS

What did not improve:

- OptiX remained effectively unchanged

That difference is technically coherent:

- the new candidate index lives in the host-side exact counting paths
- OptiX still uses its separate native path and therefore does not benefit from
  this specific redesign

So Goal 122 does **not** prove a broad RT-core win.
It proves something narrower and still important:

- the main bottleneck was candidate scanning
- reducing that scanning cost makes the non-OptiX backends much stronger

## Final conclusion

Goal 122 is a real success for this feature line.

The feature now has:

- strong correctness evidence
- large deterministic PostGIS parity
- a materially stronger CPU/Embree/Vulkan performance story on Linux
- CPU/Embree/Vulkan wins over PostGIS on the larger audited deterministic rows
  (`x256` through `x1024`)

The remaining main performance problem is now isolated:

- OptiX still needs a redesign that benefits from the same candidate-reduction
  idea instead of staying on its separate native path

## Review status

Available reviewers have been asked to audit this result inside the current tool
environment.

The user also required Claude as part of the consensus flow. A literal Claude
review is not available in this environment, so the package remains marked:

- pending external Claude review
