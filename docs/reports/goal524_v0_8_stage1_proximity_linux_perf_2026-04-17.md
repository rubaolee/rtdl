# Goal 524: v0.8 Stage-1 Proximity Linux Performance Characterization

Date: 2026-04-17

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal523 proved that the v0.8 public command surface runs on Linux across
available RTDL backends. Goal524 adds bounded in-process timing for the three
new Stage-1 proximity apps:

- ANN candidate search
- outlier detection
- DBSCAN clustering

This is a characterization gate, not a speedup claim.

## Harness

Script:

- `scripts/goal524_stage1_proximity_perf.py`

Linux command:

```text
PYTHONPATH=src:. python3 scripts/goal524_stage1_proximity_perf.py \
  --copies 128 \
  --repeats 3 \
  --output docs/reports/goal524_linux_stage1_proximity_perf_2026-04-17.json
```

Artifact copied back to this repo:

- `docs/reports/goal524_linux_stage1_proximity_perf_2026-04-17.json`

Summary:

```json
{
  "passed": 15,
  "failed": 0,
  "skipped": 3,
  "total": 18
}
```

Skipped cases:

- `ann_candidate` / `scipy`
- `outlier_detection` / `scipy`
- `dbscan_clustering` / `scipy`

Reason: `ModuleNotFoundError: No module named 'scipy'` on the Linux validation
checkout.

## Results

Median seconds, `copies=128`, `repeats=3`:

| App | Backend | Median seconds | Correctness readout |
| --- | ---: | ---: | --- |
| ANN candidate | CPU Python reference | 0.139026 | recall@1 = 0.666667, exact matches = 256 / 384 |
| ANN candidate | CPU/oracle | 0.083767 | recall@1 = 0.666667, exact matches = 256 / 384 |
| ANN candidate | Embree | 0.089331 | recall@1 = 0.666667, exact matches = 256 / 384 |
| ANN candidate | OptiX | 0.080977 | recall@1 = 0.666667, exact matches = 256 / 384 |
| ANN candidate | Vulkan | 0.085258 | recall@1 = 0.666667, exact matches = 256 / 384 |
| Outlier detection | CPU Python reference | 0.370715 | matches oracle |
| Outlier detection | CPU/oracle | 0.129815 | matches oracle |
| Outlier detection | Embree | 0.129074 | matches oracle |
| Outlier detection | OptiX | 0.127867 | matches oracle |
| Outlier detection | Vulkan | 0.132546 | matches oracle |
| DBSCAN clustering | CPU Python reference | 0.374863 | matches oracle |
| DBSCAN clustering | CPU/oracle | 0.134708 | matches oracle |
| DBSCAN clustering | Embree | 0.133019 | matches oracle |
| DBSCAN clustering | OptiX | 0.132531 | matches oracle |
| DBSCAN clustering | Vulkan | 0.137325 | matches oracle |

## Readout

Correctness:

- all RTDL backends passed
- ANN recall and distance-ratio metrics are stable across backends
- outlier and DBSCAN apps match their brute-force oracle

Performance:

- native CPU/oracle, Embree, OptiX, and Vulkan are broadly similar for these
  bounded fixtures
- OptiX is the fastest median in this run for all three apps, but the margin is
  small
- CPU Python reference is slower for the density apps, as expected, because it
  performs more Python-level pair work before reduction

## Honesty Boundary

This goal does **not** claim:

- RTDL beats mature ANN, anomaly-detection, clustering, SciPy, scikit-learn, or
  FAISS baselines
- these fixture sizes represent production-scale app behavior
- the current ANN app is a full ANN index

SciPy was not installed on the Linux validation checkout, so external SciPy
timing is not included in this artifact. External baseline timing remains a
future gate if the release needs competitive performance claims.

## Verdict

Linux Stage-1 proximity performance characterization: **ACCEPT**.

No correctness or public backend blocker is known from this run. The honest
performance position is: the new apps are correct across RTDL backends on Linux,
with similar backend timings on bounded fixtures and no external-baseline
speedup claim yet.

## AI Consensus

- Claude review: `docs/reports/goal524_claude_review_2026-04-17.md`, verdict
  `ACCEPT`.
- Gemini Flash review:
  `docs/reports/goal524_gemini_review_2026-04-17.md`, final verdict `ACCEPT`
  after a self-correction in the raw review text.
- Codex review: accepted. Claude's non-blocking note is adopted: this
  three-repeat run is adequate for characterization, but a future competitive
  performance gate should use more repeats, stronger host isolation, and
  external baselines.
