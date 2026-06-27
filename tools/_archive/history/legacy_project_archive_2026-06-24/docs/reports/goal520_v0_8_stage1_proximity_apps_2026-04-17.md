# Goal 520: v0.8 Stage-1 Proximity Apps

Date: 2026-04-17

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal519 accepted the paper-driven roadmap from arXiv `2603.28771v1` and
identified proximity workloads as the strongest near-term family for RTDL.

Goal520 implements the currently supportable Stage-1 proximity apps using the
existing RTDL language/runtime surface plus Python orchestration:

- ANN candidate search
- outlier detection
- DBSCAN clustering

No RTDL language internals were changed for this goal.

## Implemented Apps

| App | File | RTDL-owned kernel | Python-owned app logic | Boundary |
| --- | --- | --- | --- | --- |
| ANN candidate search | `examples/rtdl_ann_candidate_app.py` | candidate-subset kNN reranking with `knn_rows(k=1)` over a Python-selected candidate subset | candidate-set construction, exact full-set comparison, recall and distance-ratio reporting | not a full ANN index, training system, HNSW/IVF/FAISS replacement, or recall/latency optimizer |
| Outlier detection | `examples/rtdl_outlier_detection_app.py` | `fixed_radius_neighbors` over the point cloud | density counting, thresholding, oracle comparison | not a full anomaly-detection framework or built-in density primitive |
| DBSCAN clustering | `examples/rtdl_dbscan_clustering_app.py` | `fixed_radius_neighbors` over the point cloud | core/border/noise labeling and density-connected cluster expansion | not a full clustering engine or built-in connected-component primitive |

## What Data Becomes What Data

ANN candidate search:

- Input: query points, full search points, and a Python-selected approximate
  candidate subset.
- RTDL output: nearest-neighbor rows from each query to the candidate subset.
- Python output: recall-at-1, mean distance ratio, and per-query comparison
  rows against exact brute-force full-set nearest neighbors.

Outlier detection:

- Input: one point cloud.
- RTDL output: fixed-radius neighbor rows including self-neighbors.
- Python output: per-point density rows and outlier IDs.

DBSCAN clustering:

- Input: one point cloud.
- RTDL output: fixed-radius neighbor rows including self-neighbors.
- Python output: cluster IDs, core flags, neighbor counts, noise IDs, and
  brute-force oracle parity.

## Correctness Evidence

Focused local validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal520_dbscan_clustering_app_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal506_public_entry_v08_alignment_test \
  tests.goal511_feature_guide_v08_refresh_test \
  tests.goal513_public_example_smoke_test \
  tests.goal514_tutorial_example_harness_refresh_test -v
```

Result:

```text
Ran 22 tests in 3.193s
OK
```

Additional checks:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_ann_candidate_app.py \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  tests/goal520_dbscan_clustering_app_test.py

git diff --check
```

Both passed.

## Public Documentation Updates

Updated public-facing docs:

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/release_facing_examples.md`
- `docs/rtdl/itre_app_model.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/v0_8_app_building.md`
- `examples/README.md`

Updated runnable surfaces:

- `examples/rtdl_feature_quickstart_cookbook.py`
- `scripts/goal410_tutorial_example_check.py`

Updated tests:

- `tests/goal505_v0_8_app_suite_test.py`
- `tests/goal506_public_entry_v08_alignment_test.py`
- `tests/goal511_feature_guide_v08_refresh_test.py`
- `tests/goal513_public_example_smoke_test.py`
- `tests/goal514_tutorial_example_harness_refresh_test.py`
- `tests/goal520_dbscan_clustering_app_test.py`

## Honesty Boundary

This goal proves that RTDL + Python can express three paper-driven proximity
apps using existing ITRE kernels:

- `knn_rows`
- `fixed_radius_neighbors`

This goal does **not** claim:

- a full ANN indexing system
- a full anomaly-detection framework
- a full clustering engine
- Linux multi-backend performance closure for these new apps
- that RTDL owns DBSCAN expansion, density scoring, or ANN index construction
  as language primitives

The current claim is app-level expressibility and correctness on portable local
fixtures, with public docs preserving the RTDL/Python boundary.

## AI Consensus

- Claude review: `docs/reports/goal520_claude_review_2026-04-17.md`, verdict
  `APPROVE`.
- Gemini Flash review:
  `docs/reports/goal520_gemini_review_2026-04-17.md`, verdict `ACCEPT`.
- Codex review: accepted. Claude's non-blocking observation is preserved as a
  future-work boundary: the current ANN app demonstrates candidate-subset kNN
  reranking over a static Python-selected candidate set, not dynamic ANN index
  construction.
