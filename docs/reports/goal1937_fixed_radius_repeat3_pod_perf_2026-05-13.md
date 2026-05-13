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
  --output docs/reports/goal1937_fixed_radius_repeat3/fixed_radius_524288_repeat3.json
```

The remote checkout did not have usable `.git` metadata, so the JSON artifact
records `source_commit_label: unknown`. The harness script copied to the pod is
the local Goal1925 harness after the large-scale override support landed.

## Results

| App | Partner | v1.8 prepared OptiX median s | v2 prepared partner median s | v2 / v1.8 |
| --- | --- | ---: | ---: | ---: |
| `facility_knn_assignment` | CuPy | 1.365337 | 0.000440 | 0.000323x |
| `facility_knn_assignment` | Torch | 1.423761 | 0.000452 | 0.000318x |
| `hausdorff_distance` | CuPy | 1.337785 | 0.000397 | 0.000297x |
| `hausdorff_distance` | Torch | 1.352306 | 0.000361 | 0.000267x |
| `ann_candidate_search` | CuPy | 1.380117 | 0.000397 | 0.000288x |
| `ann_candidate_search` | Torch | 1.343490 | 0.000336 | 0.000250x |
| `outlier_detection` | CuPy | 1.353595 | 0.000443 | 0.000327x |
| `outlier_detection` | Torch | 1.392411 | 0.000415 | 0.000298x |
| `dbscan_clustering` | CuPy | 1.319673 | 0.000455 | 0.000345x |
| `dbscan_clustering` | Torch | 1.315482 | 0.000418 | 0.000318x |
| `barnes_hut_force_app` | CuPy | 1.398777 | 0.000423 | 0.000302x |
| `barnes_hut_force_app` | Torch | 1.369663 | 0.000397 | 0.000290x |

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
