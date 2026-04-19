# Goal 571 External Review: RTXRMQ Paper Workload Inclusion

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-04-18  
**Verdict:** ACCEPT

---

## Summary

Goal 571 honestly includes the RTXRMQ paper (arXiv 2306.03282v1, "Accelerating Range Minimum Queries with Ray Tracing Cores") as a bounded v0.9 pre-release gate. It does not overclaim full closest-hit RMQ support. All four native engines produce correct results on Linux.

---

## Honesty Boundary: Pass

The implementation is explicit and consistent about the scope limitation across every artifact:

- **Report** (`goal571_rtxrmq_paper_workload_engine_compare_2026-04-18.md`): States plainly that "This is not a full reproduction of the paper's RTXRMQ algorithm. Full RTXRMQ requires a closest-hit/argmin primitive that emits the nearest hit element id and value."
- **JSON output** (`goal571_rtxrmq_paper_workload_engine_compare_linux_2026-04-18.json`): Contains a top-level `honesty_boundary` field embedded in the data record itself, so the boundary travels with the results.
- **Script** (`goal571_rtxrmq_paper_workload_perf.py`): The kernel is named `rtxrmq_threshold_hitcount_kernel`, not `rtxrmq_kernel`. The workload name in the JSON is `rtxrmq_range_threshold_hitcount_analogue`. These names correctly signal that this is a subworkload, not the full algorithm.
- **GTX 1070 disclaimer**: The report notes that the Linux validation host has no hardware RT cores, so performance numbers must not be attributed to RT-core acceleration. This is correct and important.

---

## Paper Mapping Fidelity: Pass

The paper maps array elements to YZ-aligned triangles (positioned by value, shaped by index range) and each `RMQ(l,r)` query to a +X ray. Goal 571 faithfully reproduces this geometric mapping:

- One YZ-aligned `Triangle3D` per element, with X-position = element index, Y-floor = element value.
- One +X `Ray3D` per query, with origin at `(left - 0.5, threshold, 0.0)` and `tmax = right - left + 1`.

The mapping is paper-faithful. The departure from the paper is the output: instead of returning the closest-hit element (argmin), the kernel returns `hit_count` — the number of elements in `[l,r]` at or below a threshold derived from the exact CPU RMQ answer. This is a well-defined, verifiable analogue, not a guess or approximation of what the paper does.

---

## Correctness: Pass

### CPU oracle
`exact_rmq_cpu` correctly implements argmin over `values[l:r+1]`. The test case `(9,2,7,8,4,1,3)` with queries `(2,6),(0,1),(5,5)` is verified against ground truth in `test_exact_cpu_rmq_matches_paper_definition`.

### Threshold oracle agreement
`test_threshold_hitcount_geometry_matches_threshold_oracle` confirms that the ray/triangle geometry produces the same hit counts as the direct Python threshold counter. The raw CPU ray-triangle reference also matches (`matches_direct_cpu_ray_triangle_reference: true` in the JSON).

### All-backend correctness on Linux
Every backend in the Linux run reports `matches_threshold_oracle: true`:

| Backend | Correct |
|---|---|
| cpu_python_reference | yes |
| embree | yes |
| optix | yes |
| vulkan | yes |
| hiprt_one_shot | yes |
| hiprt_prepared | yes |

### Test suite
Three unit tests pass on both macOS and Linux (`Ran 3 tests in 0.001–0.002s, OK`).

---

## Performance Results: Plausible

| Backend | Median (s) | vs. CPU Python |
|---|---:|---:|
| CPU Python reference | 5.121 | 1× |
| Embree | 0.00530 | ~966× |
| OptiX | 0.0523 | ~98× |
| Vulkan | 0.0576 | ~89× |
| HIPRT one-shot | 0.549 | ~9.3× |
| HIPRT prepared query | 0.00422 | ~1,214× |

The HIPRT prepared/one-shot split (0.526 s build, 0.004 s query) is consistent with HIPRT's BVH construction cost being amortized across queries. The Embree lead over OptiX and Vulkan at this scale (4096 triangles, 2048 rays) is plausible given Embree's low setup overhead compared to GPU dispatch latency. No numbers are misrepresented.

---

## Follow-Up Path: Correctly Identified

The report correctly names the extension needed for full RTXRMQ:

```python
hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(payload=("triangle_id", "value")))
return rt.emit(hits, fields=["ray_id", "triangle_id", "value", "t"])
```

This is an accurate description of what is missing: a public closest-hit primitive that returns the hit element id and value. Deferred to v0.10 is the right call.

---

## Issues: None

No correctness issues, no overclaiming, no missing honesty disclosures, no geometric mapping errors.

---

## Verdict: ACCEPT

Goal 571 is a sound, honest, bounded paper-derived pre-release gate for v0.9. The RTXRMQ traversal subworkload is implemented correctly, all four native engines agree on Linux, and the scope boundary (threshold hit-count analogue, not full closest-hit RMQ) is stated clearly in the report, the JSON, and the naming conventions throughout the code.
