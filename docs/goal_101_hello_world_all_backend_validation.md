# Goal 101: Hello-World All-Backend Validation

## Objective

Validate the new onboarding/tutorial slice and repair the OptiX Linux failure
that blocked the backend-switching hello-world example.

This goal closes when:

- the minimal hello-world example runs locally
- the backend-switching hello-world example runs on all supported backends on
  the Linux validation host
- the OptiX fix is covered by a clean Linux full-matrix rerun
- the final package is reviewed before publish

## Why this goal exists

The new tutorial examples are now part of the first-user path. They need to be
real, not illustrative only.

The Linux backend-switching example exposed a real OptiX bug:

- NVRTC compilation for the OptiX ray-hit path failed on missing C headers

That problem had to be repaired and then revalidated under the release gate
before the tutorial slice could be treated as publishable.

## Required outputs

- one focused validation report
- one small artifact package with:
  - Linux all-backend hello-world results
  - Linux full-matrix result
- review artifacts from Codex plus external reviewers

## Acceptance

Goal 101 is done when:

- `examples/rtdl_hello_world.py` runs and prints `hello, world`
- `examples/rtdl_hello_world_backends.py` runs on:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`
- the clean Linux clone passes the full regression matrix after the OptiX fix
- the report clearly states the OptiX repair and the exact validation boundary
