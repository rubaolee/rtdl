# Goal2517: Partner-Resident Fused Grouped `sum_count` i64

## Purpose

Goal2516 proved `avg_as_sum_count` as a semantic composite: average-like output
is represented as `sum + count`, with no native average ABI. Goal2517 removes
the remaining two-launch overhead in the experimental OptiX partner-resident
path by adding one generic fused sum_count grouped reduction.

This is still a generic grouped i64 reduction. It is not a RayDB-native ABI and
it does not add a native average operation.

## Design

- Add `RtdlDbGroupedSumCountRow { group_key, sum, count }` to the OptiX native
  prelude.
- Add `RTDL_GROUPED_OP_SUM_COUNT = 5u` and
  `device_column_grouped_i64_compact_sum_count_kernel` to the generic device
  column grouped reduction kernel packet.
- Export
  `rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity`.
- Add Python binding
  `run_optix_partner_resident_columnar_grouped_sum_count_i64(...)`.
- Change the RayDB-style experimental partner-resident `avg_as_sum_count` path
  to preserve semantic lowering as `["sum", "count"]`, but execute it with one
  fused native reduction launch.

## Claim Boundary

- No native average ABI was added.
- No app-specific vocabulary was added to the native grouped reduction ABI.
- No true zero-copy claim is authorized; output rows are still materialized for
  Python inspection.
- No public speedup claim is authorized from this goal alone.
- No SQL, DBMS, authors-code, or full RayDB reproduction claim is authorized.

## Evidence

- Local contract tests: `tests/goal2517_partner_resident_fused_sum_count_i64_test.py`.
- Pod evidence runner:
  `scripts/goal2517_partner_resident_fused_sum_count_pod.py`.
- Pod artifact:
  `docs/reports/goal2517_partner_resident_fused_sum_count_pod_2026-05-23.json`.
- Pod build log:
  `docs/reports/goal2517_make_build_optix_2026-05-23.txt`.
- Pod command provided for this evidence packet:
  `ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519`.
- Actual key used from this Mac:
  `~/.ssh/id_ed25519_rtdl_codex`, because `~/.ssh/id_ed25519` was not present.
- Pod source setup: reset `/root/rtdl_python_only_goal2517` to
  `origin/main` at `a9193856547bf692069955a3dbaf6c3e00c09b1b`, then rsynced the
  current Mac working tree over that checkout for Goal2517 dirty changes.
- OptiX headers: cloned NVIDIA `optix-dev` into `/root/vendor/optix-dev` and
  checked out `v8.0.0` (`OPTIX_VERSION 80000`, ABI 87), because `v9.1.0`
  produced `Unsupported ABI version` on driver 550.
- CUDA environment: CUDA 12.8, NVIDIA driver 550.127.05, RTX 4000 Ada.
- CUDA driver/toolkit fix: the initially installed `cuda-compat-12-8`
  `575.57.08-0ubuntu1` package contained no usable compatibility libraries in
  this pod. Downgrading to `cuda-compat-12-8=570.211.01-0ubuntu1` installed
  `/usr/local/cuda-12.8/compat/libcuda.so*`. With
  `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda/lib64`, Goal2517
  runs without `RTDL_OPTIX_PTX_COMPILER`, `RTDL_OPTIX_PTX_ARCH`, or an `RTDL_NVCC`
  wrapper.
- Additional pod smoke: a real OptiX `ray_triangle_any_hit` pipeline ran against
  expected rows with `match == true` under the same fixed environment.

Observed pod result:

- CUDA available.
- Direct fused `sum_count` rows match the CPU `avg_as_sum_count` reference rows.
- App `avg_as_sum_count` rows match CPU reference rows.
- Full experimental partner-resident suite matches CPU reference rows.
- App metadata records `native_launch_count == 1`.
- App metadata records `fused_native_reduction == true`.
- App metadata records `native_avg_abi_added == false`.
- Pod focused tests:
  `PYTHONPATH=src:. python3 -m unittest tests.goal2515_partner_resident_grouped_min_max_i64_test tests.goal2516_partner_resident_composite_avg_sum_count_test tests.goal2517_partner_resident_fused_sum_count_i64_test`
  -> 18 tests OK.
- Broader pod partner-resident regression:
  `PYTHONPATH=src:. python3 -m unittest tests.goal2505_partner_resident_columnar_descriptor_contract_test ... tests.goal2517_partner_resident_fused_sum_count_i64_test`
  -> 69 tests OK across Goals2505-2517.
- Local focused tests:
  `PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2515_partner_resident_grouped_min_max_i64_test tests.goal2516_partner_resident_composite_avg_sum_count_test tests.goal2517_partner_resident_fused_sum_count_i64_test`
  -> 18 tests OK.
