# Goal 557 External Review: HIPRT `bfs_discover`

Date: 2026-04-18  
Reviewer: External (Claude Sonnet 4.6)

## Verdict: ACCEPT

## Evidence Verified

**Native implementation exists and is non-trivial.**  
`rtdl_hiprt.cpp` contains `intersectRtdlGraphEdgeBySource` (line 1500), `RtdlBfsExpandKernel` (line 1514), and `rtdl_hiprt_run_bfs_expand` (line 3921). The AABB-list primitive encoding for CSR graph edges and the custom intersection function are present. No CPU fallback path is present inside `run_hiprt` for `bfs_discover`.

**Python dispatch is wired correctly.**  
`hiprt_runtime.py` registers `bfs_discover` as a supported HIPRT predicate (lines 45, 63, 77), implements `bfs_expand_hiprt` (line 1113), and routes through `run_hiprt` at line 1542. Public export through `rtdsl.__init__` is confirmed by presence in the supported-predicate lists.

**Test suite is honest and adequate.**  
`goal557_hiprt_bfs_test.py` tests the direct helper against `bfs_expand_cpu`, the full `run_hiprt` path against `run_cpu_python_reference`, and the `dedupe=False` variant. All HIPRT tests are correctly gated by `@unittest.skipUnless(hiprt_available(), ...)` — no false passes possible on macOS.

**Linux correctness matrix is consistent with claims.**  
`goal557_hiprt_correctness_matrix_linux_2026-04-18.json` shows `bfs_discover` as PASS with `parity: true`, `pass=14`, `not_implemented=4`, `fail=0`, `hiprt_unavailable=0`. The four unimplemented workloads (`triangle_match`, `conjunctive_scan`, `grouped_count`, `grouped_sum`) are correctly reported as `NOT_IMPLEMENTED` with no CPU fallback, matching the honesty boundary stated in the report.

## Honesty Boundary Assessment

The report's honesty boundary is accurate and complete:

- Single device thread per frontier vertex — correctly disclosed, not hidden
- Host-side sort for output determinism — visible in the implementation
- No AMD GPU portability claim — no evidence in either direction; correctly omitted
- No RT-core acceleration claim — kernel is a custom-primitive intersection, not hardware RT; correctly disclosed
- The parity check is against `bfs_expand_cpu`, a real reference, not a stub

No inflation of claims was found. The implementation is correctness-first and bounded exactly as stated.

## Summary

Goal 557 is a clean, bounded HIPRT `bfs_discover` implementation. The native code, Python dispatch, test gating, and correctness matrix are all internally consistent and match the written report. The honesty boundary is accurate. ACCEPT without conditions.
