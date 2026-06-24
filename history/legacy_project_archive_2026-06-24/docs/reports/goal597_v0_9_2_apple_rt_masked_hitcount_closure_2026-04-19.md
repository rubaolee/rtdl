# Goal597: v0.9.2 Apple RT Masked Hit-Count Closure

Date: 2026-04-19

Status: ACCEPT

## Scope

Goal597 replaces the Apple RT 3D `ray_triangle_hit_count` implementation's
one-triangle acceleration-structure loop with the reviewed masked chunked
nearest-hit strategy.

The implementation remains exact for the tested RTDL contract and keeps the
same public Python API:

```python
tuple(rt.ray_triangle_hit_count_apple_rt(rays, triangles))
rt.run_apple_rt(hit_count_kernel, native_only=True, rays=rays, triangles=triangles)
```

## Design Gate

Design note:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal597_v0_9_2_apple_rt_hitcount_design_note_2026-04-19.md
```

External design review:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal597_design_external_review_2026-04-19.md
```

Design verdict: ACCEPT.

## Implementation

Changed file:

```text
/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm
```

The new native strategy:

- partitions triangles into chunks of at most 32 primitives,
- builds one MPS triangle acceleration structure per chunk,
- assigns one primitive-mask bit per triangle inside that chunk,
- uses `MPSRayDataTypeOriginMaskDirectionMaxDistance`,
- enables `MPSRayMaskOptionPrimitive`,
- runs nearest-hit traversal with primitive index,
- clears the hit primitive bit from the per-ray mask,
- repeats until no hits remain or all chunk bits are cleared.

No distance epsilon is used for correctness.

## Correctness Tests

New test file:

```text
/Users/rl2025/rtdl_python_only/tests/goal597_apple_rt_masked_hitcount_test.py
```

Focused verification:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal597_apple_rt_masked_hitcount_test tests.goal578_apple_rt_backend_test -v
```

Result:

```text
Ran 9 tests in 0.284s
OK
```

Coverage includes:

- stacked same-distance triangles,
- more than 32 triangles to force multiple chunks,
- miss ray,
- invalid zero-direction ray,
- parity against `ray_triangle_hit_count_cpu`.

## Performance Artifact

Post-change artifact:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal597_post_masked_hitcount_perf_macos_2026-04-19.json
/Users/rl2025/rtdl_python_only/docs/reports/goal597_post_masked_hitcount_perf_macos_2026-04-19.md
```

Dense 128-ray / 512-triangle hit-count fixture:

| Metric | Value |
| --- | ---: |
| Embree median | 0.002508270 s |
| Apple RT masked median | 0.329233396 s |
| Apple / Embree median ratio | 131.259x |
| Apple RT CV | 0.171 |
| Parity | true |
| Stability threshold pass | false |

Compared with the Goal595 5-warmup/20-repeat baseline for the same dense
fixture:

| Metric | Goal595 baseline | Goal597 masked |
| --- | ---: | ---: |
| Apple RT median | 0.417264375 s | 0.329233396 s |
| Apple / Embree ratio | 169.243x | 131.259x |

Interpretation: the masked chunked strategy is a correctness-preserving
improvement and reduces AS rebuild pressure, but dense all-hit workloads still
require many nearest-hit dispatches. It is not a public speedup claim.

## Consensus

Codex verdict: ACCEPT. The implementation follows the accepted design, passes
targeted correctness fixtures that the naive epsilon approach would risk
failing, and improves the dense benchmark modestly while preserving the Apple RT
honesty boundary.

External implementation review:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal597_implementation_external_review_2026-04-19.md
```

External verdict: ACCEPT. The reviewer confirmed the chunked masked nearest-hit
strategy, the >32 triangle and stacked-primitive tests, and the bounded
performance interpretation.
