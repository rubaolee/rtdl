# Goal 530: v0.8 Release-Candidate Package

Date: 2026-04-18

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal529 completed the primary Linux post-doc-refresh validation. Goal530 creates
the missing v0.8 release-candidate package under:

- `docs/release_reports/v0_8/`

This package is not a release tag and does not authorize tagging. It records the
bounded v0.8 release-candidate position for final review.

## Files Added

- `docs/release_reports/v0_8/README.md`
- `docs/release_reports/v0_8/release_statement.md`
- `docs/release_reports/v0_8/support_matrix.md`
- `docs/release_reports/v0_8/audit_report.md`
- `docs/release_reports/v0_8/tag_preparation.md`
- `tests/goal530_v0_8_release_candidate_package_test.py`

## Release-Candidate Scope

The v0.8 release-candidate package says:

- current released version remains `v0.7.0` until explicit `v0.8.0` tag
  authorization
- v0.8 is app-building work over the released v0.7.0 surface
- six accepted apps are in scope:
  - Hausdorff distance
  - ANN candidate search
  - outlier detection
  - DBSCAN clustering
  - robot collision screening
  - Barnes-Hut force approximation
- RTDL owns heavy row/candidate/query kernels
- Python owns orchestration, reductions, labels, metrics, and output
- performance claims remain app-specific and bounded by Goal507, Goal509, and
  Goal524
- Goal528 and Goal529 are the current post-doc-refresh macOS/Linux validation
  gates

## Boundaries

The package explicitly does not claim:

- tag authorization
- a new full language redesign
- a full application framework
- full ANN/vector-index support
- FAISS/HNSW/IVF/PQ replacement
- production anomaly-detection or clustering support
- full robotics or continuous collision detection
- full Barnes-Hut/N-body solver support
- general speedups over SciPy, scikit-learn, FAISS, or production systems

## Guard Test

Added:

- `tests/goal530_v0_8_release_candidate_package_test.py`

Validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal530_v0_8_release_candidate_package_test
```

Result:

```text
Ran 4 tests in 0.000s
OK
```

`git diff --check` passed.

## AI Consensus

- Claude review: `docs/reports/goal530_claude_review_2026-04-18.md`, verdict
  `ACCEPT`.
- Gemini Flash review: `docs/reports/goal530_gemini_review_2026-04-18.md`,
  verdict `ACCEPT`.
- Codex consensus: accepted. The v0.8 release-candidate package is accurate,
  bounded, complete enough for final review, and does not authorize tagging.
