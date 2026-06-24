# Goal2501: RayDB-Style OptiX Pod Validation Results

Date: 2026-05-22

## Verdict

The Goal2501 pod run closes the previously pending OptiX runtime parity gap for
the RayDB-style columnar aggregate slice.

Validated scope:

- backend: `optix`;
- modes: grouped `count` and grouped `sum`;
- fixture: tiny synthetic denormalized columnar fixture;
- contract: `columnar_grouped_aggregate_optix_columnar_payload`;
- result: both modes match the CPU reference;
- native ABI: no RayDB-specific native ABI added;
- zero-copy: not authorized; current path still uses the compatibility wrapper.

This is runtime parity evidence only. It is not performance evidence for public
speedup wording.

## Pod Environment

SSH access used:

```text
ssh root@69.30.85.198 -p 22017 -i ~/.ssh/id_ed25519_rtdl_codex
```

Note: the user-provided `~/.ssh/id_ed25519` path was not present on this Mac, so
the existing RTDL working key `~/.ssh/id_ed25519_rtdl_codex` was used.

Recorded environment artifact:

- `docs/reports/goal2501_raydb_style_pod_environment_2026-05-22.txt`

Key environment facts:

- GPU: NVIDIA RTX A5000
- driver: 570.211.01
- Python: 3.12.3
- CUDA: `/usr/local/cuda-12.8`, `nvcc` 12.8.93
- OptiX headers: NVIDIA `optix-dev` v9.0.0 at
  `/root/vendor/optix-dev-9.0.0`
- source checkout commit: `a9193856547bf692069955a3dbaf6c3e00c09b1b`
- local uncommitted Goal2492-2502 files were overlaid onto the pod checkout for
  validation.

## Build

Build command:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev-9.0.0 CUDA_PREFIX=/usr/local/cuda-12.8
```

Build artifact:

- `docs/reports/goal2501_make_build_optix_2026-05-22.txt`

Build result:

- `BUILD_RC=0`
- `build/librtdl_optix.so` was produced and loaded by `rt.optix_version()`.
- `rt.optix_version()` reported `(9, 0, 0)`.

## Test Results

Focused OptiX test:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2498_raydb_style_optix_count_sum_parity_test
```

Result:

- `Ran 6 tests`
- `OK`

Focused RayDB-style suite artifact:

- `docs/reports/goal2501_raydb_style_focused_suite_pod_2026-05-22.txt`

Result:

- `Ran 31 tests`
- `OK (skipped=2)`

The two skips are Embree runtime skips on this pod. They do not affect the OptiX
parity result.

## App Result

App artifact:

- `docs/reports/goal2501_raydb_style_optix_app_pod_2026-05-22.json`

Observed required fields:

- `"backend": "optix"`
- `"all_match_cpu_reference": true`
- `"native_abi_added": false`
- `"contract": "columnar_grouped_aggregate_optix_columnar_payload"`
- `"rt_core_accelerated": true`
- `lowering_plan.true_zero_copy_authorized == false`
- `lowering_plan.uses_compatibility_wrapper == true`

## Matrix Result

Matrix artifact:

- `docs/reports/goal2501_raydb_style_backend_matrix_pod_2026-05-22.json`

Observed required fields:

- `cases.optix.status == "ok"`
- `cases.optix.all_match_cpu_reference == true`
- `cases.optix.modes.count.matches_cpu_reference == true`
- `cases.optix.modes.sum.matches_cpu_reference == true`
- the diagnostic claim boundary is present.

Embree was skipped in the pod matrix because Embree was not installed. Local
Embree parity remains covered by the local Goal2497/Goal2500 evidence.

## Claim Boundary

Allowed internal wording after this pod run:

- OptiX runtime parity is validated for grouped `count` and grouped `sum` over
  the synthetic RayDB-style columnar aggregate contract.
- The OptiX path uses existing generic columnar payload support through a
  compatibility wrapper.

Blocked wording remains unchanged:

- RayDB reproduction;
- authors-code comparison;
- SQL engine or DBMS behavior;
- public speedup wording;
- true zero-copy wording;
- whole-app acceleration;
- min/max/avg native OptiX support;
- new app-specific native ABI.
