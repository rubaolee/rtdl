# Goal 641: v0.9.5 Pre-Release Test Report

Date: 2026-04-19

## Scope

Pre-release test gate for the v0.9.5 bounded any-hit / visibility-row /
emitted-row reduction slice after Goals 632-645.

This test gate covers:

- full local unittest discovery on macOS;
- local Apple RT and Embree coverage;
- Linux focused backend validation with Embree, OptiX, Vulkan, and HIPRT built
  in the synced checkout;
- explicit v0.9.5 new tests for CPU any-hit, visibility rows, backend dispatch,
  OptiX native any-hit, Embree native any-hit, HIPRT native any-hit, and
  `rt.reduce_rows(...)`;
- explicit Goal645 tests for the v0.9.5 public release package and
  front-page/tutorial/example doc consistency.

## Local Full Test

Command:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result:

```text
Ran 1211 tests in 111.506s
OK (skipped=179)
```

Interpretation:

- No local release-blocking failures.
- OptiX, Vulkan, and HIPRT tests that require unavailable local backend
  libraries skipped on this Mac checkout.
- Apple RT and Embree tests ran where available.
- The newly added v0.9.5 any-hit, visibility, `reduce_rows`, and public release
  package tests are included in the full discovery run.

## Linux Focused Backend Test

Linux checkout:

```text
/tmp/rtdl_goal639_hiprt_anyhit
```

Backend bring-up:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
```

Backend probes:

```text
embree OK (4, 3, 0)
optix OK (9, 0, 0)
vulkan OK (0, 1, 0)
hiprt OK {'version': (2, 2, 15109972), 'api_version': 2002,
          'device_type': 1, 'device_name': 'NVIDIA GeForce GTX 1070'}
```

Command:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal636_backend_any_hit_dispatch_test \
  tests.goal637_optix_native_any_hit_test \
  tests.goal638_embree_native_any_hit_test \
  tests.goal639_hiprt_native_any_hit_test \
  tests.goal632_ray_triangle_any_hit_test \
  tests.goal633_visibility_rows_test
```

Result:

```text
Ran 23 tests in 3.648s
OK (skipped=2)
```

Expected skips:

- Apple RT is unavailable on Linux.

Linux coverage:

- CPU any-hit predicate lowers and matches CPU reference.
- CPU visibility rows match expected line-of-sight behavior.
- Embree any-hit matches CPU and native raw rows expose `("ray_id", "any_hit")`.
- OptiX any-hit matches CPU and native raw rows expose `("ray_id", "any_hit")`.
- HIPRT exports native any-hit 2D/3D symbols and matches CPU.
- Vulkan any-hit matches CPU through documented compatibility dispatch.

## v0.9.5 Test Inventory

New / relevant tests:

- `/Users/rl2025/rtdl_python_only/tests/goal632_ray_triangle_any_hit_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal633_visibility_rows_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal636_backend_any_hit_dispatch_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal637_optix_native_any_hit_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal638_embree_native_any_hit_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal639_hiprt_native_any_hit_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal644_reduce_rows_standard_library_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal645_v0_9_5_release_package_test.py`

Goal644 focused public-doc / helper verification:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal644_reduce_rows_standard_library_test tests.goal513_public_example_smoke_test tests.goal515_public_command_truth_audit_test -v

Ran 10 tests in 2.396s
OK
```

Goal644 tutorial/example harness:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py --machine local-goal644 --output docs/reports/goal644_tutorial_example_check_2026-04-19.json
```

Result:

```text
63 passed, 0 failed, 26 skipped, 89 total
```

Public command truth after Goal644:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```text
valid: true
runnable public commands found: 245
```

Goal645 focused public-doc / release package verification:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal511_feature_guide_v08_refresh_test tests.goal532_v0_8_release_authorization_test tests.goal645_v0_9_5_release_package_test tests.goal513_public_example_smoke_test tests.goal515_public_command_truth_audit_test -v

Ran 14 tests in 2.679s
OK
```

Goal645 tutorial/example harness:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py --machine local-goal645 --output docs/reports/goal645_tutorial_example_check_2026-04-19.json
```

Result:

```text
65 passed, 0 failed, 26 skipped, 91 total
```

Public command truth after Goal645:

```text
valid: true
runnable public commands found: 248
```

## Known Non-Blocking Boundaries

- Local Mac does not have local OptiX, Vulkan, or HIPRT backend libraries built.
  Those paths are validated on the Linux host.
- Linux does not have Apple RT. Apple RT is validated locally on macOS.
- HIPRT native any-hit is validated through HIPRT/Orochi on NVIDIA GTX 1070,
  not on AMD GPU hardware.
- HIPRT whole-call timing does not yet show a speedup because unprepared setup,
  geometry build, and JIT overhead dominate; this is not a correctness blocker.

## Verdict

Codex pre-release test verdict: ACCEPT.

No release-blocking test failures were found for the v0.9.5 any-hit /
visibility-row / emitted-row reduction slice.

## External Review

Combined Goals 641-643 review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal641_643_external_review_2026-04-19.md`
- Verdict: ACCEPT.
- Original test finding: 1201 local tests and 23 Linux focused backend tests passed with
  expected skips only.
- Superseded after Goal645 by this report's 1211-test local full-suite result.
