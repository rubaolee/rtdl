# Goal 571: RTXRMQ Paper Workload Inclusion and Engine Comparison

Date: 2026-04-18

## Verdict

ACCEPT as a final pre-release workload gate with an explicit honesty boundary.

RTDL v0.9 can run and compare a paper-derived RMQ traversal subworkload across Embree, OptiX, Vulkan, and HIPRT. RTDL v0.9 does not yet implement full RTXRMQ, because full RTXRMQ requires a closest-hit/argmin result that returns the hit element id/value, while the current public RTDL surface exposes `ray_triangle_hit_count`.

## Paper

- Local file: `/Users/rl2025/Downloads/2306.03282v1.pdf`
- arXiv id: `2306.03282v1`
- Title: `Accelerating Range Minimum Queries with Ray Tracing Cores`

The paper maps array elements to YZ-aligned triangles positioned by value and shaped by index range. A query `RMQ(l,r)` becomes a +X ray launched from the `(l,r)` query coordinates; the closest hit corresponds to the minimum element in the requested range.

## What Was Implemented

Goal 571 adds a bounded paper-derived workload:

- Exact CPU RMQ oracle: computes `argmin(values[l:r+1])`.
- RTDL traversal analogue: one YZ-aligned triangle per array element, one +X ray per query range, and a threshold coordinate derived from the exact RMQ value.
- Output: `hit_count`, the number of elements in `[l,r]` with value at or below the threshold.
- Engine comparison: CPU Python reference, Embree, OptiX, Vulkan, HIPRT one-shot, and HIPRT prepared.

This tests the same core mapping family used by the paper: array elements become triangles, query ranges become rays, and the backend performs ray/triangle traversal. It is not full RMQ because it does not return the closest hit element.

## Files

- Script: `/Users/rl2025/rtdl_python_only/scripts/goal571_rtxrmq_paper_workload_perf.py`
- Tests: `/Users/rl2025/rtdl_python_only/tests/goal571_rtxrmq_paper_workload_test.py`
- Discovery wrapper: `/Users/rl2025/rtdl_python_only/tests/test_goal571_rtxrmq_paper_workload.py`
- Linux JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal571_rtxrmq_paper_workload_engine_compare_linux_2026-04-18.json`
- Local smoke JSON: `/Users/rl2025/rtdl_python_only/docs/reports/goal571_rtxrmq_paper_workload_engine_compare_local_smoke_2026-04-18.json`

## Correctness Evidence

Local macOS:

```text
python3 -m unittest tests.goal571_rtxrmq_paper_workload_test
Ran 3 tests in 0.001s
OK
```

Linux:

```text
python3 -m unittest tests.goal571_rtxrmq_paper_workload_test
Ran 3 tests in 0.002s
OK
```

Post-wrapper normal discovery:

```text
macOS: python3 -m unittest discover -s tests
Ran 235 tests in 61.399s
OK

Linux: python3 -m unittest discover -s tests
Ran 235 tests in 142.865s
OK
```

The Linux performance script also checked every backend result against the threshold-count oracle:

```text
cpu_python_reference matches_threshold_oracle: true
embree matches_threshold_oracle: true
optix matches_threshold_oracle: true
vulkan matches_threshold_oracle: true
hiprt_one_shot matches_threshold_oracle: true
hiprt_prepared matches_threshold_oracle: true
```

## Linux Performance Result

Host:

- Hostname: `lx1`
- Platform: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Python: `3.12.3`
- GPU: `NVIDIA GeForce GTX 1070, driver 580.126.09`
- Embree: `4.3.0`
- OptiX: `9.0.0`
- Vulkan RTDL backend: `0.1.0`
- HIPRT: `2.2.15109972`

Case:

- Values: `4096`
- Triangles: `4096`
- Queries/rays: `2048`
- Max query range: `128`
- Iterations per backend: `3`

| Backend | Median seconds | Correct | Notes |
|---|---:|---|---|
| CPU Python reference | `5.121054` | yes | Direct Python reference path, not a performance target. |
| Embree | `0.005303` | yes | Fastest one-shot backend in this run. |
| OptiX | `0.052339` | yes | Includes one-shot setup/launch overhead. |
| Vulkan | `0.057575` | yes | Includes one-shot setup/launch overhead. |
| HIPRT one-shot | `0.548895` | yes | Includes one-shot HIPRT setup/build overhead. |
| HIPRT prepared query | `0.004217` | yes | Query-only timing after `0.526239s` prepare/build. |

Derived ratios:

- Embree vs CPU Python reference: about `966x` faster.
- OptiX vs CPU Python reference: about `98x` faster.
- Vulkan vs CPU Python reference: about `89x` faster.
- HIPRT one-shot vs CPU Python reference: about `9.3x` faster.
- HIPRT prepared query vs CPU Python reference: about `1214x` faster.
- HIPRT prepared query vs HIPRT one-shot: about `130x` faster, after paying prepare/build once.

## External Review

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal571_external_review_2026-04-18.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal571_gemini_flash_review_2026-04-18.md`

Both reviews returned `ACCEPT`.

## Interpretation

This is a useful pre-release workload gate because it adds a new paper-inspired ray/triangle traversal pattern and verifies that all four native engines produce identical results on Linux.

This is not a full reproduction of the paper's RTXRMQ algorithm. Full RTXRMQ requires a closest-hit/argmin primitive that emits the nearest hit element id and value. RTDL v0.9 currently has enough language/runtime surface for the traversal-count analogue, but not for exact closest-hit RMQ.

The GTX 1070 host has no hardware RT cores, so these numbers must not be described as RT-core acceleration. They are backend/runtime comparisons for the current Linux validation host.

## Follow-Up Candidate

If this paper becomes a v0.10 target, the first implementable language/runtime extension should be:

```python
hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(payload=("triangle_id", "value")))
return rt.emit(hits, fields=["ray_id", "triangle_id", "value", "t"])
```

That would allow RTDL to express exact RTXRMQ instead of the threshold-count subworkload.
