# Goal1937 - Fixed-Radius Repeat-3 Large-Scale Pod Performance

Status: fixed-radius-repeat3-evidence-collected-release-still-blocked

Date: 2026-05-13

Hardware: `NVIDIA RTX A5000`, driver `570.195.03`

Pod: `root@194.68.245.162 -p 22102`

## Purpose

Claude Goal1936 accepted the Goal1933/1934 performance packet but noted that
the strongest fixed-radius evidence at `524288 x 524288` used `repeat=1`.
Goal1937 reruns that same fixed-radius six-app family at the same scale with
`repeat=3`, visible `[goal1925]` progress lines, and a shell `timeout` wrapper.

Artifact:
`docs/reports/goal1937_fixed_radius_repeat3_pod/fixed_radius_524288_repeat3.json`

Log:
`docs/reports/goal1937_fixed_radius_repeat3_pod/run.log`

## Command Shape

The pod run used the updated Goal1925 harness with large-scale overrides:

```bash
PYTHONPATH=src:. timeout --preserve-status 35m \
python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py \
  --apps facility_knn_assignment,hausdorff_distance,ann_candidate_search,outlier_detection,dbscan_clustering,barnes_hut_force_app \
  --partners cupy,torch \
  --repeat 3 \
  --query-count-override 524288 \
  --search-count-override 524288 \
  --source-commit-label 47490311d15acc668030b20324be05aeb709c4ac \
  --output docs/reports/goal1937_fixed_radius_repeat3/fixed_radius_524288_repeat3.json
```

The pod run records explicit source label
`47490311d15acc668030b20324be05aeb709c4ac`, the local commit that added the
copied-source `--source-commit-label` harness support.

## Results

| App | Partner | v1.8 prepared OptiX median s | v2 prepared partner median s | v2 / v1.8 |
| --- | --- | ---: | ---: | ---: |
| `facility_knn_assignment` | CuPy | 1.553787 | 0.000480 | 0.000309x |
| `facility_knn_assignment` | Torch | 1.348240 | 0.000445 | 0.000330x |
| `hausdorff_distance` | CuPy | 1.383386 | 0.000418 | 0.000302x |
| `hausdorff_distance` | Torch | 1.326599 | 0.000368 | 0.000277x |
| `ann_candidate_search` | CuPy | 1.380058 | 0.000389 | 0.000282x |
| `ann_candidate_search` | Torch | 1.328173 | 0.000350 | 0.000263x |
| `outlier_detection` | CuPy | 1.357974 | 0.000439 | 0.000323x |
| `outlier_detection` | Torch | 1.386685 | 0.000473 | 0.000341x |
| `dbscan_clustering` | CuPy | 1.338143 | 0.000450 | 0.000336x |
| `dbscan_clustering` | Torch | 1.337720 | 0.000436 | 0.000326x |
| `barnes_hut_force_app` | CuPy | 1.373772 | 0.000418 | 0.000304x |
| `barnes_hut_force_app` | Torch | 1.351208 | 0.000415 | 0.000307x |

All 12 rows pass `counts_match` and `summary_match`.

## Interpretation

This resolves the Goal1936 single-repeat caveat for the fixed-radius family:
the same narrow v2 statement remains strongly positive with three samples per
row. The v1.8 prepared OptiX baseline is seconds-scale across all rows, while
the v2 prepared partner path remains sub-millisecond to low-millisecond.

The claim remains narrow. These rows prove the fixed-radius count/threshold
subpath with partner-owned input/output columns. They do not authorize v2.0
release, whole-app speedup wording, broad RT-core speedup wording, arbitrary
PyTorch/CuPy acceleration, true zero-copy claims, or package-install claims.

## External Review Follow-Up

Gemini Goal1938 accepted the first repeat-3 packet with boundary. It confirmed
that Goal1937 resolves the Goal1936 single-repeat caveat and that all 12 rows
support the narrow fixed-radius v2 performance conclusion. Gemini's provenance
caveat about `source_commit_label: unknown` was resolved by rerunning the same
packet with explicit source label `47490311d15acc668030b20324be05aeb709c4ac`.
Gemini also noted that the run log should be accessible; the run log is tracked
in this repository at
`docs/reports/goal1937_fixed_radius_repeat3_pod/run.log`.
