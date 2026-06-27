# Goal676/677: Cross-Engine Optimization Closure And Public Doc Refresh

Status: implemented, documented, reviewed, accepted

Date: 2026-04-20

## Scope

This report closes the current cross-engine visibility/count optimization round
after the Apple RT optimization playbook was applied to OptiX, HIPRT, and
Vulkan.

The work is intentionally scoped to repeated 2D visibility / any-hit / blocked
ray count workloads where:

- the build-side triangle set is stable enough to prepare once;
- the probe-side ray set can be reused or prepacked;
- the app can consume compact yes/no rows or a scalar count instead of full
  materialized row dictionaries.

This is not a DB workload optimization closure, not a graph workload
optimization closure, and not a broad backend ranking.

## Implemented Optimization Pattern

The common pattern is:

1. Prepare build-side data once.
2. Reuse backend acceleration structure state across repeated queries.
3. Prepack repeated probe-side rays where Python packing dominates.
4. Prefer compact rows or scalar counts when the app does not need full rows.

## Engine Results

| Engine | Current-main optimized path | Evidence | Honest claim |
| --- | --- | --- | --- |
| Apple RT | prepared MPS/Metal 2D scene + prepacked rays + scalar blocked-ray count | `0.00091-0.00133 s` per repeated query for `32768` rays / `8192` triangles on Apple M4 | strong Mac app-level scalar-count win; not full emitted-row speedup |
| OptiX | prepared 2D scene + prepacked 2D rays + scalar count | about `0.000062-0.000075 s` versus direct around `0.00503 s` on Linux GTX 1070 | strong repeated-query win; GTX 1070 evidence is not RT-core evidence |
| HIPRT | prepared 2D Ray/Triangle any-hit rows | `0.007464495 s` versus direct `0.580084853 s` for `4096` rays / `1024` triangles on Linux | large setup/JIT/BVH reuse win on HIPRT/Orochi CUDA; not AMD GPU evidence |
| Vulkan | prepared 2D scene + prepacked 2D rays | `0.004496957 s` versus direct `0.008035034 s` for `4096` rays / `1024` triangles; `0.021956306 s` versus `0.028801230 s` for `32768` rays / `8192` triangles on Linux | real repeated-query win only when rays are prepacked |

## Source Changes

Relevant implementation changes from this round include:

- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`

Focused tests added or updated:

- `/Users/rl2025/rtdl_python_only/tests/goal671_optix_prepared_anyhit_count_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal674_hiprt_prepared_anyhit_2d_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal675_vulkan_prepared_anyhit_2d_test.py`

## Documentation Refresh

Goal677 refreshed the public-facing docs so the current-main story is visible
without overclaiming:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_main_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

The docs now make three points explicit:

- prepared repeated-query visibility/count optimization exists beyond Apple RT;
- the strongest performance paths require prepared build data and prepacked
  probe data;
- these results are not broad speedup claims for all workloads, engines, or
  output contracts.

## Verification So Far

Local focused tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal675_vulkan_prepared_anyhit_2d_test -v

Ran 19 tests in 0.003s
OK (skipped=7)
```

Linux validation already recorded in the goal-specific reports:

- Goal674 HIPRT focused Linux validation: `13` tests OK.
- Goal675 Vulkan focused Linux validation: `14` tests OK, `4` skips.
- Goal672/673 OptiX Linux validation and performance evidence recorded in the
  OptiX reports.

Mechanical check:

```text
git diff --check
```

Result before this doc refresh: clean. A final doc-audit pass should be run
after this report and the public-doc edits.

## Allowed Claims

Allowed:

- RTDL current `main` has a proven prepared/prepacked optimization direction
  for repeated 2D visibility/count-style workloads.
- Apple RT, OptiX, HIPRT, and Vulkan each now have bounded current-main
  evidence that preparation and lower-copy probe paths reduce repeated-query
  overhead.
- Python overhead is a real performance issue; prepacking and reduced output
  contracts are first-class optimization tools.

Not allowed:

- broad speedup across all RTDL workloads;
- broad backend ranking from these measurements;
- DB or graph speedup from visibility/count data;
- full emitted-row Apple RT speedup from scalar count evidence;
- RT-core speedup from GTX 1070 evidence;
- AMD GPU validation from HIPRT/Orochi CUDA evidence;
- native backend acceleration for `rt.reduce_rows(...)`.

## Current Consensus State

- Goal674 HIPRT prepared 2D any-hit: Codex, Claude, and Gemini Flash accepted.
- Goal675 Vulkan prepared 2D any-hit plus packed rays: Codex and Gemini Flash
  accepted; Claude CLI stalled and produced no verdict file.
- Goal676/677 closure and doc refresh: Codex, Claude, and Gemini accepted.

## Next Gate

Run broader total test, total doc audit, and total flow audit if this
current-main optimization round is to become a release.
