# Goal 570: v0.9 Final Pre-Release Test, Documentation, and Flow Audit

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Status: accepted by Codex, Claude, and Gemini Flash.

## Purpose

This is the final pre-release gate requested before the user-controlled v0.9
release action. It verifies the post-Goal568/Goal569 state with:

- total local test discovery;
- fresh Linux backend-capable test discovery;
- explicit Linux HIPRT correctness matrix;
- explicit Linux HIPRT/Embree/OptiX/Vulkan parity/performance smoke matrix;
- public documentation consistency checks;
- release-flow audit.

This report does not tag, commit, or publish `v0.9.0`. It only records whether
the candidate is ready for the explicit release action.

## Linux Fresh Checkout

Fresh validation checkout:

`/tmp/rtdl_goal570_final_release_gate`

Sync rule:

```bash
rsync -a --delete --exclude .git --exclude .venv --exclude build --exclude __pycache__ --exclude '*.pyc' \
  /Users/rl2025/rtdl_python_only/ \
  lestat-lx1:/tmp/rtdl_goal570_final_release_gate/
```

PostgreSQL check:

```text
psql (PostgreSQL) 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)
/var/run/postgresql:5432 - accepting connections
```

Backend build/probe:

```bash
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
make build-embree
```

Embree probe:

```text
Embree 4.3.0
```

Runtime environment:

```bash
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
```

## Total Test Gate

### Local macOS Full Test

Command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 66.337s
OK
```

### Linux Full Backend-Capable Test

Command:

```bash
cd /tmp/rtdl_goal570_final_release_gate
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 150.277s
OK
```

### Linux HIPRT Correctness Matrix

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal547_hiprt_correctness_matrix.py \
  --output docs/reports/goal570_hiprt_correctness_matrix_linux_2026-04-18.json
```

Local copy:

`/Users/rl2025/rtdl_python_only/docs/reports/goal570_hiprt_correctness_matrix_linux_2026-04-18.json`

Summary:

```json
{"pass": 18, "not_implemented": 0, "hiprt_unavailable": 0, "fail": 0}
```

### Linux Cross-Backend Parity/Performance Smoke Matrix

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal560_hiprt_backend_perf_compare.py \
  --output docs/reports/goal570_hiprt_backend_perf_compare_linux_2026-04-18.json
```

Local copy:

`/Users/rl2025/rtdl_python_only/docs/reports/goal570_hiprt_backend_perf_compare_linux_2026-04-18.json`

Summary:

```json
{"pass": 72, "backend_unavailable": 0, "fail": 0}
```

Boundary: this matrix is a one-repeat small-fixture release smoke comparison.
It proves availability and row parity across HIPRT, Embree, OptiX, and Vulkan;
it is not a production throughput benchmark or RT-core speedup claim.

## Documentation Gate

Audited public/release-facing files:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_hiprt_ray_triangle_hitcount.py`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

Stale wording check:

```bash
rg -n 'current released state is the bounded `v0\.7\.0`|current released version is `v0\.7\.0`|not yet released as `v0\.8\.0`|experimental HIPRT|HIPRT preview|preview backend|HIPRT-preview|one workload only|narrow single-workload|broader prepared HIPRT reuse remains future|DB table reuse.*future|does not yet cover.*DB' ...
```

Result: no matches.

Local Markdown link check:

```text
checked 12 files
bad_links 0
```

Focused documentation tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal544_hiprt_docs_examples_test \
  tests.goal560_hiprt_backend_perf_compare_test
```

Result:

```text
Ran 3 tests in 0.102s
OK
```

One documentation inconsistency was found and fixed during this final gate:

- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md` still said the
  current released state was the bounded `v0.7.0` package. It now says the
  current released state is `v0.8.0`, while `v0.9` remains the active HIPRT
  candidate until explicit release action.

## Flow Audit

The v0.9 evidence chain is complete through Goal 570:

- Goal 560: 18-workload HIPRT/Embree/OptiX/Vulkan matrix.
- Goal 562: pre-release test gate.
- Goal 563: documentation audit.
- Goal 564: release-candidate flow audit.
- Goal 565: prepared HIPRT 3D ray/triangle performance mitigation.
- Goal 566: prepared HIPRT 3D fixed-radius nearest-neighbor mitigation.
- Goal 567: prepared HIPRT graph CSR mitigation.
- Goal 568: prepared HIPRT bounded DB table reuse, including PostgreSQL
  comparison.
- Goal 569: post-Goal568 release-gate refresh.
- Goal 570: final total test/doc/audit gate.

Goal 568 and Goal 569 both have Codex, Claude, and Gemini Flash ACCEPT verdicts.
Goal 570 now also has external ACCEPT review from Claude and Gemini Flash.

## Current Known Errors

Known code errors: none release-blocking. Local tests, fresh Linux full tests,
HIPRT correctness matrix, and cross-backend matrix all pass.

Known documentation errors: none release-blocking after the feature-guide fix.
The public docs consistently state:

- current released version before the final action is `v0.8.0`;
- `v0.9` is the HIPRT candidate/release line;
- HIPRT is validated on Linux through the HIPRT/Orochi CUDA path;
- no AMD GPU validation is claimed;
- no HIPRT CPU fallback is claimed;
- no RT-core speedup is claimed from the GTX 1070 validation host;
- bounded DB support is not a DBMS or arbitrary SQL claim.

Known flow errors: none release-blocking. The final release action remains
explicitly separate and user-controlled.

## Codex Verdict

ACCEPT. The v0.9 candidate is ready for the final user-controlled release
action.

## External Consensus

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal570_external_review_2026-04-18.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal570_gemini_flash_review_2026-04-18.md`

Consensus verdict: ACCEPT, no blockers.
