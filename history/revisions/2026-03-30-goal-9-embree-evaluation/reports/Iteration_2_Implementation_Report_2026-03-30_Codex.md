# Iteration 2 Implementation Report

Date: 2026-03-30
Author: Codex
Round: Goal 9 Embree Baseline Reproduction

## Implemented Scope

Goal 9 implementation adds a dedicated Embree evaluation layer on top of the
frozen baseline:

- a frozen evaluation matrix in code and docs,
- deterministic larger derived dataset cases,
- a full evaluation runner that performs CPU-vs-Embree parity checks before
  timing,
- generated Markdown and CSV summary tables,
- generated SVG figures,
- and a final PDF report generated directly from Python without external
  plotting or document-conversion libraries.

## Main Files

- `/Users/rl2025/rtdl_python_only/src/rtdsl/evaluation_matrix.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/evaluation_report.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/baseline_runner.py`
- `/Users/rl2025/rtdl_python_only/tests/evaluation_test.py`
- `/Users/rl2025/rtdl_python_only/docs/embree_evaluation_matrix.md`

## Generated Artifacts

- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/embree_evaluation.json`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/embree_evaluation_summary.md`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/embree_evaluation_table.csv`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/figures/latency_by_case.svg`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/figures/speedup_by_case.svg`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/figures/scaling_by_workload.svg`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/embree_gap_analysis.md`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/embree_evaluation_report.pdf`

## Observed Results

- 13 evaluation cases were generated.
- All 13 cases passed CPU-vs-Embree parity checks.
- The largest observed Embree speedup was on `ray_synthetic_large`.
- Small authored cases remain slower on Embree than the Python CPU reference,
  which is expected at this scale.

## Verification

- `python3 -m py_compile src/rtdsl/evaluation_matrix.py src/rtdsl/evaluation_report.py`
- `PYTHONPATH=src:. python3 -m unittest tests.evaluation_test tests.baseline_integration_test`
- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`
- `PYTHONPATH=src:. python3 -m rtdsl.evaluation_report --iterations 3 --warmup 1`

## Review Request

Please review the Goal 9 implementation and final artifacts against the
previously agreed criteria:

1. Is the evaluation matrix defensible and complete for the current Embree
   baseline?
2. Are the generated artifacts sufficient to claim Goal 9 complete?
3. Are there any correctness, provenance, reporting, or over-claim issues that
   should block consensus?
4. End with a clear decision on whether Goal 9 is complete.
