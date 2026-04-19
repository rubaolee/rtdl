# Goal 567: HIPRT Prepared Graph CSR Performance Round

Date: 2026-04-18

## Scope

Goal 567 extends the v0.9 HIPRT performance-improvement line from prepared 3D
ray/triangle and prepared 3D nearest-neighbor workloads to graph CSR build-side
reuse.

The prepared object is intentionally bounded:

- one prepared HIPRT graph CSR context owns the uploaded CSR/edge data, AABB
  geometry, function tables, and compiled BFS/triangle kernels
- repeated query calls upload only the frontier/visited set or edge seeds
- the public RTDL language surface is unchanged

## Implementation Summary

Files changed:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal567_hiprt_prepared_graph_test.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal567_hiprt_prepared_graph_perf.py`

Native HIPRT now has a prepared graph CSR context that owns:

- HIPRT runtime/context
- uploaded CSR row offsets and column indices
- uploaded encoded graph edges
- graph-edge source AABBs
- HIPRT AABB geometry
- BFS function table and compiled BFS kernel
- triangle-match function table and compiled triangle-match kernel

The triangle-match kernel was also improved from a single-thread launch to
one GPU thread per seed. BFS has a correctness boundary: deterministic global
dedupe is order-sensitive, so `dedupe=True` keeps the serialized traversal path
for exact CPU parity. The simple parallel BFS path is safe only for no-dedupe
semantics and is not used for the release-facing comparison.

## Correctness Evidence

Local macOS import/discovery check:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal567_hiprt_prepared_graph_test
Ran 4 tests ... OK (skipped=4)
```

Linux HIPRT execution check:

```text
cd /tmp/rtdl_goal567_prepared_graph
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest tests.goal567_hiprt_prepared_graph_test tests.goal557_hiprt_bfs_test tests.goal558_hiprt_triangle_match_test
Ran 12 tests in 6.655s
OK
```

The tests verify:

- direct prepared graph CSR BFS parity against CPU across multiple frontier
  batches
- direct prepared graph CSR triangle-match parity against CPU across multiple
  seed batches
- high-level `rt.prepare_hiprt(...)` BFS parity
- high-level `rt.prepare_hiprt(...)` triangle-match parity
- existing one-shot HIPRT BFS and triangle-match tests still pass

## Linux Performance Evidence

Raw JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal567_hiprt_prepared_graph_perf_linux_2026-04-18.json`

Fixture:

- 512 vertices
- degree parameter `4`
- 4096 directed edges
- 128 BFS frontier rows
- 256 triangle seeds
- 5 prepared-query repeats

### BFS Discover

This BFS result uses `dedupe=True`, so it preserves deterministic CPU-compatible
global dedupe and remains serialized inside the HIPRT graph kernel.

| Path | Median seconds | Correct vs CPU |
|---|---:|---|
| CPU Python reference | 0.000722 | reference |
| Embree one-shot | 0.014502 | PASS |
| OptiX one-shot | 0.005469 | PASS |
| Vulkan one-shot | 0.002587 | PASS |
| HIPRT one-shot | 0.669876 | PASS |
| HIPRT prepare/build | 0.723796 | build phase |
| HIPRT prepared query | 0.020456 | PASS |

Computed one-shot HIPRT to prepared HIPRT query speedup:

```text
0.669876 / 0.020456 = 32.75x
```

### Triangle Match

Triangle-match now uses one GPU thread per seed.

| Path | Median seconds | Correct vs CPU |
|---|---:|---|
| CPU Python reference | 0.001850 | reference |
| Embree one-shot | 0.004035 | PASS |
| OptiX one-shot | 0.001827 | PASS |
| Vulkan one-shot | 0.001755 | PASS |
| HIPRT one-shot | 0.574389 | PASS |
| HIPRT prepare/build | 0.723796 | build phase |
| HIPRT prepared query | 0.002198 | PASS |

Computed one-shot HIPRT to prepared HIPRT query speedup:

```text
0.574389 / 0.002198 = 261.27x
```

## Interpretation

Prepared graph CSR reuse removes the repeated HIPRT setup/build/JIT cost from
graph workloads. Triangle-match additionally benefits from per-seed GPU
parallelism and is now close to the OptiX/Vulkan/CPU small-fixture timings after
preparation.

BFS remains slower than CPU/OptiX/Vulkan on this deterministic-dedupe fixture.
That is expected: exact global dedupe semantics are order-sensitive, and this
round chose correctness over a nondeterministic atomic race. A future BFS
optimization would need a deterministic two-pass or ordered reduction design.

## Honesty Boundary

This report does not claim:

- HIPRT graph is performance-leading on this fixture
- a full graph analytics system benchmark
- AMD GPU validation
- RT-core speedup evidence
- deterministic parallel BFS global dedupe

It does claim:

- prepared HIPRT graph CSR execution is correct for BFS and triangle-match on
  the Linux HIPRT/CUDA path
- prepared graph reuse materially reduces HIPRT repeated-query time compared
  with HIPRT one-shot execution
- triangle-match now uses a more parallel HIPRT query kernel

## Verdict

Goal 567 is technically implemented and Linux-validated for prepared graph CSR
reuse.

## AI Review Consensus

Review artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal567_external_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal567_gemini_flash_review_2026-04-18.md`

Claude returned `ACCEPT`, specifically confirming that deterministic BFS global
dedupe is correctly serialized for CPU parity, triangle-match dispatches one
GPU thread per seed, the performance numbers match the raw JSON, and the v0.9
docs are consistent. Gemini Flash also returned `ACCEPT`, confirming the same
correctness, boundary, performance-honesty, and documentation points. Codex
accepts the goal with the same bounded interpretation.
