# Goal603: v0.9.3 Apple RT Native-Coverage Contract

Date: 2026-04-19

Status: accepted with 3-AI consensus

## Scope

Goal603 implements the first v0.9.3 step from Goal602: make the Apple RT
support matrix precise enough to separate:

- native Apple Metal/MPS RT candidate discovery
- shape-dependent native support
- CPU-reference compatibility dispatch
- CPU refinement after native candidate discovery

No new workload is marked native in this goal. This is a contract hardening
goal, not a coverage-expansion goal.

## Code Changes

Updated:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`

Added:

- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`

`rt.apple_rt_support_matrix()` now returns one row per current predicate with:

- `predicate`
- `mode`
- `native_candidate_discovery`
- `cpu_refinement`
- `native_only`
- `native_shapes`
- `notes`

## Current Contract

Native or shape-dependent rows:

| Predicate | Native candidate discovery | Native shapes | CPU refinement |
| --- | --- | --- | --- |
| `ray_triangle_closest_hit` | `yes` | `Ray3D/Triangle3D` | `row_materialization_only` |
| `ray_triangle_hit_count` | `shape_dependent` | `Ray3D/Triangle3D` | `count_accumulation` |
| `segment_intersection` | `yes` | `Segment2D/Segment2D` | `exact_intersection_point` |

All other current predicates remain:

- `native_candidate_discovery`: `no`
- `cpu_refinement`: `full_cpu_reference_compat`
- `native_only`: `unsupported_until_v0_9_3_native_lowering`
- `native_shapes`: `()`

This keeps the v0.9.3 honesty boundary machine-checkable: a future workload is
not hardware-backed until the matrix row changes and `native_only=True` succeeds
with parity tests.

## Validation

Targeted command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Actual result:

```text
Ran 8 tests in 0.017s
OK
```

Additional checks:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py tests/goal603_apple_rt_native_contract_test.py
git diff --check
```

Both completed with no output.

## Verdict

Codex verdict: ACCEPT as a contract-hardening step.

This goal deliberately does not claim new Apple RT hardware coverage. It makes
the remaining v0.9.3 implementation goals harder to overclaim.

External consensus:

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal603_external_review_2026-04-19.md` verdict ACCEPT.
- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal603_gemini_review_2026-04-19.md` verdict ACCEPT.
