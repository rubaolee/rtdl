# Goal 527 External Review

Date: 2026-04-18

Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## What Was Checked

- `examples/README.md` — current v0.8 app example boundary section
- `docs/capability_boundaries.md` — nearest-neighbor, ANN, and "cannot do yet" sections
- `tests/goal527_examples_capability_boundary_refresh_test.py` — guard test assertions

## Findings

### examples/README.md

The three Stage-1 proximity apps (ANN candidate search, outlier detection, DBSCAN
clustering) each carry the correct Goal524 scoping sentence. The phrasing is
specific:

- ANN candidate app: "it is not an external ANN-baseline speedup claim"
- Outlier detection: "it is not a claim against SciPy, scikit-learn, or production
  anomaly detection systems"
- DBSCAN: "it is not a claim against scikit-learn DBSCAN or production clustering
  systems"

No overclaiming. No missing disclaimers.

### docs/capability_boundaries.md

The document correctly distinguishes bounded candidate-subset reranking from full
ANN index support at two independent locations:

1. Nearest-neighbor section (line 59): "This is candidate-subset reranking, not a
   full ANN index."
2. "Cannot do yet" section (lines 192–194): the v0.8 ANN candidate app "does not
   contradict this limit … not FAISS, HNSW, IVF, PQ, or learned/vector-index
   support."

The accepted v0.8 app set is enumerated correctly (Hausdorff distance, ANN candidate
search, outlier detection, DBSCAN clustering, robot collision screening, Barnes-Hut
force approximation). Goal507, Goal509, and Goal524 are cited as the performance
boundary records.

### Guard Test

Both test methods directly assert the key precision substrings. All five tests pass
(reported `OK` in the validation run). The assertions are tight enough to catch
regression if the scoping language is softened or removed.

### No Issues Found

- No ANN speedup claim against external baselines
- No SciPy, scikit-learn, FAISS, or production-system claim
- ANN candidate app is correctly bounded as candidate-subset reranking over existing
  `knn_rows(k=1)`
- `git diff --check` passed (no trailing whitespace or merge markers)
