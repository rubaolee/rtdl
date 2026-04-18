# Goal 527: Examples And Capability Boundary Refresh

Date: 2026-04-18

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal527 refreshes two user-facing docs that were not fully covered by the
Goal525/Goal526 public-doc pass:

- `examples/README.md`
- `docs/capability_boundaries.md`

The issue was not code correctness. The issue was user-facing precision:
examples and capability docs should tell users exactly where the new v0.8
Stage-1 proximity apps fit, and should not blur a bounded ANN candidate demo
into a full ANN/vector-search claim.

## Changes

### examples/README.md

The v0.8 app boundary now says:

- ANN candidate search has Goal524 bounded Linux RTDL-backend timing
  characterization, but no external ANN-baseline speedup claim.
- Outlier detection has Goal524 bounded Linux RTDL-backend timing
  characterization, but no claim against SciPy, scikit-learn, or production
  anomaly-detection systems.
- DBSCAN has Goal524 bounded Linux RTDL-backend timing characterization, but no
  claim against scikit-learn DBSCAN or production clustering systems.

### docs/capability_boundaries.md

The capability page now says:

- the current v0.8 ANN candidate app is candidate-subset reranking over
  existing `knn_rows(k=1)`, not a full ANN index
- current accepted v0.8 app examples are Hausdorff distance, ANN candidate
  search, outlier detection, DBSCAN clustering, robot collision screening, and
  Barnes-Hut force approximation
- app backend/performance boundaries are recorded in Goal507, Goal509, and
  Goal524
- the ANN candidate app does not contradict the "cannot do full
  high-dimensional ANN/vector-search systems yet" limit

## Guard Test

Added:

- `tests/goal527_examples_capability_boundary_refresh_test.py`

The test verifies:

- `examples/README.md` carries the Goal524 boundary for the three Stage-1
  proximity apps
- `docs/capability_boundaries.md` distinguishes bounded ANN candidate reranking
  from full ANN index/vector-search support
- the capability page lists the current v0.8 app set and points to Goal507,
  Goal509, and Goal524

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal527_examples_capability_boundary_refresh_test \
  tests.goal526_v0_8_public_doc_stale_phrase_test \
  tests.goal525_v0_8_proximity_perf_doc_refresh_test
```

Result:

```text
Ran 5 tests in 0.001s
OK
```

`git diff --check` passed.

## AI Consensus

- Claude review: `docs/reports/goal527_claude_review_2026-04-18.md`, verdict
  `ACCEPT`.
- Gemini Flash review: `docs/reports/goal527_gemini_review_2026-04-18.md`,
  verdict `ACCEPT`.
- Codex consensus: accepted. The examples index and capability-boundary docs now
  correctly bound the Stage-1 proximity apps and avoid overstating ANN, SciPy,
  scikit-learn, FAISS, or production-system support.
