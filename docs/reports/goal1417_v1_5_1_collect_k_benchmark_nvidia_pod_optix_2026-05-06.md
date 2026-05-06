# Goal 1417 v1.5.1 COLLECT_K_BOUNDED Benchmark

## Verdict

ACCEPTED for this measured package.

Same-contract COLLECT_K_BOUNDED benchmark evidence only; not a public primitive promotion, not a speedup claim, and not a zero-copy claim.

## Run Scope

- Copies: 1, 16, 64
- Backends requested: python_reference, optix
- Required backends: optix
- Repeats: 5
- Warmups: 1
- Capacity policy: exact capacity equals expected candidate-row count
- Platform: Linux-6.5.0-41-generic-x86_64-with-glibc2.35
- Python: 3.11.10
- Git HEAD: 8b8332dd1c8638ef9f539c5ec0fe4ec62d27a4b2
- Elapsed seconds: 0.817230

## Backend Summary

- python_reference: pass=3, fail=0, skipped=0
- optix: pass=3, fail=0, skipped=0

## Timing Table

- copies=1 left=2 right=3 candidate_rows=2
- copies=1 backend=python_reference status=pass median_sec=0.000185251 min_sec=0.000181839 max_sec=0.000191286
- copies=1 backend=optix status=pass median_sec=0.000730745 min_sec=0.000723287 max_sec=0.000870720
- copies=16 left=32 right=48 candidate_rows=32
- copies=16 backend=python_reference status=pass median_sec=0.002511077 min_sec=0.002499387 max_sec=0.002527773
- copies=16 backend=optix status=pass median_sec=0.001024656 min_sec=0.001011752 max_sec=0.001122385
- copies=64 left=128 right=192 candidate_rows=128
- copies=64 backend=python_reference status=pass median_sec=0.010028064 min_sec=0.010003962 max_sec=0.010153651
- copies=64 backend=optix status=pass median_sec=0.002125360 min_sec=0.002106950 max_sec=0.002226502

## Files

- JSON artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.json`
- Markdown artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.md`
