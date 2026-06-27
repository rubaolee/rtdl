# Goal 44 Report: Remote OptiX Performance & Large-Scale Validation

Date: 2026-04-02

## Summary

Goal 44 established a large-scale performance baseline for the OptiX backend on the remote host `192.168.1.20`. Using a synthetic Point-in-County join workload, the OptiX backend demonstrated significant speedups over the Embree (CPU) reference on matched hardware.

This is a bounded synthetic benchmark, not yet an exact-source RayJoin-family GPU reproduction.

## Environment

- **Host:** `192.168.1.20` (Ubuntu 24.04, GTX 1070)
- **CPU Backend:** Embree 4.3.0
- **GPU Backend:** OptiX 9.0.0
- **PTX Compiler:** `nvcc` fallback

## Performance Results

Workload: **Point-in-Polygon (PIP)**
Dataset: **US County Feature Layer** (Staged) + Synthetic Points

| Metric | Scale: Smoke (10 features) | Scale: Med (250 features) |
| :--- | :--- | :--- |
| **Polygons** | 25 | 1,016 |
| **Points** | 10,000 | 10,000 |
| **Total Intersections** | 250,000 | 10,160,000 |
| **Embree (CPU) Time** | 4.58s | 93.10s |
| **OptiX (GPU) JIT Time** | 0.52s | 0.77s |
| **OptiX (GPU) Warm Time** | 0.02s | 0.31s |
| **Measured Speedup** | **219.68x** | **296.17x** |

The checked-in harness now explicitly models these two scales:

- `smoke`: `max_features=10`
- `medium`: `max_features=250`

and uses deterministic synthetic points (`seed = 20260402`) so future reruns are reproducible.

## Observations

1. **Massive Throughput:** The OptiX backend achieved over **32 million result rows per second** in the medium-scale run, providing nearly a **300x speedup** over the single-threaded Embree reference.
2. **Predictable JIT Overhead:** JIT and pipeline initialization overhead remained stable (~0.5s - 0.7s) regardless of workload scale, making it negligible for large-scale processing.
3. **Scaling:** The system handled over 10 million intersections without stability issues or memory bottlenecks on the 8GB GTX 1070.
4. **Data Handling:** Large ArcGIS JSON pages (100MB+) were successfully loaded and processed, though loading speed is currently limited by Python's JSON parser.

## Verification

- **Parity:** the reported benchmark maintained row-count parity between Embree and OptiX across both scales.
- **Exact-row check:** the benchmark harness now treats `smoke` as an exact-row parity point and `medium` as a row-count parity point to keep the larger run practical.
- **Stability:** No post-success teardown crashes were observed during the Goal 44 execution round.

## Conclusion

The OptiX backend is now validated as a high-performance execution target for bounded synthetic RTDL PIP workloads on the GTX 1070 host. It delivers order-of-magnitude speedups over the Embree baseline while preserving the parity mode stated above. This is a strong GPU baseline, but it is not yet the same as validating OptiX on the real exact-source RayJoin families already exercised on Embree.

## Final Verdict

**Goal 44 Status: ACCEPTED (bounded synthetic benchmark)**
