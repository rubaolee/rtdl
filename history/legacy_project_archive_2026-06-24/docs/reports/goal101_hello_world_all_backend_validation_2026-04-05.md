# Goal 101 Report: Hello-World All-Backend Validation

Date: 2026-04-05
Status: accepted and reviewed

## Objective

Validate the onboarding/tutorial hello-world slice and repair the Linux OptiX
failure that blocked the backend-switching example.

Validated head:

- `e15ee77` plus the local Goal 101 patch

Fresh Linux clone used for the hard gate:

- `/home/lestat/work/rtdl_goal100_clean`

## Problem found

The backend-switching hello-world example ran on Linux for:

- `cpu_python_reference`
- `cpu`
- `embree`
- `vulkan`

but failed for:

- `optix`

Observed failure:

- `NVRTC compile failed for rayhit_kernel.cu`
- missing standard C headers such as:
  - `stdint.h`
  - `math.h`

## Repair

File repaired:

- [rtdl_optix.cpp](../../src/native/rtdl_optix.cpp)

What changed:

- the embedded OptiX ray-hit CUDA source was made more self-contained for basic
  type/math helpers
- PTX compilation now falls back from `nvrtc` to `nvcc` automatically when
  NVRTC compilation fails

Why that is the right fix:

- the hello-world ray query is a real supported RTDL path
- requiring users to discover a manual `RTDL_OPTIX_PTX_COMPILER=nvcc`
  workaround would be a release-quality bug
- automatic fallback preserves the existing fast path when NVRTC works, while
  making the path usable on the Linux validation host

## Validation

### Local example sanity

Command:

- `PYTHONPATH=src:. python3 examples/rtdl_hello_world.py`

Observed output:

- `hello, world`

Command:

- `PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference`

Observed result:

- `triangle_hit_count = 2`
- `visible_hit_rect_id = 2`
- `visible_hit_label = "hello, world"`

### Linux all-backend hello-world smoke

Artifact:

- [goal101_hello_world_all_backends.json](goal101_hello_world_validation_artifacts_2026-04-05/goal101_hello_world_all_backends.json)

Backends run successfully on the clean Linux clone:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`
- `vulkan`

All five returned the same visible hit:

- `visible_hit_rect_id = 2`
- `visible_hit_label = "hello, world"`

### Linux full regression matrix

Artifact:

- [goal101_full_matrix.json](goal101_hello_world_validation_artifacts_2026-04-05/goal101_full_matrix.json)

Command:

- `PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group full`

Result:

- `293 tests`
- `OK`
- `1 skipped`

## Honest conclusion

Goal 101 succeeded locally.

The tutorial slice is real, the OptiX Linux issue is repaired for the
backend-switching hello-world example, and the clean Linux clone still passes
the full regression matrix with the fix applied.

Review note:

- Claude identified one latent asymmetry in the new `nvcc` fallback helper:
  `extra_opts` were not being forwarded on the fallback path
- that helper was corrected after review
- the corrected helper was then rebuilt and the Linux OptiX hello-world example
  still passed

Important boundary:

- this is a focused validation package for the onboarding/tutorial slice and
  the OptiX PTX fallback repair
- it is not a replacement for the broader release package or paper review
