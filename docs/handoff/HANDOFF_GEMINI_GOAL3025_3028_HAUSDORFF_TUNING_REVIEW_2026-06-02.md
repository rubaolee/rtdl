# Handoff: Gemini Review For Goal3025-3028 Hausdorff Tuning

Please perform an independent read-only review of the Goal3025 through Goal3028
Hausdorff tuning chain.

## Files To Inspect

- `docs/reports/goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.md`
- `docs/reports/goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.json`
- `tests/goal3025_hausdorff_adaptive_reduced_pod_probe_test.py`
- `docs/reports/goal3026_hausdorff_raw_row_view_probe_2026-06-02.md`
- `docs/reports/goal3026_hausdorff_raw_row_view_probe_2026-06-02.json`
- `tests/goal3026_hausdorff_adaptive_raw_row_view_test.py`
- `tests/goal3026_hausdorff_raw_row_view_probe_test.py`
- `docs/reports/goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.md`
- `docs/reports/goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.json`
- `docs/reports/goal3028_hausdorff_raw_row_view_32768_probe_2026-06-02.json`
- `docs/reports/goal3028_hausdorff_raw_row_view_65536_probe_2026-06-02.json`
- `tests/goal3028_hausdorff_raw_row_view_larger_scale_probe_test.py`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/research/future_version_to_do_list.md`

## Questions To Answer

1. Does Goal3025 correctly record the adaptive-reduced method as correct but
   not promoted because it is slower than both the existing adaptive RT path and
   the dense CuPy grouped-grid reference?
2. Does Goal3026 correctly implement a generic raw row-view surface over the
   existing point-group nearest-witness OptiX ABI without adding native
   Hausdorff-specific engine logic?
3. Does Goal3026 fairly interpret the pod evidence: raw row-view is faster than
   the old warm adaptive RT row path, but still slower than CuPy grouped-grid on
   dense exact 2D Hausdorff?
4. Does Goal3028 fairly extend that interpretation across 8192, 16384, 32768,
   and 65536 points: stable RTDL-vs-RTDL improvement, narrowing but no crossover
   against CuPy?
5. Are the README, language-lab method table, roadmap, future-version to-do
   list, and tests consistent with the claim boundary?
6. Are any public speedup, release, true-zero-copy, broad RT-core, package
   install, or app-specific native-engine claims over-authorized?

## Required Review Output

Write a Markdown review with:

- A line exactly like `Verdict: accept`, `Verdict: accept-with-boundary`,
  `Verdict: needs-more-evidence`, or `Verdict: reject`.
- Findings first, ordered by severity with file references.
- A short summary of what is accepted.
- Any required fixes before this evidence can be used in v2.6 planning.
- An explicit statement that this is an independent Gemini review distinct from
  Codex authoring.

This is not a release review and must not authorize v2.6 release or public
speedup claims.
