# Goal 87 Report: Vulkan Long Exact-Source Unblocked

Date: 2026-04-05
Status: complete

## Summary

Goal 87 asked whether the Vulkan positive-hit `pip` path could be changed from
worst-case sparse-candidate allocation to a count/materialize contract that
actually runs on the accepted long exact-source `county_zipcode` prepared
surface.

The accepted answer is yes:

- the old guardrail failure is gone
- the long exact-source prepared surface now runs on Linux hardware
- parity against PostGIS is preserved on both reruns

Vulkan still does not beat PostGIS on this surface, but Goal 87 removes the
main scaling blocker identified in Goal 85.

## Problem Before Goal 87

Goal 85 already established that Vulkan had moved beyond the old dense host
full-scan design, but the implementation still preallocated the sparse
candidate buffer as if the worst case were required:

- `point_count x poly_count x sizeof(GpuPipCandidate)`

On the accepted long exact-source `county_zipcode` prepared surface, that
tripped the current Vulkan output guardrail before execution:

```text
RuntimeError: Vulkan PIP positive-hit output exceeds current Vulkan guardrail of 536870912 bytes
```

So the problem was no longer basic correctness. It was the allocation contract.

## Code Change

File changed:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`

The positive-hit Vulkan path now uses two passes:

1. count-only GPU pass
   - counts sparse candidates with an atomic counter
   - does not materialize candidate rows
2. materialize pass
   - allocates exactly for the counted candidate size
   - writes compact `(point_index, poly_index)` candidate pairs
3. host exact finalization
   - keeps the existing exact-finalize rule
   - preserves the published parity boundary

Full-matrix Vulkan behavior is unchanged.

## Validation

Linux build and smoke validation on `lestat-lx1` using the Goal 85 workspace:

```bash
cd /home/lestat/work/rtdl_goal85
make build-vulkan
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test tests.goal85_vulkan_prepared_exact_source_county_test
```

Result:

- `20` tests
- `OK`

This confirms the patched Vulkan backend still compiles and clears the accepted
Vulkan smoke slice on hardware.

## Long Exact-Source Prepared Measurement

Host:

- `lestat-lx1`

Surface:

- workload: long exact-source `county_zipcode`
- predicate: positive-hit `pip`
- boundary: execution-ready / prepacked
- source directories:
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json`

Measured result:

- row count: `39073`
- parity preserved on both reruns: `true`
- run 1:
  - Vulkan: `6.139390790 s`
  - PostGIS: `3.259119608 s`
- run 2:
  - Vulkan: `6.164127524 s`
  - PostGIS: `3.046611804 s`

Preparation profile:

- prepare kernel: `0.015264227 s`
- pack points: `0.053759134 s`
- pack polygons: `5.245195745 s`
- bind: `0.000031985 s`

## Outcome

Goal 87 closes the Vulkan allocation/scaling blocker from Goal 85.

Accepted claims:

- Vulkan now runs the accepted long exact-source prepared `county_zipcode`
  positive-hit `pip` surface that previously failed before execution.
- parity against PostGIS is preserved on both reruns.
- the old worst-case sparse-candidate allocation contract is no longer the
  gating blocker for this surface.

Non-claims:

- Goal 87 does not claim that Vulkan beats PostGIS on this surface.
- Goal 87 does not claim that Vulkan joins the OptiX/Embree mature-performance
  closure.
- Goal 87 does not claim that the repeated raw-input Vulkan story is complete.

## Interpretation

The important change is not the absolute runtime number. It is that Vulkan is
now executing the same long exact-source prepared row as the other mature
backends instead of failing at allocation time.

That means Vulkan has moved from:

- hardware-validated but blocked on the true long row

to:

- hardware-validated, parity-clean, and executable on the true long row

The remaining Vulkan gap is now straightforward:

- runtime performance is still behind PostGIS, OptiX, and Embree

but the backend is no longer blocked by the old candidate-allocation contract.

## Evidence

- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.md`
