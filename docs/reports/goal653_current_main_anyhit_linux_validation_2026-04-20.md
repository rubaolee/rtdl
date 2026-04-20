# Goal653: Current-Main Native Any-Hit Linux Validation

Date: 2026-04-20

## Verdict

Codex local verdict: ACCEPT.

Consensus:

- Codex: ACCEPT
- Gemini 2.5 Flash: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal653_gemini_flash_review_2026-04-20.md`

Claude was called with the same handoff request, but the CLI process stalled
without writing a report and was terminated to avoid leaving another long-lived
process open. Goal653 is closed with the required 2-AI consensus.

Goal653 validates the current-main post-release any-hit backend state on the
Linux GPU host after Goals650-652:

- OptiX native any-hit
- Embree native any-hit
- HIPRT native any-hit
- Vulkan native any-hit
- Apple RT current-main native/native-assisted any-hit remains macOS-only and
  was validated in Goals651-652

## Host

Linux host:

```text
hostname: lx1
GPU: NVIDIA GeForce GTX 1070
driver: 580.126.09
VRAM: 8192 MiB
Python: 3.12.3
PostgreSQL: 16.13
```

## Checkout And Build

Synced current `main` from `/Users/rl2025/rtdl_python_only` to:

```text
/home/lestat/work/rtdl_goal653_anyhit_linux
```

Built/probed:

```text
make build-embree
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
make build-hiprt
```

Result:

- Embree probe: `Embree 4.3.0`
- OptiX build: OK
- Vulkan build: OK
- HIPRT build: OK, with only a vendor Orochi unused-result warning

## Runtime Probes

Environment:

```text
PYTHONPATH=src:.
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so
RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:$LD_LIBRARY_PATH
```

Probe result:

```text
embree (4, 3, 0)
optix (9, 0, 0)
vulkan (0, 1, 0)
hiprt {'version': (2, 2, 15109972), 'api_version': 2002, 'device_type': 1, 'device_name': 'NVIDIA GeForce GTX 1070'}
```

## Exported Native Any-Hit Symbols

```text
rtdl_optix_run_ray_anyhit
rtdl_optix_run_ray_anyhit_3d
rtdl_vulkan_run_ray_anyhit
rtdl_vulkan_run_ray_anyhit_3d
rtdl_hiprt_run_ray_anyhit_2d
rtdl_hiprt_run_ray_anyhit_3d
```

## Focused Tests

Command:

```text
python3 -m unittest \
  tests.goal636_backend_any_hit_dispatch_test \
  tests.goal637_optix_native_any_hit_test \
  tests.goal638_embree_native_any_hit_test \
  tests.goal639_hiprt_native_any_hit_test \
  -v
```

Result:

```text
Ran 15 tests in 8.763s
OK (skipped=2)
```

The two skips are expected Apple RT skips on Linux.

Covered:

- Embree 2D and 3D any-hit parity with CPU.
- OptiX 2D and 3D any-hit parity with CPU and raw rows.
- Vulkan 2D and 3D any-hit parity with CPU.
- HIPRT 2D and 3D any-hit parity with CPU and direct runtime calls.
- `visibility_rows` dispatch through backend any-hit for available Linux
  backends.

## Documentation Boundary Refresh

Updated release-facing v0.9.5 package docs to distinguish:

- released `v0.9.5` tag boundary, where Vulkan and Apple RT any-hit were
  compatibility dispatch;
- post-release current `main`, where Goal650 adds native Vulkan any-hit and
  Goals651-652 add Apple RT native/native-assisted any-hit after backend
  rebuilds.

Updated:

- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/tag_preparation.md`

Local doc verification:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal512_public_doc_smoke_audit_test tests.goal645_v0_9_5_release_package_test tests.goal646_public_front_page_doc_consistency_test -v
```

Result: 10 tests OK.

Public command audit:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result: valid true, 248 public commands across 14 docs.

## Honesty Boundary

- This is correctness and symbol/export validation, not a performance-speedup
  report.
- The Linux GPU is a GTX 1070; do not infer hardware RT-core speedup.
- Apple RT evidence remains macOS-only from Goals651-652.
- The released `v0.9.5` tag remains historical; current-main post-release
  backend improvements are not retroactively part of the tag.
