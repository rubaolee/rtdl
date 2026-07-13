# Call For Review: Goal4954-B Writer-Free Baseline Measurement Blocked

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4954b_writer_free_baseline_measurement_blocked_2026-07-04.md`
- `history/internal_docs/goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md`
- `history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py`

Requested verdict:

`accept_goal4954b_blocked_by_pod_missing_optix_sdk`

or:

`reject_blocker_continue_with_available_environment`

## Context

Goal4954-B is measurement-only. It should run the writer-free binary overlay
baseline on the public County x Soil sample. It must not implement optimizations
or change RTDL runtime/core code.

The current POD has:

- RTX 4000 Ada GPU;
- CUDA toolkit and `nvcc`;
- verified public sample data.

The POD does not appear to have:

- OptiX SDK headers;
- `build/librtdl_optix.so`;
- any compatible `RTDL_OPTIX_LIB`.

The first measurement attempt failed with `FileNotFoundError: librtdl_optix not
found`. `make build-optix` then failed because `optix.h` was missing.

## Review Questions

1. Is the blocker diagnosis correct: the measurement is blocked by missing
   OptiX SDK/native RTDL OptiX library, not by RayJoin algorithm work?

2. Did the executor avoid doing forbidden work:
   - no RTDL core/runtime edits;
   - no columnar reprojection/sort implementation;
   - no Layer 4 fusion;
   - no fake performance result?

3. Is the measurement script appropriate as a measurement-only artifact?

4. Is it correct not to continue by using CPU/Embree/non-OptiX routes, given
   Goal4954-B is specifically about the OptiX-backed RayJoin binary overlay
   path?

5. Are the required unblock options complete enough:
   - provide OptiX SDK;
   - provide configured POD image;
   - provide compatible prebuilt `librtdl_optix.so`?

6. Should Goal4954-B remain open but blocked with:

   `blocked_by_pod_missing_optix_sdk`

## Non-Authorization Boundary

Approving this blocker does not authorize:

- skipping OptiX measurement;
- using mismatched backends;
- claiming Goal4954-B completed;
- changing RTDL core/runtime;
- installing proprietary SDK material without proper authorization.
