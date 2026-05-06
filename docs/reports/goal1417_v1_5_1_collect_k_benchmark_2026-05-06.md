# Goal 1417 v1.5.1 COLLECT_K_BOUNDED Benchmark

## Verdict

ACCEPTED for this measured package.

Same-contract COLLECT_K_BOUNDED benchmark evidence only; not a public primitive promotion, not a speedup claim, and not a zero-copy claim.

## Run Scope

- Copies: 1, 16, 64
- Backends requested: python_reference, embree, optix
- Required backends: none
- Repeats: 5
- Warmups: 1
- Capacity policy: exact capacity equals expected candidate-row count
- Platform: Windows-10-10.0.19045-SP0
- Python: 3.11.9
- Git HEAD: 8b8332dd1c8638ef9f539c5ec0fe4ec62d27a4b2
- Elapsed seconds: 0.628795

## Backend Summary

- python_reference: pass=3, fail=0, skipped=0
- embree: pass=3, fail=0, skipped=0
- optix: pass=0, fail=0, skipped=3

## Timing Table

- copies=1 left=2 right=3 candidate_rows=2
- copies=1 backend=python_reference status=pass median_sec=0.000557400 min_sec=0.000553600 max_sec=0.000564200
- copies=1 backend=embree status=pass median_sec=0.000150300 min_sec=0.000138400 max_sec=0.000244900
- copies=1 backend=optix status=skipped FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.
- copies=16 left=32 right=48 candidate_rows=32
- copies=16 backend=python_reference status=pass median_sec=0.008106100 min_sec=0.008084400 max_sec=0.008124900
- copies=16 backend=embree status=pass median_sec=0.002452600 min_sec=0.002430000 max_sec=0.002583700
- copies=16 backend=optix status=skipped FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.
- copies=64 left=128 right=192 candidate_rows=128
- copies=64 backend=python_reference status=pass median_sec=0.032613700 min_sec=0.032603800 max_sec=0.032701700
- copies=64 backend=embree status=pass median_sec=0.031193100 min_sec=0.031104500 max_sec=0.031329900
- copies=64 backend=optix status=skipped FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.

## Files

- JSON artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.json`
- Markdown artifact: `docs/reports/goal1417_v1_5_1_collect_k_benchmark_2026-05-06.md`
