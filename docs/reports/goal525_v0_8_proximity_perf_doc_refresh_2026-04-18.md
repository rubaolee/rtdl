# Goal 525: v0.8 Proximity Performance Documentation Refresh

Date: 2026-04-18

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal524 added Linux performance characterization for the three Goal519 Stage-1
proximity apps:

- ANN candidate search
- outlier detection
- DBSCAN clustering

Goal525 refreshes public documentation so users no longer see stale language
claiming that those apps lack Linux performance closure.

## Files Updated

- `README.md`
- `docs/README.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/v0_8_app_building.md`
- `docs/current_architecture.md`
- `tests/goal525_v0_8_proximity_perf_doc_refresh_test.py`

## Documentation Changes

The refreshed docs now state:

- Goal524 exists and covers the three Stage-1 proximity apps.
- Linux timing characterization covers RTDL CPU/oracle, Embree, OptiX, and
  Vulkan for those apps.
- ANN candidate search preserves stable recall and distance-ratio metrics
  across RTDL backends in the measured fixture.
- Outlier detection and DBSCAN match the brute-force oracle in the measured
  fixture.
- The result is a bounded RTDL-backend characterization, not an external
  speedup claim.
- SciPy was not installed in the Goal524 Linux validation checkout, so no SciPy
  timing is included for those three apps.
- No claim is made against SciPy, scikit-learn, FAISS, HNSW/IVF-style ANN
  indexes, or production anomaly-detection/clustering systems.

## Guard Test

Added:

- `tests/goal525_v0_8_proximity_perf_doc_refresh_test.py`

The test checks that the public docs:

- reference Goal524
- mention ANN candidate search, outlier detection, and DBSCAN
- preserve the SciPy-not-installed boundary
- preserve the no-external-baseline-speedup boundary
- no longer contain the stale phrase
  `do not yet have Linux performance closure`

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal525_v0_8_proximity_perf_doc_refresh_test \
  tests.goal511_feature_guide_v08_refresh_test
```

Result:

```text
Ran 5 tests in 0.001s
OK
```

## Release Readout

Goal525 is documentation-only plus a regression test. It does not add new
performance claims beyond Goal524. It fixes release-facing freshness by making
the public docs consistent with the current v0.8 evidence trail.

## AI Consensus

- Claude review: `docs/reports/goal525_claude_review_2026-04-18.md`, verdict
  `ACCEPT`.
- Gemini Flash review: `docs/reports/goal525_gemini_review_2026-04-18.md`,
  verdict `ACCEPT`.
- Codex consensus: accepted. The public docs now match Goal524 and preserve the
  no-external-baseline-speedup boundary.
