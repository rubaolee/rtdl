# Goal 636: v0.9.5 Backend Any-Hit Compatibility And User Doubt Log

Date: 2026-04-19

## Goal

Extend the new `rt.ray_triangle_any_hit(exact=False)` feature beyond the
CPU/oracle contract so real RTDL backends can execute kernels using this
predicate:

- Embree
- OptiX
- Vulkan
- HIPRT
- Apple Metal/MPS RT

Also expose `visibility_rows(..., backend=...)` so the visibility-row standard
library helper can use the same backend any-hit compatibility dispatch.

## User Doubt Recorded

The user explicitly challenged the first backend strategy:

> You are just using existing way to know the hit count, then judge it is >0
> or not?

This concern is correct and must remain part of the release record.

## Engineering Decision

For Goal 636, the backend implementation is a **compatibility dispatch**, not a
native early-exit performance implementation.

The current backend logic is:

```text
backend ray_triangle_hit_count traversal
  -> row {ray_id, hit_count}
  -> project to {ray_id, any_hit = hit_count > 0}
```

This means:

- the traversal is still executed by the selected backend;
- the result schema matches `ray_triangle_any_hit`;
- backend parity can be tested against the CPU/oracle result;
- the implementation does **not** stop traversal on the first accepted hit;
- the implementation must not be used to claim any any-hit speedup.

## Honesty Boundary

Allowed claim:

> `ray_triangle_any_hit` can run through Embree, OptiX, Vulkan, HIPRT, and
> Apple RT compatibility dispatch by projecting each backend's existing
> ray-triangle hit-count result to a boolean `any_hit` row.

Disallowed claim:

> These backends now implement optimized native early-exit any-hit traversal.

Disallowed claim:

> Goal 636 proves performance benefit from any-hit.

## Why This Step Still Matters

This compatibility step is useful because it makes the feature runnable through
the same public backend dispatcher surface as other RTDL kernels. It also gives
a low-risk correctness gate before adding backend-specific native early-exit
shader/kernel work.

## Next Required Goal

The real performance goal must be separate:

```text
Goal 637: native early-exit any-hit kernels
```

Goal 637 should implement and test backend-specific first-hit termination where
the backend API supports it, then compare against hit-count projection and CPU
reference results.

## Current Local Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal636_backend_any_hit_dispatch_test -v
```

Result:

```text
Ran 5 tests
OK (skipped=3)
```

Local Mac evidence:

- Embree any-hit compatibility dispatch matches CPU and prepared dispatch.
- Apple RT `native_only=True` any-hit compatibility dispatch matches CPU for
  2D and 3D.
- `visibility_rows(..., backend="embree")` matches `visibility_rows_cpu`.
- `visibility_rows(..., backend="apple_rt", native_only=True)` matches
  `visibility_rows_cpu`.
- OptiX, Vulkan, and HIPRT skip locally because this Mac checkout does not have
  those runtime libraries available.

## Linux Backend Validation

Host:

```text
lestat-lx1
NVIDIA GeForce GTX 1070, 8192 MiB
Python 3.12.3
```

Synced checkout:

```text
/tmp/rtdl_goal636_anyhit
```

Backend build commands:

```bash
make build-embree
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
make build-hiprt
```

Focused backend command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal636_backend_any_hit_dispatch_test -v
```

Result:

```text
Ran 7 tests in 6.651s
OK (skipped=2)
```

Linux backend evidence:

- Embree any-hit compatibility dispatch matches CPU.
- OptiX any-hit compatibility dispatch matches CPU.
- Vulkan any-hit compatibility dispatch matches CPU.
- HIPRT any-hit compatibility dispatch matches CPU for 2D and 3D.
- `visibility_rows(..., backend="embree")` matches `visibility_rows_cpu`.
- Apple RT tests skip on Linux, as expected.

Combined v0.9.5 focused Linux command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal632_ray_triangle_any_hit_test tests.goal633_visibility_rows_test tests.goal636_backend_any_hit_dispatch_test -v
```

Result:

```text
Ran 16 tests in 1.705s
OK (skipped=2)
```

## External Review

Review file:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal636_external_review_2026-04-19.md
```

Verdict:

```text
ACCEPT
```

Reviewer conclusion:

- The user's doubt is correctly recorded.
- The implementation is honestly documented as hit-count projection
  compatibility.
- No native early-exit or performance claim is made.
- Goal 637 is the right place for true backend-native early-exit kernels.

## Status

ACCEPTED as a compatibility/backend-parity goal.

This does not close native early-exit performance work.

## Post-Fix Local Regression

After adding `ray_triangle_any_hit` to the Apple RT support matrix, the full
suite initially exposed three stale Apple support-matrix expectations that
still assumed 18 predicates. Those tests were updated to expect 19 predicates
and to assert the any-hit projection boundary explicitly.

Final local command:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result:

```text
Ran 1194 tests in 106.585s
OK (skipped=174)
```

Public doc/command audit commands:

```bash
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Results:

```text
goal497 valid: true
goal515 valid: true, command_count: 244, public_doc_count: 14
```
