# Goal 562: External Review — v0.9 Pre-Release Test Gate

Date: 2026-04-18

Reviewer: Claude Sonnet 4.6 (external review pass)

## Verdict

ACCEPT

## Evidence Examined

- `docs/reports/goal562_v0_9_pre_release_test_gate_2026-04-18.md`
- `docs/reports/goal562_hiprt_correctness_matrix_linux_2026-04-18.json`
- `docs/reports/goal562_hiprt_backend_perf_compare_linux_2026-04-18.json`

## Findings

### Test suite

232 tests pass under `PYTHONPATH=src:. python3 -m unittest discover -s tests` on both
macOS (61s) and the Linux backend host (148s). The report correctly notes that
dropping the `-s tests` flag finds zero tests; using the right discovery root is the
correct fix and is not a concern.

### HIPRT correctness matrix

All 18 v0.9 target workloads report `status: PASS` and `parity: true` against the CPU
reference row count. Summary counters (`fail=0`, `not_implemented=0`,
`hiprt_unavailable=0`) match the per-entry data exactly. No discrepancies found.

### Cross-backend smoke matrix

72 entries (18 workloads × 4 backends: hiprt, embree, optix, vulkan) all report
`status: PASS` and `parity_vs_cpu_reference: true`. Summary counters
(`fail=0`, `backend_unavailable=0`) are consistent with per-entry data.

The `repeats=1` single-run timing is weak for performance measurement, but the report
and the JSON's `honesty_boundary` field both state explicitly that these are
startup/JIT-inclusive smoke timings, not throughput or speedup evidence. The large
HIPRT wall-clock values (~0.4–0.6 s on tiny fixtures) are consistent with GPU cold-start
overhead and do not contradict any claim the report makes.

### Scope boundary

The report's "This test gate does not support" list is explicit and complete:
AMD GPU validation, RT-core speedup, performance leadership, production throughput
benchmarking, and standalone final-release authorization are all correctly excluded.
No overclaiming was found anywhere in the three artifacts.

## Conditions

None. The evidence is sufficient and honestly bounded for the stated gate purpose.

## Next Steps

As the report identifies, the remaining gates are the v0.9 documentation audit and the
whole-flow release audit. Those should verify that public docs, candidate release notes,
handoffs, and test artifacts are mutually consistent and do not overclaim.
