# Gemini Review: Goal3658 RayJoin PIP Tuned Device Predicate

Date: 2026-06-06
Verdict: `accept-with-boundary`

## Overview

Goal3658 introduces a generic `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS` specialization to the native OptiX engine to improve performance for point-in-polygon (PIP) scalar count workloads. This allows RTDL/OptiX to avoid host-side exact refinement in the timed hot path for validated domains, enabling it to supersede the prior CuPy-based dense baseline for the measured public-CDB slice.

## Questions & Findings

### 1. Does the new `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS` specialization remain generic and app-agnostic?

**Yes.** Implementation in `src/native/optix/rtdl_optix_workloads.cpp` uses a standard environment variable lookup and string replacement in the PTX source. It operates on a generic `point_eps` constant within the point/closed-shape membership kernel. No RayJoin-specific or CDB-specific logic or terminology is present in the native implementation. This is further verified by `tests/goal3658_rayjoin_pip_tuned_device_predicate_test.py`.

### 2. Does the runner correctly scope and record `--rtdl-pip-device-predicate-eps`, and does the measured route remain fail-closed?

**Yes.** The runner `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py` uses a scoped `temporary_env` to apply the epsilon only during RTDL PIP execution. Every measured sample in the `device_filtered_prepared_points_validated` mode is checked against an exact inclusive prepared count (the oracle); any mismatch results in a `RuntimeError`, ensuring the timing lane is only recorded for correct results.

### 3. Does the clean A5000 artifact support the stated bounded finding?

**Yes.** The artifact `docs/reports/goal3658_rayjoin_pip_tuned_device_predicate_a5000/summary.json` shows:
- **Count:** `1417` (exact).
- **Commit:** `9c85c2a0` (clean, empty dirty list).
- **RTDL Tuned Median:** `0.283574ms` over `30000` internal repeats.
- **Prior CuPy Baseline:** `0.437917ms` (superseded).
- **RayJoin `query_exec`:** `0.191354ms` (RTDL still trails by ~1.48x).

### 4. Are the claim boundaries intact?

**Yes.** Both the summary report and the JSON artifact explicitly set all public/release/paper-reproduction claim flags to `false`. The report clearly states that this is an internal performance improvement and not authorization for public speedup wording or RTDL-beats-RayJoin claims.

### 5. Are the Goal3657 integration text and tests updated honestly?

**Yes.** The integration report `docs/reports/goal3657_v2_9_rayjoin_lsi_10s_integration_2026-06-06.md` accurately reflects that for PIP scalar positive-membership counts, RTDL/OptiX now beats the prior CuPy recommendation while still trailing RayJoin. Tests in `tests/goal3657_v2_9_rayjoin_lsi_10s_integration_test.py` confirm this narrative is present.

## Verdict Details

The verdict is **`accept-with-boundary`**.

### Boundary

Goal3658 is a valid internal v2.9 performance improvement and positioning update for the RTDL/OptiX PIP scalar count route. It is **not** authorization for:
- Public v2.9 release or speedup wording.
- Broad RT-core or whole-app RayJoin speedup claims.
- RayJoin paper reproduction or RTDL-beats-RayJoin claims.
- True zero-copy claims or app-specific native-engine logic.

The performance gain is achieved through a generic tuning knob (`eps`) that allows the device-side filter to be used as an exact count on this specific validated domain, avoiding candidate download and host refinement.
