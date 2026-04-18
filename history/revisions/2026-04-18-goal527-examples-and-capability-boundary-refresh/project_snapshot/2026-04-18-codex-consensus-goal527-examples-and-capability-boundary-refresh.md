# Codex Consensus: Goal527 Examples And Capability Boundary Refresh

Date: 2026-04-18

Verdict: ACCEPT

## Reviewed Inputs

- `docs/reports/goal527_examples_and_capability_boundary_refresh_2026-04-18.md`
- `docs/reports/goal527_claude_review_2026-04-18.md`
- `docs/reports/goal527_gemini_review_2026-04-18.md`
- `examples/README.md`
- `docs/capability_boundaries.md`
- `tests/goal527_examples_capability_boundary_refresh_test.py`

## Consensus

Claude and Gemini both accepted Goal527. Codex agrees.

The examples index now carries the Goal524 boundary for ANN candidate search,
outlier detection, and DBSCAN clustering. The capability-boundaries page now
explicitly says the v0.8 ANN candidate app is bounded candidate-subset reranking
over `knn_rows(k=1)`, not a full ANN/vector-index system. It also lists the six
current v0.8 app examples and points to Goal507, Goal509, and Goal524 for
backend/performance boundaries.

No overclaiming was introduced. The docs do not claim external speedups against
SciPy, scikit-learn, FAISS, HNSW/IVF/PQ systems, or production anomaly-detection
and clustering systems.

## Local Validation

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
