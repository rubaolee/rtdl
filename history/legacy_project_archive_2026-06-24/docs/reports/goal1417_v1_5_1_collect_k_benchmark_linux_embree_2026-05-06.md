# Goal 1417 v1.5.1 COLLECT_K_BOUNDED Benchmark

## Verdict

ACCEPTED for this measured package.

Same-contract COLLECT_K_BOUNDED benchmark evidence only; not a public primitive promotion, not a speedup claim, and not a zero-copy claim.

## Run Scope

- Copies: 1, 16, 64
- Backends requested: python_reference, embree
- Required backends: embree
- Repeats: 5
- Warmups: 1
- Capacity policy: exact capacity equals expected candidate-row count
- Platform: Linux-6.17.0-20-generic-x86_64-with-glibc2.39
- Python: 3.12.3
- Git HEAD: 8b8332dd1c8638ef9f539c5ec0fe4ec62d27a4b2
- Elapsed seconds: 0.164172

## Backend Summary

- python_reference: pass=3, fail=0, skipped=0
- embree: pass=3, fail=0, skipped=0

## Timing Table

- copies=1 left=2 right=3 candidate_rows=2
- copies=1 backend=python_reference status=pass median_sec=0.000171364 min_sec=0.000169444 max_sec=0.000235815
- copies=1 backend=embree status=pass median_sec=0.000051770 min_sec=0.000049199 max_sec=0.000106225
- copies=16 left=32 right=48 candidate_rows=32
- copies=16 backend=python_reference status=pass median_sec=0.002482771 min_sec=0.002451640 max_sec=0.002595272
- copies=16 backend=embree status=pass median_sec=0.000823825 min_sec=0.000821823 max_sec=0.000859277
- copies=64 left=128 right=192 candidate_rows=128
- copies=64 backend=python_reference status=pass median_sec=0.009666137 min_sec=0.009653740 max_sec=0.009742222
- copies=64 backend=embree status=pass median_sec=0.009634878 min_sec=0.009574911 max_sec=0.009835146

## Files

- JSON artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.json`
- Markdown artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.md`
