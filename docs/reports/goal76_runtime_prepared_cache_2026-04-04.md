# Goal 76: Runtime Prepared-Execution Cache

## Summary

Goal 76 adds an in-process prepared-execution cache to the RTDL Embree, OptiX, and Vulkan runtimes. The cache is used only for repeated identical raw-input calls. Packed-input calls continue to bypass the cache.

This is a compiler/runtime-owned optimization step. It keeps the authored RTDL surface unchanged and moves a useful repeated-call optimization into runtime policy.

## Code Surface

- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal76_runtime_prepared_cache_test.py`

## Design

Each runtime now maintains a small LRU cache of prepared executions.

Cache key components:

- compiled kernel name
- backend
- precision
- predicate name
- predicate options
- input signature
- emitted fields
- normalized logical inputs

Cache policy:

- raw logical inputs are normalized and become eligible for reuse
- already packed inputs bypass the cache
- cache is bounded to a small in-process LRU window
- explicit cache-clear helpers exist for tests

## Evidence

Local validation:

- `python3 -m py_compile src/rtdsl/embree_runtime.py src/rtdsl/optix_runtime.py src/rtdsl/vulkan_runtime.py tests/goal76_runtime_prepared_cache_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal76_runtime_prepared_cache_test`
- `PYTHONPATH=src:. python3 -m unittest tests.goal71_prepared_backend_positive_hit_county_test`

Observed results:

- Goal 76 cache test: `4` tests, `OK`
- Goal 71 prepared-backend selector regression test: `3` tests, `OK`

## Accepted Claim

RTDL now automatically reuses prepared executions for repeated identical raw-input calls on Embree, OptiX, and Vulkan, without changing RTDL program semantics.

## Boundaries

- This goal is not a new benchmark claim.
- This goal does not claim a specific end-to-end speedup number.
- This goal does not alter full-matrix or positive-hit workload semantics.
- This goal does not change the truth-oracle hierarchy.
