# Goal2475 Codex/Gemini Consensus - Same-Root Grouped-Union Culling

Date: 2026-05-21

Consensus participants:

- Codex implementation and pod validation.
- Gemini review:
  `docs/reviews/goal2475_gemini_review_same_root_culling_pod_2026-05-21.md`.

## Decision

Goal2475 is accepted as a correct and beneficial internal engineering
optimization for the generic OptiX fixed-radius grouped-union continuation path
on the tested RTX A5000 rows.

The accepted change is generic:

```text
grouped_union_same_root_culling_policy = parent_union_same_root_before_anyhit
```

The intersection program skips `optixReportIntersection` for parent-union
candidates when the current union-find roots already match. This avoids anyhit
callbacks that cannot change connectivity. The anyhit path keeps its safety
checks.

## Evidence

Pod endpoint:

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

Focused Goal2457-2475 tests passed on the pod: 61 tests OK.

Compared with the previous Goal2472 unblocked baseline:

| points | Goal2472 total sec | Goal2475 total sec | total speedup | Goal2472 grouped native sec | Goal2475 grouped native sec | native speedup | signatures match |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 32,768 | 0.043300 | 0.041628 | 1.040x | 0.031052 | 0.025131 | 1.236x | true |
| 65,536 | 0.110211 | 0.098348 | 1.121x | 0.082476 | 0.066053 | 1.249x | true |

Telemetry remained sane:

| points | parent attempts | parent successes | attempts / point |
| ---: | ---: | ---: | ---: |
| 32,768 | 42,037.5 | 32,763.0 | 1.2829 |
| 65,536 | 82,031.0 | 65,532.0 | 1.2517 |

Artifacts:

```text
docs/reports/goal2475_same_root_grouped_union_intersection_culling_2026-05-21.md
docs/reports/goal2475_same_root_culling_pod/
docs/reports/goal2475_same_root_culling_atomic_scale_pod.json
```

## Boundary

No DBSCAN-specific native ABI, constants, or vocabulary were introduced. The
optimization remains a generic fixed-radius grouped-union continuation culling
policy.

Public performance wording remains unauthorized. This consensus authorizes the
internal engineering direction and integration of the generic same-root culling
candidate, not a public speedup claim.

## Next Step

Proceed with internal integration and then evaluate the next scale-up or
broader grouped-union workload matrix. Any public performance statement still
needs the normal reviewed wording and release-claim process.
