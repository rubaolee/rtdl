# Goal 559 External Review: HIPRT DB Workloads

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6 (external review pass)

## Verdict

ACCEPT.

## Evidence Verified

**Native layer** (`src/native/rtdl_hiprt.cpp`):
- `intersectRtdlDbRowAabb` (line 1758): broad-AABB custom primitive, always accepts, correct for single-probe-ray DB scan design.
- `RtdlDbMatchKernel` (line 1821): single-thread kernel traverses geometry, applies conjunctive predicate via `dbRowMatches`/`dbClauseMatches`, writes matched primitive IDs atomically. Device predicate logic covers `eq`, `lt`, `le`, `gt`, `ge`, `between` (ops 1–6) correctly.
- `rtdl_hiprt_run_conjunctive_scan` (line 4719), `rtdl_hiprt_run_grouped_count` (line 4748), `rtdl_hiprt_run_grouped_sum` (line 4779): real C extern entry points with proper null-pointer guards, delegating to `run_db_*` host-side helpers. Not stubs.

**Python layer** (`src/rtdsl/hiprt_runtime.py`):
- `conjunctive_scan_hiprt` (line 1318), `grouped_count_hiprt` (line 1348), `grouped_sum_hiprt` (line 1393): each calls `_hiprt_lib()` via ctypes — no CPU fallback path. Python handles only text encoding and output decoding.

**Test layer** (`tests/goal559_hiprt_db_workloads_test.py`):
- 7 tests covering direct helper equality against CPU reference, `run_hiprt` dispatch equality against CPU reference, and empty-table edge cases for all three workloads.
- All tests guarded by `@unittest.skipUnless(hiprt_available(), ...)` — honest skip rather than silent pass on macOS.

**Correctness matrix** (`docs/reports/goal559_hiprt_correctness_matrix_linux_2026-04-18.json`):
- 18 workloads, all `PASS`, `not_implemented=0`, `fail=0`, `hiprt_unavailable=0`.
- `conjunctive_scan`, `grouped_count`, `grouped_sum` all show `parity: true` with matching row counts against CPU reference.
- Linux timing ~0.6 s per workload is consistent with GPU init overhead on small fixtures, not a correctness concern.

## Honesty Boundary Assessment

The report accurately characterizes the design: broad row AABBs with a single probe ray, device predicate refinement, host-side projection and grouped aggregation. The report does not claim RT-core acceleration, AMD portability, or performance superiority. The single-group-key limitation is documented and enforced in the Python wrappers with a `ValueError`. These are correct and honest constraints.

## Issues Found

None blocking acceptance. One observation: `RtdlDbMatchKernel` is single-threaded (early return for any block/thread other than `(0,0)`), which is intentional for correctness-first design but limits throughput at scale. The report acknowledges this is correctness-first, so this is not a gap in honesty.

## Summary

Goal 559 completes the v0.9 HIPRT workload matrix. All three DB workloads (`conjunctive_scan`, `grouped_count`, `grouped_sum`) have real native HIPRT traversal paths, honest Python wrappers, and validated correctness on Linux HIPRT with GPU hardware. The implementation matches the report's claims. No CPU fallback. No fabricated evidence detected.
