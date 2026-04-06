# Goal 123 Report: OptiX Candidate-Index Alignment

Date: 2026-04-06
Status: accepted

## Summary

Goal 123 moved the OptiX `segment_polygon_hitcount` default path onto the same
host-indexed candidate-reduction strategy introduced in Goal 122.

The older native OptiX traversal path is still present, but it is now behind:

- `RTDL_OPTIX_SEGPOLY_MODE=native`

So the default behavior is now:

- correctness-preserving host-indexed candidate reduction
- exact refine unchanged
- dramatic reduction in candidate scanning work

## Code touched

- [rtdl_optix.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp)

Linux artifacts:

- [summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal123_optix_candidate_index_artifacts_2026-04-06/summary.json)
- [summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal123_optix_candidate_index_artifacts_2026-04-06/summary.md)

## Correctness result

Local focused regression:

- `PYTHONPATH=src:. python3 -m unittest tests.goal110_segment_polygon_hitcount_closure_test tests.goal114_segment_polygon_postgis_test tests.goal116_segment_polygon_backend_audit_test tests.goal118_segment_polygon_linux_large_perf_test`
- result:
  - `12` tests
  - `OK`
  - `5` skipped on the local Mac because `geos_c` is absent there

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
  - OptiX: `0.000878 s`
- `x256`
  - OptiX: `0.003307 s`

### Large PostGIS-backed rows

- `x64`
  - PostGIS: `0.009207 s`
  - OptiX: `0.009804 s`
- `x256`
  - PostGIS: `0.051580 s`
  - OptiX: `0.007160 s`
- `x512`
  - PostGIS: `0.098630 s`
  - OptiX: `0.013913 s`
- `x1024`
  - PostGIS: `0.314453 s`
  - OptiX: `0.028282 s`

## Before vs after

Compared with the pre-alignment OptiX story:

- `x256`
  - before: about `0.38 s`
  - after: `0.007160 s`
- `x1024`
  - before: about `6.0 s`
  - after: `0.028282 s`

So the OptiX lag is no longer the main feature bottleneck.

## Interpretation

This is a real performance win, but it must be described correctly.

What changed:

- OptiX now uses the same host-indexed candidate-reduction idea as the other
  backends

What did **not** change:

- this is not a new RT-core-native traversal success
- the older native path is still only an optional experimental path

So Goal 123 should be read as:

- algorithmic alignment success
- OptiX performance closure for the current feature

not as:

- a proof that the native custom-primitive OptiX traversal path is now the best
  implementation

## External review follow-up

External Claude review was later completed in:

- [goal107_123_package_review_claude_2026-04-06.md](goal107_123_package_review_claude_2026-04-06.md)

That review accepted the Goal 123 implementation as a genuine performance
alignment win while explicitly confirming that the gain comes from the
host-indexed candidate strategy rather than native RT-core maturity.

## Final conclusion

Goal 123 closes successfully.

After Goals 122 and 123 together, the `segment_polygon_hitcount` feature now
has:

- strong correctness
- large deterministic PostGIS parity
- strong Linux large-row performance across CPU, Embree, OptiX, and Vulkan

That is the strongest state this feature line has reached so far.

## Review status

Available reviewers have been asked to audit this result inside the current tool
environment.

Those audits found only wording/attribution issues:

- do not describe this as a native OptiX-path win
- do not overstate OptiX as the fastest backend on every audited row

Those issues were corrected before publish.

The user also required Claude as part of the consensus flow. A literal Claude
review is not available in this environment, so the package remains marked:

- pending external Claude review
