# Goal5098 RT-DBSCAN Representative Fixtures

## Status

`completed_representative_synthetic_fixtures`

## Purpose

Goal5095 proved a bounded tiny border/noise case. Goal5098 adds larger synthetic same-input fixtures so RT-DBSCAN correctness and timing can be checked beyond the tiny gate without claiming exact paper dataset provenance.

## Generator

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/generate_representative_fixtures.py
```

The generator writes the fixtures and manifest below.

## Fixtures

| Case | Points | Epsilon | MinPts | Expected signature |
|---|---:|---:|---:|---|
| `representative_medium_two_clusters3d` | 100 | 0.09 | 6 | core=96, sizes=[48,48], noise=4 |
| `representative_border_shell3d` | 60 | 0.085 | 8 | core=54, sizes=[29,29], noise=2 |
| `representative_three_components_noise3d` | 64 | 0.095 | 6 | core=61, sizes=[16,18,27], noise=3 |

Manifest:

```text
Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/representative_fixtures_manifest.json
```

## Boundary

These are synthetic representative fixtures. They are not the exact paper datasets and do not close full RT-DBSCAN paper reproduction.

## Evidence

The local CPU-reference matrix confirms all three fixture signatures:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/representative_partition_matrix_local_cpu_summary.json
```
