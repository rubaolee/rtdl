# Goal2141: RTDL Hausdorff Application Acceleration Synthesis

Date: 2026-05-16

Status: round complete, with bounded acceptance

## Bottom Line

This round is enough to make a strong, precise statement:

RTDL v2 can express a real exact Hausdorff-distance application in Python, keep the RTDL native engine app-agnostic, and use generic OptiX/RT traversal to beat an optimized grouped CuPy baseline on substantial public graphics and geo point-set workloads.

It is not enough to claim full X-HD paper reproduction, full 3D surface Hausdorff, all MRI/BraTS workloads, all geographic polygon semantics, or universal CUDA-vs-RT speedup.

## What Was Built

The user-level program computes exact 2D projected-point Hausdorff distance. It uses X-HD ideas as an application policy, not as native engine customization:

- seed an initial exact lower bound from a deterministic sample;
- use a generic point-group threshold traversal to mark source points that cannot beat the current maximum;
- run exact nearest-witness reduction only on unresolved candidates;
- preserve a grouped CuPy raw-kernel path as the fairness baseline;
- preserve exactness by comparing the RTDL/OptiX distance against the grouped CuPy distance in every artifact row.

The engine contribution is generic:

- point-group threshold flags;
- point-group nearest-witness reduction;
- vectorized host point packing.

The Hausdorff-specific choices remain in Python.

## Evidence Set

| Goal | Dataset lane | Scale | Result | Review |
| --- | --- | --- | --- | --- |
| Goal2132 | Stanford Dragon/Happy projected XY controls | ~438k points | 6.10x to 6.38x best-vs-best over grouped CuPy | Goal2133 Gemini `accept` / `accept-with-boundary` |
| Goal2134 | X-HD graphics model names, public Stanford sources | 262k and 437k/524k effective points | 4.08x to 8.66x best-vs-best over grouped CuPy | Goal2135 Gemini `accept` |
| Goal2136 | X-HD graphics dense stress | 437k and 1,048,576 effective points | 8.26x to 13.93x over grouped CuPy | Goal2137 Gemini `accept` |
| Goal2139 | Public geo analogues for X-HD WKT lane | 131k/262k Census; 131k/162k Natural Earth | Census 6.84x to 12.49x; Natural Earth 1.20x to 1.48x | Goal2140 Gemini `accept` |

Across these reports, 52 measured artifact rows matched grouped CuPy correctness within the harness tolerance.

## Headline Performance

| Lane | Strongest row | Grouped CuPy | RTDL/OptiX | Speedup |
| --- | --- | ---: | ---: | ---: |
| Stanford control | Dragon vs Happy XY | 3.417380 s | 0.535331 s | 6.38x |
| X-HD graphics | Dragon vs Happy Buddha, 437k, group 4096 | 5.592102 s | 0.591490 s | 9.45x |
| X-HD graphics dense stress | Thai Statuette vs Asian Dragon, 1M, group 8192 | 17.380398 s | 1.248008 s | 13.93x |
| Public geo detailed | Census counties vs ZCTA, 262k, group 1024 | 3.760128 s | 0.301055 s | 12.49x |
| Public geo sparse | Natural Earth lakes vs parks, 162k, group 2048 | 0.113681 s | 0.076850 s | 1.48x |

The sparse Natural Earth row is intentionally included because it keeps the story honest. RTDL/OptiX still wins, but only modestly, because the workload is too small and sparse for RT traversal to dominate fixed overhead.

## Why This Matters For RTDL As A Language/Runtime

The result is not merely "one optimized benchmark." It shows the intended v2 programming model working:

1. The user writes domain logic in Python.
2. The user uses partner compute, here CuPy, for fairness baselines and GPU-side ordinary work.
3. The user calls RTDL for the part that maps well to generic RT traversal.
4. The RTDL engine stays app-agnostic.
5. The same app-level policy works across graphics and geo data without adding Hausdorff-specific native exports.

That is the core language/runtime claim: RTDL gives Python programs access to RT-style traversal primitives that ordinary tensor libraries do not expose, while still interoperating with those tensor libraries.

## What We Learned

The wins appear when the app has enough candidate geometry for pruning and nearest-witness reduction to dominate overhead:

- dense graphics pairs improve as the sample size grows;
- detailed Census/ZCTA geo vertices show strong speedup;
- sparse Natural Earth data is correct but near overhead parity.

The key performance fix was not a Hausdorff-specific kernel. The decisive changes were generic:

- a reusable threshold-mask primitive;
- exact witness reduction over point groups;
- vectorized point packing so Python/ctypes conversion no longer erases the RT traversal win.

## Claim Boundary

| Claim | Verdict |
| --- | --- |
| This round is enough to close the current exact 2D projected-point Hausdorff acceleration test | `accept` |
| RTDL/OptiX beats optimized grouped CuPy on the measured A5000 dense graphics and detailed geo rows | `accept-with-boundary` |
| RTDL engine remains app-agnostic for this work | `accept` |
| RTDL can support real Python applications that combine partner compute and RT traversal | `accept-with-boundary` |
| RTDL universally beats all possible CUDA implementations | `not-claimed` |
| Full X-HD paper reproduction | `not-claimed` |
| Full 3D surface Hausdorff | `not-claimed` |
| MRI/BraTS X-HD reproduction | `not-claimed` |
| Original X-HD local WKT files reproduced exactly | `not-claimed` |
| Full geographic polygon/surface Hausdorff semantics | `not-claimed` |
| v2.0 release authorization | `not-authorized-here` |

## Recommendation

Close this Hausdorff test-and-comparison round as successful.

Use the result as a v2.0 application case study:

- "RTDL v2 lets Python users combine partner GPU code with generic RT traversal."
- "On dense public point-set Hausdorff workloads, RTDL/OptiX can outperform optimized grouped CuPy by 6x to 14x on an RTX A5000."
- "The strongest wins come from dense candidate geometry; sparse rows may be overhead-limited."

Keep MRI/BraTS, original X-HD WKT files, and full 3D surface Hausdorff as future validation lanes rather than blockers for this completed round.

## Artifact Index

- `docs/reports/goal2132_xhd_seeded_pruned_packfast_a5000_perf_2026-05-16.md`
- `docs/reports/goal2134_xhd_graphics_dataset_perf_2026-05-16.md`
- `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md`
- `docs/reports/goal2139_public_geo_hausdorff_perf_2026-05-16.md`
- `docs/reviews/goal2133_gemini_review_goal2131_2132_xhd_packfast_hd_2026-05-16.md`
- `docs/reviews/goal2135_gemini_review_goal2134_xhd_graphics_hd_perf_2026-05-16.md`
- `docs/reviews/goal2137_gemini_review_goal2136_dense_xhd_graphics_stress_2026-05-16.md`
- `docs/reviews/goal2140_gemini_review_goal2139_public_geo_hd_perf_2026-05-16.md`
