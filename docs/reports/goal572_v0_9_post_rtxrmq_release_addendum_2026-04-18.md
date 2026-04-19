# Goal 572: v0.9 Post-RTXRMQ Release Addendum

Date: 2026-04-18

## Verdict

ACCEPT. v0.9 remains release-ready after adding the RTXRMQ paper-derived workload gate.

## Why This Addendum Exists

Goal 570 was the prior final pre-release test/doc/audit gate. After that gate, `/Users/rl2025/Downloads/2306.03282v1.pdf` was added as a final release-blocking workload check. Goal 571 therefore became a new mandatory addendum before release.

## Added Workload Gate

Goal 571 covers the paper `Accelerating Range Minimum Queries with Ray Tracing Cores`.

RTDL v0.9 now includes:

- Exact CPU RMQ oracle for the paper definition.
- RTDL paper-derived range-threshold traversal workload using YZ-aligned triangles and +X query rays.
- Engine comparison on Linux across CPU Python reference, Embree, OptiX, Vulkan, HIPRT one-shot, and HIPRT prepared.
- Explicit honesty boundary that this is not full RTXRMQ because v0.9 lacks public closest-hit/argmin emission.

Primary report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal571_rtxrmq_paper_workload_engine_compare_2026-04-18.md`

## Final Test Evidence After Goal 571

Focused Goal 571 tests:

```text
macOS: python3 -m unittest tests.goal571_rtxrmq_paper_workload_test
Ran 3 tests in 0.001s
OK

Linux: python3 -m unittest tests.goal571_rtxrmq_paper_workload_test
Ran 3 tests in 0.002s
OK
```

Normal discovery after adding `/Users/rl2025/rtdl_python_only/tests/test_goal571_rtxrmq_paper_workload.py`:

```text
macOS: python3 -m unittest discover -s tests
Ran 235 tests in 61.399s
OK

Linux: python3 -m unittest discover -s tests
Ran 235 tests in 142.865s
OK
```

Linux engine comparison:

- JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal571_rtxrmq_paper_workload_engine_compare_linux_2026-04-18.json`
- All compared backends matched the threshold oracle.

| Backend | Median seconds | Correct |
|---|---:|---|
| CPU Python reference | `5.121054` | yes |
| Embree | `0.005303` | yes |
| OptiX | `0.052339` | yes |
| Vulkan | `0.057575` | yes |
| HIPRT one-shot | `0.548895` | yes |
| HIPRT prepared query | `0.004217` | yes |

## Consensus

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal571_external_review_2026-04-18.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal571_gemini_flash_review_2026-04-18.md`
- Goal 572 Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal572_external_review_2026-04-18.md`
- Goal 572 Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal572_gemini_flash_review_2026-04-18.md`

Goal 571 and Goal 572 reviews accepted this as an honest bounded pre-release gate and confirmed that v0.9 remains release-ready.

## Release Impact

No release blocker was introduced.

The only new limitation to carry forward is a future feature candidate: exact RTXRMQ should be implemented through a public closest-hit/argmin primitive, not by stretching `ray_triangle_hit_count` beyond its actual semantics.
