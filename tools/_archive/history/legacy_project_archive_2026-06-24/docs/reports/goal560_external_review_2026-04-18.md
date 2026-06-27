# Goal 560 External Review

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6 (external review pass)
Verdict: **ACCEPT**

## What Was Reviewed

- `docs/reports/goal560_hiprt_backend_perf_compare_2026-04-18.md`
- `docs/reports/goal560_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `scripts/goal560_hiprt_backend_perf_compare.py`
- `tests/goal560_hiprt_backend_perf_compare_test.py`

## Correctness Assessment

### Timing methodology

`time.perf_counter()` wraps the full backend call per repeat. With `repeats=1`, min/median/max are identical — this is structurally correct and the report is transparent about it. The methodology measures end-to-end latency including startup, JIT, geometry build, and dispatch. That is the right scope for a smoke comparison and is disclosed in the `honesty_boundary` field of both the JSON and the markdown report.

### Parity check

Row equality against `rt.run_cpu_python_reference` output is the correctness gate. The JSON records `parity_vs_cpu_reference: true` for all 72 backend/workload pairs and `"pass": 72, "fail": 0`. The script uses Python tuple equality on the returned rows, which is exact — no floating-point tolerance relaxation is hiding anything here.

### Workload count

18 workloads in the JSON match the 18-workload matrix claimed in the report. Each workload entry names the workload string, so the mapping is auditable. No workloads are missing or duplicated.

### Outlier reporting

Vulkan `segment_polygon_hitcount` at 4.94 s is a legitimate outlier. It is not suppressed or down-weighted — it appears exactly in the table and in the JSON. No cherry-picking.

### HIPRT performance gap

HIPRT timings cluster 0.37–0.57 s vs. Embree sub-millisecond on the same small fixtures. The report correctly attributes this to per-call startup/JIT/module/build overhead, not to dispatch throughput. The performance gap is acknowledged rather than excused, and next-work targets (prepared context reuse, multi-repeat larger-fixture tests) are identified.

## Honesty Boundary Assessment

The scope-limiting claims are correctly stated and are the right ones:

- NVIDIA GTX 1070, CUDA/Orochi mode — not AMD GPU validation, no RT cores.
- One repeat, small fixtures — not a throughput benchmark.
- Disallowed claims list (`AMD GPU`, `RT-core acceleration`, `performance-leading`) matches what the evidence cannot support.
- The `honesty_boundary` field is embedded in the JSON output itself, which means it travels with the data file.

No overclaiming was found in the markdown report.

## Script Quality

The script is clean. Backend unavailability is caught as `FileNotFoundError / OSError / NotImplementedError` and reported as `UNAVAILABLE` rather than `FAIL`, which is the correct distinction. All other exceptions report as `FAIL` with error type and message — no silent swallowing. The `lambda runner=runner` closure capture is correct and avoids the late-binding variable capture bug.

## Test Coverage

Two tests: cpu_reference smoke (verifies 18 workloads, all PASS, locally executable without GPU) and unknown-backend rejection. This is appropriate — GPU backend tests cannot run in GPU-absent CI. The test file imports from the script correctly.

## Issues Found

None blocking. Two observations for the record:

1. With `repeats=1`, the median/min/max statistics carry no information beyond the single timing. This is not a bug; it is correctly scoped as a smoke run. A future multi-repeat run should use `repeats >= 3` to expose warm-vs-cold variation.
2. The test suite does not cover the `--repeats 0` rejection path in `main()`, but the guard exists and is correct.

## Summary

The Linux cross-backend parity/performance evidence is technically correct: the methodology is sound, all 72 checks passed exact row parity, timing numbers are consistent with the expected per-call JIT/startup overhead pattern, and no inflated claims are made. The honesty boundary is explicit, accurate, and embedded in the artifact itself. ACCEPT for v0.9 release smoke comparison purposes.
