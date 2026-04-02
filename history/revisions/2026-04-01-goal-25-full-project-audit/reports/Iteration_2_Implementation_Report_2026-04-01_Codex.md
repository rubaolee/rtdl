# Iteration 2 Implementation Report

## Goal

Respond to Claude's blocked full-project audit, revise the repository accordingly, and prepare a narrowed re-audit snapshot for Claude with Gemini monitoring the closure.

## Revisions Applied

### 1. Section 5.6 reproducibility and publication split

Files:

- `src/rtdsl/section_5_6_scalability.py`
- `Makefile`
- `README.md`
- `docs/reports/section_5_6_scalability_report_2026-03-31.md`
- `docs/reports/section_5_6_scalability_report_2026-03-31.pdf`

Changes:

- The default Section 5.6 CLI path no longer publishes checked-in docs by default.
- Added explicit `--publish-docs` CLI flag.
- Aligned the default smoke probe-series with the module constants (`160,320,480,640,800`).
- Added a named `Makefile` target:
  - `eval-section-5-6-publish-2026-03-31`
- Recorded the exact documented command for the checked-in 2026-03-31 large LSI-only published report.
- Made Section 5.6 interpretation text conditional on selected workloads.
- Corrected the checked-in 2026-03-31 markdown report to state that Figure 14 was not executed in that published run.
- Regenerated the checked-in PDF so the binary artifact matches the corrected report text.

### 2. README/native-performance methodology clarification

Files:

- `README.md`
- `docs/rtdl_feature_guide.md`
- `docs/runtime_overhead_architecture.md`

Changes:

- Clarified that the "native" Goal 15 / Goal 19 baseline uses the same compiled Embree shared library as RTDL.
- Clarified that those comparisons primarily measure Python/ctypes host-path overhead.
- Added the `native_loop` caveat directly to the README low-overhead summary so `segment_polygon_hitcount` and `point_nearest_segment` are not implied to be BVH-backed Embree traversal workloads there.

### 3. Invalid Goal 18 native-gap numbers removed

Files:

- `docs/reports/goal18_low_overhead_runtime_continuation_2026-04-01.md`

Changes:

- Removed the invalid `raw gap vs native lower-bound` and `prepared raw gap vs native lower-bound` claims.
- Replaced them with a methodology note stating that the Goal 15 native numbers remain only historical context and are not directly comparable to the Goal 18 micro-measurement.

### 4. README/layout cleanup

Files:

- `README.md`

Changes:

- Removed the duplicate `docs/vision.md` repository-layout entry.
- Replaced ambiguous "published" wording for the Embree baseline with "checked in to this repository."

### 5. Portable Goal 15 artifact paths

Files:

- `docs/reports/goal15_cpp_embree_comparison_2026-03-31.md`

Changes:

- Replaced machine-specific absolute paths with repo-relative artifact names.

## Verification Run

Executed:

- `PYTHONPATH=src:. python3 -m unittest tests.section_5_6_scalability_test tests.goal19_compare_test`
- `make eval-section-5-6`
- `python3 -m py_compile src/rtdsl/section_5_6_scalability.py`

Additional spot checks:

- confirmed the checked-in 2026-03-31 Section 5.6 report still contains the large-command reproduction note
- confirmed the checked-in report now explicitly says Figure 14 was not executed
- confirmed the default smoke run writes its report under `build/section_5_6_scalability/` with the smoke-note text and does not overwrite the checked-in docs report

## Expected Audit Outcome

Expected closure on Claude findings:

- F1: addressed
- F2: addressed
- F3: addressed
- F4: addressed
- F5: addressed
- F6: addressed
- F7: addressed
- F8: addressed to the level of documentation/labeling honesty; the default path is now explicitly a smoke analogue rather than a published performance claim

## Request to Re-Audit

Claude should now re-audit the revised repository snapshot with emphasis on:

- Section 5.6 reproducibility integrity
- README/native-performance honesty
- Goal 18 report methodology wording
- low-overhead workload boundary wording
- residual documentation contradictions
