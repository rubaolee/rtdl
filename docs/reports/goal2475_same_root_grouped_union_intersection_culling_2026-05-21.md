# Goal2475 - Same-root grouped-union intersection culling

Date: 2026-05-21

Status: pod validated on 2026-05-21. This is a generic OptiX fixed-radius
grouped-union continuation optimization candidate, not a DBSCAN-specific
native path. Internal pod evidence is positive, but public performance claims
remain blocked pending review/consensus.

## Purpose

Goal2473 showed that parent atomic attempts are only about 1.19x-1.23x per
point at benchmark scale, while native grouped-union time remains substantial.
That suggests many RT hits may reach anyhit even after the union-find structure
already connects their endpoints. Anyhit then performs a root check and returns
without a global atomic.

Goal2475 moves that no-op root check earlier for parent-union candidates:
after the exact radius test in the intersection program, read the current
union-find roots and skip `optixReportIntersection` when `source` and `target`
already have the same root.

## Change

The grouped-union intersection program now:

1. rejects predicate-impossible hits before distance work;
2. computes the exact fixed-radius distance;
3. for parent-union candidates only, checks current source/target union roots;
4. skips `optixReportIntersection` if the roots already match;
5. still reports fallback-candidate hits because fallback state is not a
   parent-union relation.

The anyhit program remains unchanged and keeps its root checks as a safety net.
Python metadata records:

```text
grouped_union_same_root_culling_policy = parent_union_same_root_before_anyhit
```

## Boundary

- No DBSCAN-specific native ABI or vocabulary was added.
- The primitive remains generic: fixed radius, predicate flags, parent union,
  fallback candidate, and same-root culling.
- Correctness relies on monotonic union-find connectivity: if two endpoints are
  already connected, skipping a later union for that hit cannot disconnect them.
- The change trades extra root reads in intersection for fewer anyhit
  callbacks. Pod timing below shows this tradeoff wins on the tested RTX A5000
  rows.
- Public performance claims remain blocked until external review/consensus.

## Pod Validation

An earlier pod endpoint
`ssh root@69.30.85.171 -p 22118 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex`
was checked after the local implementation and returned `Connection refused`.

The successful pod run used the user-provided endpoint with the local RTDL key
because `/Users/rl2025/.ssh/id_ed25519` was not present on this Mac:

```text
ssh root@69.30.85.177 -p 22181 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
host: ecdc0a16bb30
gpu: NVIDIA RTX A5000, driver 570.211.01
cuda nvcc: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX headers: NVIDIA/optix-dev v8.0.0
```

The pod tree was a filtered rsync of the local dirty Goal2467-2475 working
tree. Because `.git` was intentionally excluded from that pod sync, report JSON
`source_commit` fields are empty; the local base commit at sync time was
`a9193856547bf692069955a3dbaf6c3e00c09b1b`.

Focused tests passed on the pod:

```text
PYTHONPATH=src:. python -m unittest \
  tests.goal2475_same_root_grouped_union_intersection_culling_test \
  tests.goal2474_predicate_aware_grouped_union_intersection_culling_test \
  tests.goal2473_grouped_union_atomic_scale_telemetry_test \
  tests.goal2472_grouped_union_self_range_blocked_candidate_test \
  tests.goal2471_grouped_union_atomic_telemetry_test \
  tests.goal2470_grouped_continuation_segment_sensitivity_test \
  tests.goal2469_rt_dbscan_column_signature_mode_test \
  tests.goal2468_rt_dbscan_overhead_breakdown_instrumentation_test \
  tests.goal2467_blocked_grouped_continuation_design_test \
  tests.goal2465_grouped_union_all_items_intersection_cull_test \
  tests.goal2463_grouped_union_all_items_path_test \
  tests.goal2461_grouped_stream_self_query_device_path_test \
  tests.goal2459_grouped_stream_threshold_capped_core_flags_test \
  tests.goal2457_generic_grouped_stream_continuation_implementation_test
```

Result: 61 tests passed.

## Timing Results

The grouped-stream column-signature runner was executed with five repeats and
compared against the previous Goal2472 unblocked artifact on the same GPU
class. Values are tail medians after discarding repeat 1.

| points | Goal2472 total sec | Goal2475 total sec | total speedup | total reduction | Goal2472 grouped native sec | Goal2475 grouped native sec | native speedup | native reduction | signatures match |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 32,768 | 0.043300 | 0.041628 | 1.040x | 3.9% | 0.031052 | 0.025131 | 1.236x | 19.1% | true |
| 65,536 | 0.110211 | 0.098348 | 1.121x | 10.8% | 0.082476 | 0.066053 | 1.249x | 19.9% | true |

Artifacts:

```text
docs/reports/goal2475_same_root_culling_pod/
docs/reports/goal2475_same_root_culling_atomic_scale_pod.json
```

The follow-up Goal2471 telemetry scale run stayed sane:

| points | parent attempts | parent successes | attempts / point | baseline native sec | telemetry native sec |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32,768 | 42,037.5 | 32,763.0 | 1.2829 | 0.024749 | 0.024241 |
| 65,536 | 82,031.0 | 65,532.0 | 1.2517 | 0.067059 | 0.067185 |

Parent atomic attempts are slightly higher than Goal2473, but native time is
substantially lower. This supports the Goal2473 interpretation: the useful
target was reducing anyhit/reporting work, not only lowering global atomic
attempt counts.

## Replay Commands

The pod validation sequence was:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev-8.0.0 CUDA_PREFIX=/usr/local/cuda-12.8
```

```text
PYTHONPATH=src:. python scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --signature-mode column \
  --repeat-count 5 \
  --output-dir docs/reports/goal2475_same_root_culling_pod
```

```text
PYTHONPATH=src:. python scripts/goal2473_grouped_union_atomic_scale_pod_runner.py \
  --repeat-count 3 \
  --output docs/reports/goal2475_same_root_culling_atomic_scale_pod.json
```

## External Review

Gemini reviewed the code, report, and pod artifacts:

```text
docs/reviews/goal2475_gemini_review_same_root_culling_pod_2026-05-21.md
```

Verdict: approved, no blocking or nonblocking issues.

The Codex/Gemini consensus is recorded in:

```text
docs/reviews/goal2475_codex_gemini_consensus_same_root_culling_pod_2026-05-21.md
```
